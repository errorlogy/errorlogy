"""Load YAML seed packs for eval harness."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

EVALS_DIR = Path(__file__).parent
SEEDS_DIR = EVALS_DIR / "seeds"

EVAL_LIVE = os.environ.get("EVAL_LIVE") == "1"


def load_seed_pack(filename: str) -> list[dict]:
    path = SEEDS_DIR / filename
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data.get("cases", [])
