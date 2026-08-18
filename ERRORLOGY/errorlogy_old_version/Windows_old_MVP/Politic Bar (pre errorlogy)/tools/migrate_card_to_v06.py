"""Schema-only migration: v0.1 / v0.2 cards → v0.6 schema, no LLM.

What this does
--------------
Old seed cards (SU-USSR-1986-CHERNOBYL-01, US-IC-2002-IRAQ-WMD-01,
GB-POL-1999-HORIZON-01, US-MMS-2010-DEEPWATER-01, US-NASA-1986-CHALLENGER-01)
were authored against the v0.1/v0.2 schema. They lack the v0.6 fields
asymmetry_vectors, propagated_from, propagates_to, constitutive_roles,
event_type, and their classifications use bias_id/bias_name without an
explicit `layer`. As a result:

- They cannot be loaded into politic_bar.models.ErrorCard.
- They never appear as candidates for Chain-Mapper propagation links
  (the catalog DAG ignores them).
- They cannot be aggregated by the new actor-profile pipeline.

This migration adds the missing fields with empty/default values and
upgrades classification entries in place: bias_id→mode_id, bias_name→
mode_name, and layer is inferred from cognitive_biases.json category.
NO new factual claims are introduced; the migration is schema-only,
content-preserving.

Usage
-----
    python -m tools.migrate_card_to_v06              # dry-run all cases
    python -m tools.migrate_card_to_v06 --apply      # write changes
    python -m tools.migrate_card_to_v06 CASE-ID      # one case, dry-run
    python -m tools.migrate_card_to_v06 CASE-ID --apply

Idempotent: a card already at v0.6 (i.e. with event_type set) is left
untouched.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "cases"
TAXONOMY_DIR = ROOT / "taxonomy"


# ---------------------------------------------------------------------------
# Layer inference from category
# ---------------------------------------------------------------------------

# Mapping cognitive_biases.json categories to METHODOLOGY §5/§5a layers.
# Anything not listed defaults to L1 (individual cognitive bias).
_CATEGORY_TO_LAYER = {
    "group": "L2",
    "informational_environment": "L3",
}


def _load_bias_layer_index() -> dict[str, str]:
    """Build {CB-id: layer} from cognitive_biases.json category."""
    data = json.loads((TAXONOMY_DIR / "cognitive_biases.json").read_text(encoding="utf-8"))
    return {
        b["id"]: _CATEGORY_TO_LAYER.get(b.get("category", ""), "L1")
        for b in data["biases"]
    }


# ---------------------------------------------------------------------------
# Per-card migration
# ---------------------------------------------------------------------------

def needs_migration(card: dict) -> bool:
    """A card is at v0.6 when event_type is set. Anything else is older."""
    return "event_type" not in card


def _migrate_classification(c: dict, bias_layer: dict[str, str]) -> dict:
    """Upgrade one classification dict in place-style: returns new dict."""
    out = dict(c)
    if "mode_id" not in out and "bias_id" in out:
        out["mode_id"] = out["bias_id"]
    if "mode_name" not in out and "bias_name" in out:
        out["mode_name"] = out["bias_name"]
    if "layer" not in out:
        # Infer from cognitive_biases.json category. If the id is not a
        # CB-* (cannot happen for v0.1/v0.2 cards but guard anyway), fall
        # back to L1.
        out["layer"] = bias_layer.get(out.get("mode_id", ""), "L1")
    return out


def migrate_card(card: dict, bias_layer: dict[str, str]) -> dict:
    """Return a new card dict with v0.6 schema fields added.

    Pure function: does not mutate the input. Schema-only — no factual
    claims introduced. Migration metadata is appended to analyst_notes."""
    if not needs_migration(card):
        return card

    out = dict(card)

    # Default fields v0.6 expects
    out.setdefault("event_type", "decision")
    out.setdefault("asymmetry_vectors", [])
    out.setdefault("propagated_from", [])
    out.setdefault("propagates_to", [])
    out.setdefault("constitutive_roles", [])
    out.setdefault("counter_arguments", [])
    out.setdefault("residual_uncertainty", "")
    out.setdefault("sources", [])

    # Upgrade classifications
    out["classifications"] = [
        _migrate_classification(c, bias_layer)
        for c in out.get("classifications", [])
    ]

    # Bump version, append migration note
    prior_version = out.get("version", 1)
    out["version"] = prior_version + 1

    migration_note = (
        f"[v0.1/v0.2 → v0.6 schema migration {datetime.utcnow().date().isoformat()}: "
        f"event_type, asymmetry_vectors, propagated_from, propagates_to, "
        f"constitutive_roles defaulted to empty; classifications got mode_id "
        f"and inferred layer per cognitive_biases.json category. "
        f"Schema-only: no new factual claims introduced. "
        f"Prior version: {prior_version}.]"
    )
    existing_notes = (out.get("analyst_notes") or "").strip()
    out["analyst_notes"] = (
        f"{existing_notes} {migration_note}".strip() if existing_notes else migration_note
    )

    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _iter_target_cards(only_id: str | None):
    if only_id:
        path = CASES_DIR / only_id / "card.json"
        if not path.exists():
            print(f"error: cases/{only_id}/card.json not found", file=sys.stderr)
            sys.exit(2)
        yield only_id, path
        return
    for case_dir in sorted(CASES_DIR.iterdir()):
        card_path = case_dir / "card.json"
        if card_path.exists():
            yield case_dir.name, card_path


def _diff_summary(before: dict, after: dict) -> list[str]:
    """Compact human-readable summary of what changed."""
    lines = []
    added = sorted(set(after) - set(before))
    if added:
        lines.append(f"  + fields added: {', '.join(added)}")
    if before.get("version") != after.get("version"):
        lines.append(f"  + version: {before.get('version')} → {after.get('version')}")
    cls_before = before.get("classifications", []) or []
    cls_after = after.get("classifications", []) or []
    if cls_before and cls_after:
        upgraded = sum(1 for b, a in zip(cls_before, cls_after)
                       if "mode_id" not in b and "mode_id" in a)
        if upgraded:
            lines.append(f"  + classifications upgraded: {upgraded}/{len(cls_after)} "
                         "got mode_id + layer")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("case_id", nargs="?", help="single case id, or omit for all cases")
    parser.add_argument("--apply", action="store_true",
                        help="write changes to disk (default is dry-run)")
    args = parser.parse_args(argv)

    bias_layer = _load_bias_layer_index()
    n_total = 0
    n_changed = 0

    for case_id, card_path in _iter_target_cards(args.case_id):
        n_total += 1
        before = json.loads(card_path.read_text(encoding="utf-8"))
        if not needs_migration(before):
            print(f"{case_id}: already v0.6, skip")
            continue
        after = migrate_card(before, bias_layer)
        n_changed += 1
        print(f"{case_id}: migrate v{before.get('version')} → v{after['version']}")
        for line in _diff_summary(before, after):
            print(line)
        if args.apply:
            card_path.write_text(
                json.dumps(after, indent=2, default=str, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"  wrote {card_path}")

    mode = "applied" if args.apply else "dry-run"
    print(f"\n{n_changed}/{n_total} card(s) need migration ({mode}).")
    if n_changed and not args.apply:
        print("Re-run with --apply to write changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
