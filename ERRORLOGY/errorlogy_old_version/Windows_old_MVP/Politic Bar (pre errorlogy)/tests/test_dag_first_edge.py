"""First real DAG edge: DEEPWATER (2010) ← CHALLENGER-V06-01 (1986).

Pinned regression: this edge is hand-authored, not produced by the
pipeline, so any future tool run that overwrites either card without
re-asserting the link will fail this test before silent loss.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEEPWATER_PATH = ROOT / "cases" / "US-MMS-2010-DEEPWATER-01" / "card.json"
CHALLENGER_PATH = ROOT / "cases" / "US-NASA-1986-CHALLENGER-V06-01" / "card.json"


def _read_tolerant(path: Path) -> dict:
    """Tolerate cowork mount-cache trailing whitespace past the closing `}`."""
    obj, _ = json.JSONDecoder().raw_decode(path.read_text(encoding="utf-8"))
    return obj


# Verbatim Rogers Commission quote — already verified on the V06-01 card.
_ROGERS_EXCERPT_HEAD = (
    "The Commission is troubled by what appears to be a propensity of "
    "management at Marshall to contain potentially serious problems"
)


def test_deepwater_propagated_from_challenger_v06():
    mms = _read_tolerant(DEEPWATER_PATH)
    links = mms.get("propagated_from", [])
    matching = [l for l in links if l.get("card_id") == "US-NASA-1986-CHALLENGER-V06-01"]
    assert len(matching) == 1, (
        f"DEEPWATER should have exactly one propagated_from link to "
        f"CHALLENGER-V06-01; found {len(matching)}"
    )
    link = matching[0]
    assert link["channel"] == "AV3", f"channel must be AV3 (regulator-operator); got {link['channel']!r}"
    assert link["evidence_excerpt"].startswith(_ROGERS_EXCERPT_HEAD), (
        "evidence_excerpt must be the verbatim Rogers Commission Vol. I "
        "Chapter V passage (already verified on V06-01)"
    )
    assert "Rogers Commission" in link["source_ref"]
    # P1/P2/P3 §5b reasoning must be on the record.
    just = link["justification"]
    assert "P1" in just and "P2" in just and "P3" in just, (
        "propagation justification must spell out P1/P2/P3 (METHODOLOGY §5b)"
    )


def test_challenger_v06_has_back_ref_to_deepwater():
    ch = _read_tolerant(CHALLENGER_PATH)
    back_refs = ch.get("propagates_to", [])
    matching = [l for l in back_refs if l.get("card_id") == "US-MMS-2010-DEEPWATER-01"]
    assert len(matching) == 1, (
        "CHALLENGER-V06-01 should have exactly one propagates_to back-ref "
        "to DEEPWATER (catalog.update_propagates_to enforces idempotency)"
    )
    assert matching[0]["channel"] == "AV3"
    # Bumped from v1 to v2 when the back-ref was added.
    assert ch["version"] >= 2


def test_edge_quotes_match_on_both_sides():
    """The same Rogers excerpt appears on both ends of the edge — the
    propagation channel is anchored in the same verified quote."""
    mms = _read_tolerant(DEEPWATER_PATH)
    ch = _read_tolerant(CHALLENGER_PATH)

    fwd = next(l for l in mms["propagated_from"]
               if l["card_id"] == "US-NASA-1986-CHALLENGER-V06-01")
    back = next(l for l in ch["propagates_to"]
                if l["card_id"] == "US-MMS-2010-DEEPWATER-01")

    # Back-ref carries the same excerpt and source the analyst supplied.
    assert back["evidence_excerpt"] == fwd["evidence_excerpt"]
    assert back["source_ref"] == fwd["source_ref"]
