"""Knowledge-base backends (optional)."""

from mas.kb.zvec_store import (
    HashingEmbedder,
    ZvecHit,
    ZvecStore,
    build_embedder_from_env,
)

__all__ = [
    "HashingEmbedder",
    "ZvecHit",
    "ZvecStore",
    "build_embedder_from_env",
]
