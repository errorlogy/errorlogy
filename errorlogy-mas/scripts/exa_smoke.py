#!/usr/bin/env python3
"""Smoke check for Exa configuration (no API key printed)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def _flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def main() -> int:
    key = os.environ.get("EXA_API_KEY", "").strip()
    configured = bool(key)
    print(f"EXA_API_KEY: {'set' if configured else 'not set'}")
    print(f"EXA_SEARCH_TYPE: {os.environ.get('EXA_SEARCH_TYPE', 'auto')}")
    print(f"EXA_AGENT_MODE: {_flag('EXA_AGENT_MODE')}")
    print(f"EXA_AGENT_EFFORT: {os.environ.get('EXA_AGENT_EFFORT', 'minimal')}")
    print(f"EXA_PREFERRED: {_flag('EXA_PREFERRED')}")

    try:
        from exa_py import Exa  # noqa: F401
    except ImportError:
        print("exa-py not installed — run: pip install exa-py>=2.14.0")
        return 1

    print("exa-py: installed")

    if not configured:
        print("Skip live call — set EXA_API_KEY in .env to test search.")
        return 0

    from exa_py import Exa

    exa = Exa(api_key=key)
    response = exa.search(
        "UK parliamentary inquiry regulatory failure governance report",
        type=os.environ.get("EXA_SEARCH_TYPE", "auto"),
        num_results=2,
        contents={"highlights": True},
    )
    results = getattr(response, "results", []) or []
    print(f"live_search_hits: {len(results)}")
    for result in results[:2]:
        title = (getattr(result, "title", None) or "")[:80]
        url = (getattr(result, "url", None) or "")[:60]
        print(f"  - {title} ({url})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
