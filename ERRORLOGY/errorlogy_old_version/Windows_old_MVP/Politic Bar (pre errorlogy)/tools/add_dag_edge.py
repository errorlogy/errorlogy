"""Add a propagation edge between two published cards (METHODOLOGY §5b).

Schema-only operation: appends `propagated_from` on the downstream card
and triggers `catalog.update_propagates_to` to write the matching
`propagates_to` back-ref on the upstream card. No LLM. No new factual
claims beyond what the analyst supplies on the command line — the
evidence_excerpt must be verbatim and the source must be locator-bearing.

Robust against mount-cache trailing-whitespace residue (raw_decode).

Usage
-----
    python -m tools.add_dag_edge \\
        --downstream US-MMS-2010-DEEPWATER-01 \\
        --upstream   US-NASA-1986-CHALLENGER-V06-01 \\
        --channel    AV3 \\
        --evidence   "..." \\
        --source     "Rogers Commission Report, Vol. I, Chapter V" \\
        --justification "P1/P2/P3 reasoning..." \\
        [--apply]

Idempotent: re-running with the same (downstream, upstream) replaces
the prior link; the upstream's back-ref is replaced rather than
duplicated (catalog.update_propagates_to enforces that).
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime

from politic_bar import catalog


def _read_card_tolerant(path) -> dict:
    """raw_decode swallows trailing whitespace / mount-cache padding past
    the closing `}`. Plain json.loads would refuse with 'Extra data'."""
    text = path.read_text(encoding="utf-8")
    obj, _ = json.JSONDecoder().raw_decode(text)
    return obj


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--downstream", required=True,
                    help="case_id of the downstream card (gets propagated_from)")
    ap.add_argument("--upstream", required=True,
                    help="case_id of the upstream card (gets propagates_to back-ref)")
    ap.add_argument("--channel", required=True,
                    choices=["AV1", "AV2", "AV3", "AV4", "AV5"])
    ap.add_argument("--evidence", required=True,
                    help="verbatim excerpt anchoring the propagation claim")
    ap.add_argument("--source", required=True,
                    help="source ref / locator for the excerpt")
    ap.add_argument("--justification", default="",
                    help="P1-P3 justification per METHODOLOGY §5b")
    ap.add_argument("--apply", action="store_true",
                    help="write changes (default is dry-run)")
    args = ap.parse_args(argv)

    down_path = catalog.CASES_DIR / args.downstream / "card.json"
    if not down_path.exists():
        print(f"error: downstream cases/{args.downstream}/card.json not found")
        return 2

    upstream = catalog.load_card(args.upstream)
    if upstream is None:
        # load_card uses json.loads strictly; fall back to tolerant read.
        up_path = catalog.CASES_DIR / args.upstream / "card.json"
        if not up_path.exists():
            print(f"error: upstream cases/{args.upstream}/card.json not found")
            return 2
        upstream = _read_card_tolerant(up_path)

    # Hard guard: chronological direction.
    up_date = upstream.get("decision_date", "")
    down = _read_card_tolerant(down_path)
    down_date = down.get("decision_date", "")
    if up_date and down_date and up_date.split("/")[0] > down_date.split("/")[-1]:
        print(f"error: upstream date {up_date} > downstream date {down_date}. "
              f"Did you swap --upstream and --downstream?")
        return 3

    new_link = {
        "card_id": args.upstream,
        "channel": args.channel,
        "evidence_excerpt": args.evidence,
        "source_ref": args.source,
        "justification": args.justification,
    }

    existing = down.get("propagated_from", []) or []
    existing = [e for e in existing if e.get("card_id") != args.upstream]
    existing.append(new_link)
    down["propagated_from"] = existing

    prior_version = down.get("version", 1)
    down["version"] = prior_version + 1
    edit_note = (
        f"[Edge added by analyst {datetime.utcnow().date().isoformat()}: "
        f"propagated_from += {args.upstream} via {args.channel}. "
        f"Schema-only edit; evidence excerpt cited verbatim from source.]"
    )
    existing_notes = (down.get("analyst_notes") or "").strip()
    down["analyst_notes"] = (
        f"{existing_notes} {edit_note}".strip() if existing_notes else edit_note
    )

    print(f"downstream {args.downstream}: v{prior_version} → v{down['version']}; "
          f"propagated_from += {args.upstream} via {args.channel}")
    if not args.apply:
        print("dry-run; re-run with --apply to write changes.")
        return 0

    down_path.write_text(
        json.dumps(down, indent=2, default=str, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"wrote {down_path}")

    touched = catalog.update_propagates_to(down)
    print(f"upstream back-refs updated on: {touched}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
