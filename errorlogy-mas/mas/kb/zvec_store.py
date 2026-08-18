from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import Iterable, Literal, Protocol

import numpy as np

QueryMode = Literal["auto", "vector", "fts", "hybrid"]

_FTS_STOPWORDS = frozenset(
    {"a", "an", "and", "or", "the", "in", "on", "at", "to", "for", "of", "with"}
)


def _normalize_fts_query(text: str) -> str:
    """Drop common stopwords so FTS queries behave more like natural language."""
    tokens: list[str] = []
    for tok in (text or "").lower().split():
        cleaned = tok.strip(".,;:!?\"'()[]")
        if cleaned and cleaned not in _FTS_STOPWORDS:
            tokens.append(cleaned)
    return " ".join(tokens)


class Embedder(Protocol):
    def embed(self, text: str) -> list[float]:
        """Return a fixed-dimension fp32 vector for text."""

    @property
    def dim(self) -> int: ...


@dataclass(frozen=True)
class HashingEmbedder:
    """Tiny, deterministic embedder (no external models / API keys).

    Not semantically meaningful, but good enough for a runnable demo.
    """

    dim: int = 128

    def embed(self, text: str) -> list[float]:
        text = text or ""
        vec = np.zeros((self.dim,), dtype=np.float32)
        if not text.strip():
            return vec.tolist()

        # Token hashing into buckets, with signed accumulation.
        for tok in text.lower().split():
            h = hashlib.blake2b(tok.encode("utf-8"), digest_size=16).digest()
            idx = int.from_bytes(h[:4], "little") % self.dim
            sign = -1.0 if (h[4] & 1) else 1.0
            weight = 1.0 + (h[5] / 255.0)
            vec[idx] += sign * weight

        # Normalize to unit length (cosine-friendly).
        n = float(np.linalg.norm(vec))
        if n > 0:
            vec /= n
        return vec.tolist()


@dataclass
class SentenceTransformerEmbedder:
    """Optional real embeddings via existing `sentence-transformers` dependency."""

    model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"
    _model: object | None = field(default=None, init=False, repr=False)
    _dim: int | None = field(default=None, init=False, repr=False)

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
            self._dim = int(self._model.get_sentence_embedding_dimension())
        return self._model

    @property
    def dim(self) -> int:
        if self._dim is None:
            self._load_model()
        return int(self._dim or 0)

    def embed(self, text: str) -> list[float]:
        model = self._load_model()
        vec = model.encode(text or "", normalize_embeddings=True)
        return np.asarray(vec, dtype=np.float32).tolist()


@dataclass
class FastEmbedEmbedder:
    """Optional lightweight embeddings when `fastembed` is installed."""

    model_name: str = "BAAI/bge-small-en-v1.5"
    _model: object | None = field(default=None, init=False, repr=False)
    _dim: int | None = field(default=None, init=False, repr=False)

    def _load_model(self):
        if self._model is None:
            from fastembed import TextEmbedding

            self._model = TextEmbedding(model_name=self.model_name)
            probe = next(self._model.embed("probe"))
            self._dim = len(probe)
        return self._model

    @property
    def dim(self) -> int:
        if self._dim is None:
            self._load_model()
        return int(self._dim or 0)

    def embed(self, text: str) -> list[float]:
        model = self._load_model()
        vec = next(model.embed(text or ""))
        arr = np.asarray(vec, dtype=np.float32)
        n = float(np.linalg.norm(arr))
        if n > 0:
            arr /= n
        return arr.tolist()


def build_embedder_from_env() -> Embedder:
    """Select embedder from env vars with safe fallbacks.

    Env:
      KB_EMBEDDINGS=hash|fastembed|sentence-transformers|st
      KB_EMBEDDING_MODEL=<model id>  (optional)
      KB_EMBEDDING_DIM=<int>         (hash only, default 128)
    """
    mode = os.getenv("KB_EMBEDDINGS", "hash").strip().lower()
    model = os.getenv("KB_EMBEDDING_MODEL", "").strip()

    if mode in ("hash", "hashing", ""):
        dim = int(os.getenv("KB_EMBEDDING_DIM", "128"))
        return HashingEmbedder(dim=dim)

    if mode in ("st", "sentence-transformers", "sentence_transformers", "sbert"):
        try:
            return SentenceTransformerEmbedder(
                model_name=model or "paraphrase-multilingual-MiniLM-L12-v2"
            )
        except ImportError:
            return HashingEmbedder(dim=int(os.getenv("KB_EMBEDDING_DIM", "128")))

    if mode == "fastembed":
        try:
            return FastEmbedEmbedder(model_name=model or "BAAI/bge-small-en-v1.5")
        except ImportError:
            return HashingEmbedder(dim=int(os.getenv("KB_EMBEDDING_DIM", "128")))

    return HashingEmbedder(dim=int(os.getenv("KB_EMBEDDING_DIM", "128")))


@dataclass
class ZvecHit:
    id: str
    score: float
    text: str | None = None
    vector_score: float | None = None
    fts_score: float | None = None


class ZvecStore:
    """Minimal Zvec-backed store with optional FTS + hybrid query."""

    def __init__(
        self,
        *,
        path: str,
        collection_name: str = "kb",
        text_field: str = "text",
        vector_field: str = "embedding",
        embedder: Embedder | None = None,
        hybrid_weights: tuple[float, float] = (0.5, 0.5),
    ) -> None:
        self.path = path
        self.collection_name = collection_name
        self.text_field = text_field
        self.vector_field = vector_field
        self.embedder: Embedder = embedder or build_embedder_from_env()
        self.hybrid_weights = hybrid_weights

        self._collection = None
        self._fts_index_ready = False
        self._vector_index_ready = False

    def open(self):
        import zvec

        parent = os.path.dirname(os.path.abspath(self.path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        schema = zvec.CollectionSchema(
            name=self.collection_name,
            fields=[
                zvec.FieldSchema(self.text_field, zvec.DataType.STRING, nullable=False),
            ],
            vectors=zvec.VectorSchema(
                self.vector_field,
                zvec.DataType.VECTOR_FP32,
                self.embedder.dim,
            ),
        )
        if os.path.isdir(self.path):
            try:
                if not os.listdir(self.path):
                    os.rmdir(self.path)
            except Exception:
                pass

        if os.path.exists(self.path):
            self._collection = zvec.open(path=self.path)
        else:
            self._collection = zvec.create_and_open(path=self.path, schema=schema)

        self._fts_index_ready = self._schema_has_fts()
        self._vector_index_ready = self._schema_has_vector_index()
        return self._collection

    @property
    def collection(self):
        if self._collection is None:
            return self.open()
        return self._collection

    @property
    def fts_enabled(self) -> bool:
        return self._fts_index_ready

    @property
    def vector_index_enabled(self) -> bool:
        return self._vector_index_ready

    def _schema_has_fts(self) -> bool:
        try:
            field_schema = self.collection.schema.field(self.text_field)
            param = getattr(field_schema, "index_param", None)
            return param is not None and type(param).__name__ == "FtsIndexParam"
        except Exception:
            return False

    def _schema_has_vector_index(self) -> bool:
        try:
            vector_schema = self.collection.schema.vector(self.vector_field)
            param = getattr(vector_schema, "index_param", None)
            if param is None:
                return False
            return type(param).__name__ in {"HnswIndexParam", "FlatIndexParam", "IVFIndexParam"}
        except Exception:
            return False

    def ensure_fts_index(self) -> bool:
        """Create an FTS index on the text field if missing."""
        if self._fts_index_ready or self._schema_has_fts():
            self._fts_index_ready = True
            return True

        import zvec

        try:
            self.collection.create_index(self.text_field, zvec.FtsIndexParam())
            self._fts_index_ready = True
            return True
        except Exception:
            self._fts_index_ready = False
            return False

    def ensure_vector_index(self) -> bool:
        """Create an HNSW index on the vector field if missing."""
        if self._vector_index_ready or self._schema_has_vector_index():
            self._vector_index_ready = True
            return True

        import zvec

        try:
            self.collection.create_index(self.vector_field, zvec.HnswIndexParam())
            self._vector_index_ready = True
            return True
        except Exception:
            self._vector_index_ready = False
            return False

    def add_texts(self, items: Iterable[tuple[str, str]]) -> int:
        import zvec

        docs: list = []
        for doc_id, text in items:
            vec = self.embedder.embed(text)
            docs.append(
                zvec.Doc(
                    id=str(doc_id),
                    fields={self.text_field: text},
                    vectors={self.vector_field: vec},
                )
            )
        if not docs:
            return 0
        self.collection.insert(docs)
        try:
            self.collection.flush()
        except Exception:
            # flush() availability may vary across versions; inserts are still valid.
            pass
        return len(docs)

    def query(
        self,
        query_text: str,
        *,
        topk: int = 5,
        mode: QueryMode = "auto",
    ) -> list[ZvecHit]:
        if mode == "vector":
            return self._query_vector(query_text, topk=topk)
        if mode == "fts":
            if not self.ensure_fts_index():
                return []
            return self._query_fts(query_text, topk=topk)
        if mode == "hybrid":
            if not self.ensure_fts_index():
                return self._query_vector(query_text, topk=topk)
            return self._query_hybrid(query_text, topk=topk)

        # auto: hybrid when FTS is available, otherwise vector-only fallback.
        if self.ensure_fts_index():
            return self._query_hybrid(query_text, topk=topk)
        return self._query_vector(query_text, topk=topk)

    def _parse_doc(self, result) -> ZvecHit:
        if hasattr(result, "id") and hasattr(result, "score"):
            rid = str(getattr(result, "id", ""))
            score = float(getattr(result, "score", 0.0))
            fields = getattr(result, "fields", None) or {}
            text = fields.get(self.text_field)
        else:
            rid = str(result.get("id", ""))
            score = float(result.get("score", 0.0))
            fields = result.get("fields") or {}
            text = fields.get(self.text_field)
        return ZvecHit(id=rid, score=score, text=text)

    def _query_vector(self, query_text: str, *, topk: int) -> list[ZvecHit]:
        import zvec

        qvec = self.embedder.embed(query_text)
        results = self.collection.query(
            queries=zvec.Query(self.vector_field, vector=qvec),
            topk=int(topk),
            output_fields=[self.text_field],
        )
        hits: list[ZvecHit] = []
        for result in results or []:
            hit = self._parse_doc(result)
            hit.vector_score = hit.score
            hits.append(hit)
        return hits

    def _fts_query(self, query_text: str):
        import zvec

        normalized = _normalize_fts_query(query_text) or (query_text or "").strip()
        return zvec.Query(self.text_field, fts=zvec.Fts(normalized))

    def _query_fts(self, query_text: str, *, topk: int) -> list[ZvecHit]:
        results = self.collection.query(
            queries=self._fts_query(query_text),
            topk=int(topk),
            output_fields=[self.text_field],
        )
        hits: list[ZvecHit] = []
        for result in results or []:
            hit = self._parse_doc(result)
            hit.fts_score = hit.score
            hits.append(hit)
        return hits

    def _query_hybrid(self, query_text: str, *, topk: int) -> list[ZvecHit]:
        import zvec

        fetch_k = max(int(topk) * 3, int(topk))
        vector_by_id = {h.id: h for h in self._query_vector(query_text, topk=fetch_k)}
        fts_by_id = {h.id: h for h in self._query_fts(query_text, topk=fetch_k)}

        qvec = self.embedder.embed(query_text)
        vector_query = zvec.Query(self.vector_field, vector=qvec)
        fts_query = self._fts_query(query_text)
        results = self.collection.query(
            queries=[vector_query, fts_query],
            topk=int(topk),
            output_fields=[self.text_field],
            reranker=zvec.WeightedReRanker(list(self.hybrid_weights)),
        )

        hits: list[ZvecHit] = []
        for result in results or []:
            hit = self._parse_doc(result)
            vector_hit = vector_by_id.get(hit.id)
            fts_hit = fts_by_id.get(hit.id)
            hit.vector_score = vector_hit.vector_score if vector_hit else None
            hit.fts_score = fts_hit.fts_score if fts_hit else None
            hits.append(hit)
        return hits

    def schema_summary(self) -> str:
        try:
            return json.dumps(json.loads(str(self.collection.schema)), indent=2)
        except Exception:
            return str(self.collection.schema)
