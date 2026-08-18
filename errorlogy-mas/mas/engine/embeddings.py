"""Optional multilingual sentence embeddings for fuzzy mode matching."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    pass

_MODEL = None
_MODE_VECTORS: dict[str, np.ndarray] = {}
_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def use_embeddings() -> bool:
    return os.getenv("ERRORLOGY_USE_EMBEDDINGS", "1").strip() not in ("0", "false", "no")


def is_available() -> bool:
    if not use_embeddings():
        return False
    try:
        import sentence_transformers  # noqa: F401
        return True
    except ImportError:
        return False


def _get_model():
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer(_MODEL_NAME)
    return _MODEL


def _mode_text(mode: dict) -> str:
    parts = [
        mode.get("name", ""),
        mode.get("operational_signal") or "",
        mode.get("government_decision_cue") or "",
        mode.get("definition") or "",
    ]
    return " ".join(p for p in parts if p).strip()


def _embed(text: str) -> np.ndarray | None:
    if not text.strip() or not is_available():
        return None
    try:
        model = _get_model()
        vec = model.encode(text, normalize_embeddings=True)
        return np.asarray(vec, dtype=np.float32)
    except Exception:
        return None


def mode_vector(mode_id: str, mode: dict) -> np.ndarray | None:
    if mode_id in _MODE_VECTORS:
        return _MODE_VECTORS[mode_id]
    vec = _embed(_mode_text(mode))
    if vec is not None:
        _MODE_VECTORS[mode_id] = vec
    return vec


def precompute_modes(modes: list[dict]) -> int:
    """Batch-encode atomic modes at taxonomy load. Returns count encoded."""
    if not is_available() or not modes:
        return 0
    try:
        model = _get_model()
        ids: list[str] = []
        texts: list[str] = []
        for m in modes:
            mid = m.get("id", "")
            if not mid or mid in _MODE_VECTORS:
                continue
            text = _mode_text(m)
            if not text.strip():
                continue
            ids.append(mid)
            texts.append(text)
        if not texts:
            return 0
        vectors = model.encode(texts, normalize_embeddings=True, batch_size=64, show_progress_bar=False)
        for mid, vec in zip(ids, vectors):
            _MODE_VECTORS[mid] = np.asarray(vec, dtype=np.float32)
        return len(ids)
    except Exception:
        return 0


def semantic_similarity(mode: dict, case_text: str) -> float | None:
    """Cosine similarity between case text and mode operational signal. None if unavailable."""
    mode_id = mode.get("id", "")
    if not mode_id:
        return None
    mvec = mode_vector(mode_id, mode)
    cvec = _embed(case_text[:8000])
    if mvec is None or cvec is None:
        return None
    return float(np.clip(np.dot(mvec, cvec), 0.0, 1.0))
