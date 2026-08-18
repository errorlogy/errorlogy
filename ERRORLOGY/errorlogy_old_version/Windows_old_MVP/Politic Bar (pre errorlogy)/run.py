"""CLI entry point for the politic.bar pipeline.

Usage:
    export ANTHROPIC_API_KEY=sk-...
    python run.py <case_id> <path_to_source_bundle.txt>

The source bundle is a single text file containing the raw material about
the decision-event: primary source excerpts, URLs with fetched content,
transcripts, official releases. The pipeline treats it as the authoritative
evidence set for this run.

Pre-analyzed seed cases live in cases/ and do not require a model key to
view in the dashboard — they were produced by the methodology applied by
hand; see methodology/seed_notes.md for how.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from politic_bar.pipeline import run_pipeline


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python run.py <case_id> <source_bundle.txt>", file=sys.stderr)
        return 2
    case_id, bundle_path = sys.argv[1], Path(sys.argv[2])
    if not bundle_path.exists():
        print(f"Source bundle not found: {bundle_path}", file=sys.stderr)
        return 2

    bundle = bundle_path.read_text(encoding="utf-8")
    card = run_pipeline(case_id, bundle)
    if card is None:
        print(f"Pipeline halted for case {case_id} — see cases/{case_id}/_pipeline/")
        return 1
    print(json.dumps(card.to_dict(), indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
