#!/usr/bin/env python3
"""Print OSS funnel checklist from research/oss-candidates.yaml (no network)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
TRACKER = ROOT / "research" / "oss-candidates.yaml"

SCORE_KEYS = (
    "coupling",
    "duplication",
    "test_safety",
    "blast_radius",
    "license",
    "maintenance",
    "engine_llm_fit",
    "old_sketch_risk",
)

STAGE_CHECKLIST = {
    "discover": [
        "Entry in oss-candidates.yaml with repo_url and target_area",
        "Check ACTIVE / RESEARCH / OLD SKETCH boundaries (AGENTS.md)",
        "Mark example: true if decision not made",
    ],
    "screen": [
        "Fill all score axes (1–5)",
        "Check veto: LLM numbers, OLD SKETCH merge, GUI license",
        f"weighted total >= screen_threshold → spike",
    ],
    "spike": [
        "Branch spike/<name>, POC outside main",
        "For mas/engine — engine_only smoke required",
        "Notes in notes_en",
    ],
    "pilot": [
        "Narrow PR, CI: pytest + challenger --engine-only + gui build",
        "Without weakening LANGUAGE_RULES / μ guards",
    ],
    "adopt": ["decision: adopt, update docs if needed"],
    "reject": ["decision: reject, reason in notes_en"],
    "defer": ["decision: defer, review_after: YYYY-QN"],
}


def weighted_total(score: dict, weights: dict) -> float:
    num = 0.0
    den = 0.0
    for key in SCORE_KEYS:
        if key not in score or score[key] is None:
            continue
        w = float(weights.get(key, 1.0))
        num += w * float(score[key])
        den += w
    return round(num / den, 2) if den else 0.0


def veto_flags(candidate: dict) -> list[str]:
    flags: list[str] = []
    notes = (candidate.get("notes_en") or "").lower()
    area = candidate.get("target_area", "")
    if candidate.get("score", {}).get("engine_llm_fit", 5) <= 2:
        flags.append("engine_llm_fit <= 2 — LLM-in-numbers risk")
    if candidate.get("score", {}).get("old_sketch_risk", 5) <= 2:
        flags.append("old_sketch_risk <= 2 — OLD SKETCH contamination risk")
    if "old sketch" in notes and "migration" not in notes:
        flags.append("notes mention OLD SKETCH without migration task")
    if area == "mas" and "replace orchestrator" in notes:
        flags.append("orchestrator replacement — typical anti-pattern")
    return flags


def print_candidate(c: dict, weights: dict, threshold: float) -> None:
    score = c.get("score") or {}
    total = score.get("total")
    if total is None:
        total = weighted_total(score, weights)

    print(f"\n{'=' * 60}")
    print(f"ID:     {c.get('id')}")
    print(f"Name:   {c.get('name')}")
    print(f"Stage:  {c.get('stage')}  |  Area: {c.get('target_area')}  |  Decision: {c.get('decision')}")
    if c.get("example"):
        print("NOTE:   example entry — not a decided integration")
    print(f"Score:  {total} / 5.0  (threshold for spike: {threshold})")

    print("\nAxes:")
    for key in SCORE_KEYS:
        val = score.get(key, "—")
        w = weights.get(key, 1.0)
        print(f"  {key:20} {val!s:>4}  (w={w})")

    flags = veto_flags(c)
    if flags:
        print("\nVeto / warnings:")
        for f in flags:
            print(f"  ! {f}")

    stage = (c.get("stage") or "discover").lower()
    items = STAGE_CHECKLIST.get(stage, STAGE_CHECKLIST["discover"])
    print(f"\nChecklist ({stage}):")
    for item in items:
        print(f"  [ ] {item}")

    if total >= threshold and not flags:
        print("\n=> Screen PASS: mozhno perehodit k spike")
    elif flags:
        print("\n=> Screen FAIL: resolve veto before spike")
    else:
        print("\n=> Screen FAIL: score below threshold — reject or defer")

    if c.get("notes_en"):
        print("\nnotes_en:")
        for line in str(c["notes_en"]).strip().splitlines():
            print(f"  {line}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="OSS funnel checklist (offline)")
    parser.add_argument("--name", "-n", help="Candidate id filter")
    parser.add_argument("--tracker", type=Path, default=TRACKER)
    args = parser.parse_args()

    if not args.tracker.is_file():
        print(f"Tracker not found: {args.tracker}", file=sys.stderr)
        return 1

    data = yaml.safe_load(args.tracker.read_text(encoding="utf-8"))
    weights = data.get("rubric_weights") or {}
    threshold = float(data.get("screen_threshold", 3.0))
    candidates = data.get("candidates") or []

    if args.name:
        candidates = [c for c in candidates if c.get("id") == args.name]
        if not candidates:
            print(f"No candidate with id={args.name!r}", file=sys.stderr)
            return 1

    print(f"Errorlogy OSS funnel — {len(candidates)} candidate(s)")
    print(f"Doc: docs/oss-integration-funnel.md")

    for c in candidates:
        print_candidate(c, weights, threshold)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
