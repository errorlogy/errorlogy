"""Zvec KB demo: vector search, FTS index, and hybrid query.

Run from repo root:
  python examples/zvec_kb_demo.py

Optional env:
  KB_EMBEDDINGS=hash|fastembed|sentence-transformers
  KB_EMBEDDING_MODEL=<model id>
  KB_EMBEDDING_DIM=128            # hash only

Requires: pip install zvec>=0.5.0 (already listed in requirements.txt)
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _load_zvec_store():
    """Load KB module without importing full MAS (keeps demo lightweight)."""
    module_path = os.path.join(_ROOT, "mas", "kb", "zvec_store.py")
    spec = importlib.util.spec_from_file_location("errorlogy_zvec_store", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {module_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


_zvec = _load_zvec_store()
ZvecStore = _zvec.ZvecStore
build_embedder_from_env = _zvec.build_embedder_from_env


def _print_hits(label: str, hits) -> None:
    print(f"\n{label} ({len(hits)} hits)")
    if not hits:
        print("  (no results)")
        return
    for i, hit in enumerate(hits, start=1):
        text = (hit.text or "").replace("\n", " ").strip()
        parts = [f"id={hit.id}", f"score={hit.score:.4f}"]
        if hit.vector_score is not None:
            parts.append(f"vector={hit.vector_score:.4f}")
        if hit.fts_score is not None:
            parts.append(f"fts={hit.fts_score:.4f}")
        print(f"  {i}. {' '.join(parts)}")
        print(f"     {text}")


def main() -> None:
    data_path = ".data/zvec_kb_demo"
    if os.path.isdir(data_path):
        shutil.rmtree(data_path)

    embedder = build_embedder_from_env()
    print(f"Embedder: {type(embedder).__name__} (dim={embedder.dim})")

    store = ZvecStore(
        path=data_path,
        collection_name="errorlogy_demo_kb",
        embedder=embedder,
        hybrid_weights=(0.5, 0.5),
    )

    docs = [
        ("d1", "Public procurement delays due to unclear requirements and frequent scope changes."),
        ("d2", "Budget planning missed inflation assumptions; procurement costs increased unexpectedly."),
        ("d3", "Citizen feedback indicates long queues and poor service reliability at local offices."),
        ("d4", "Audit notes weak internal controls and incomplete documentation for approvals."),
        ("d5", "IT rollout suffered from vendor lock-in and insufficient staff training."),
    ]
    inserted = store.add_texts(docs)
    print(f"Inserted {inserted} docs into zvec collection at {store.path!r}")

    fts_ok = store.ensure_fts_index()
    vec_idx_ok = store.ensure_vector_index()
    print(f"FTS index ready: {fts_ok}")
    print(f"Vector index ready: {vec_idx_ok}")

    query = "procurement cost increase weak controls"
    print(f"\nQuery: {query!r}")

    _print_hits("Vector-only", store.query(query, topk=3, mode="vector"))
    if fts_ok:
        _print_hits("FTS-only", store.query(query, topk=3, mode="fts"))
        _print_hits("Hybrid (FTS + vector)", store.query(query, topk=3, mode="hybrid"))
    else:
        print("\nFTS unavailable — hybrid falls back to vector-only.")
        _print_hits("Auto (fallback vector)", store.query(query, topk=3, mode="auto"))


if __name__ == "__main__":
    main()
