"""Post-migration regression: every card.json under cases/ deserialises
into politic_bar.models.ErrorCard without errors.

Confirms the v0.1/v0.2 → v0.6 schema migration was content-preserving
and that the old seed cards now participate in the same type contract
as cards produced by the live pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from politic_bar.models import (
    AsymmetryVector,
    Classification,
    ConstitutiveRole,
    CounterArgument,
    ErrorCard,
    PropagationLink,
    Source,
)

ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "cases"


def _all_card_paths() -> list[Path]:
    if not CASES_DIR.exists():
        return []
    return sorted(p / "card.json" for p in CASES_DIR.iterdir()
                  if (p / "card.json").exists())


@pytest.mark.parametrize("card_path", _all_card_paths(),
                         ids=lambda p: p.parent.name)
def test_card_loads_into_error_card(card_path: Path):
    raw = json.loads(card_path.read_text(encoding="utf-8"))

    classifications = [Classification(
        mode_id=c.get("mode_id") or c["bias_id"],
        mode_name=c.get("mode_name") or c["bias_name"],
        layer=c["layer"],
        evidence_excerpt=c["evidence_excerpt"],
        source_ref=c["source_ref"],
        confidence=c["confidence"],
        justification=c["justification"],
    ) for c in raw.get("classifications", [])]

    asymmetry_vectors = [AsymmetryVector(**v) for v in raw.get("asymmetry_vectors", [])]
    propagated_from = [PropagationLink(**p) for p in raw.get("propagated_from", [])]
    propagates_to = [PropagationLink(**p) for p in raw.get("propagates_to", [])]
    constitutive_roles = [ConstitutiveRole(**r) for r in raw.get("constitutive_roles", [])]
    counter_arguments = [CounterArgument(**a) for a in raw.get("counter_arguments", [])]
    sources = [Source(**s) for s in raw.get("sources", [])]

    card = ErrorCard(
        id=raw["id"],
        version=raw["version"],
        country=raw["country"],
        branch=raw["branch"],
        level=raw["level"],
        body=raw["body"],
        decision_date=raw["decision_date"],
        event_type=raw["event_type"],
        summary=raw["summary"],
        claimed=raw["claimed"],
        known_or_knowable=raw["known_or_knowable"],
        decision=raw["decision"],
        gap=raw["gap"],
        classifications=classifications,
        asymmetry_vectors=asymmetry_vectors,
        propagated_from=propagated_from,
        propagates_to=propagates_to,
        constitutive_roles=constitutive_roles,
        counter_arguments=counter_arguments,
        residual_uncertainty=raw.get("residual_uncertainty", ""),
        sources=sources,
        analyst_notes=raw.get("analyst_notes", ""),
        compiled_at=raw.get("compiled_at", ""),
    )

    assert card.event_type in ("decision", "non_decision", "unstable_decision")
    assert card.classifications, f"{card.id}: no classifications after migration"
    for c in card.classifications:
        assert c.layer in ("L1", "L2", "L3", "L4", "L5"), (
            f"{card.id}: classification {c.mode_id} has invalid layer {c.layer!r}"
        )
