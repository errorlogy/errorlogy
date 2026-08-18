"""Configuration for the analytics microservice."""

import os
from pathlib import Path

# Project root is two levels up from src/analytics/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

TAXONOMY_PATH = PROJECT_ROOT / "errorlogy_unified_taxonomy_v16_max_catastrophe_2.json"

ANALYTICS_HOST = os.getenv("ANALYTICS_HOST", "127.0.0.1")
ANALYTICS_PORT = int(os.getenv("ANALYTICS_PORT", "8000"))

# Comma-separated list; empty => allow all origins without credentials (browser-safe default).
def cors_allow_origins() -> list[str] | None:
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if not raw:
        return None
    return [o.strip() for o in raw.split(",") if o.strip()]
