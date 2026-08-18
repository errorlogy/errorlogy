"""Schema migration v0.1/v0.2 → v0.6 — pure function tests, no I/O."""

from __future__ import annotations

from tools.migrate_card_to_v06 import (
    _CATEGORY_TO_LAYER,
    migrate_card,
    needs_migration,
)


# A representative v0.1 card — the SU-USSR-1986-CHERNOBYL-01 shape
_V01_CARD = {
    "id": "TEST-V01-01",
    "version": 1,
    "country": "X",
    "branch": "executive",
    "level": "national",
    "body": "Test Body",
    "decision_date": "1986-04-26",
    "summary": "summary",
    "claimed": "claimed",
    "known_or_knowable": "known",
    "decision": "decision",
    "gap": "gap",
    "classifications": [
        {"bias_id": "CB-019", "bias_name": "Groupthink",
         "evidence_excerpt": "...", "source_ref": "...",
         "confidence": "medium", "justification": "..."},
        {"bias_id": "CB-001", "bias_name": "Confirmation bias",
         "evidence_excerpt": "...", "source_ref": "...",
         "confidence": "high", "justification": "..."},
    ],
    "sources": [],
}


_BIAS_LAYER_STUB = {
    # CB-019 Groupthink lives in `group` category → L2
    "CB-019": "L2",
    # CB-001 Confirmation bias is `decision_and_belief` → L1
    "CB-001": "L1",
}


def test_needs_migration_detects_old_card():
    assert needs_migration(_V01_CARD) is True


def test_needs_migration_skips_v06_card():
    v06 = dict(_V01_CARD)
    v06["event_type"] = "decision"
    assert needs_migration(v06) is False


def test_migration_adds_v06_fields_with_empty_defaults():
    after = migrate_card(_V01_CARD, _BIAS_LAYER_STUB)

    assert after["event_type"] == "decision"
    assert after["asymmetry_vectors"] == []
    assert after["propagated_from"] == []
    assert after["propagates_to"] == []
    assert after["constitutive_roles"] == []
    assert after["counter_arguments"] == []
    assert after["residual_uncertainty"] == ""


def test_migration_upgrades_classifications_in_place():
    after = migrate_card(_V01_CARD, _BIAS_LAYER_STUB)
    cls = after["classifications"]

    # bias_id is preserved (legacy alias kept on disk) but mode_id + layer added.
    assert cls[0]["mode_id"] == "CB-019"
    assert cls[0]["mode_name"] == "Groupthink"
    assert cls[0]["layer"] == "L2"  # group category

    assert cls[1]["mode_id"] == "CB-001"
    assert cls[1]["layer"] == "L1"  # decision_and_belief default


def test_migration_bumps_version_and_records_note():
    after = migrate_card(_V01_CARD, _BIAS_LAYER_STUB)
    assert after["version"] == 2
    assert "schema migration" in after["analyst_notes"]
    assert "Schema-only" in after["analyst_notes"]
    # Prior version preserved in note for audit trail.
    assert "Prior version: 1" in after["analyst_notes"]


def test_migration_is_pure_does_not_mutate_input():
    before_snapshot = dict(_V01_CARD)
    before_snapshot["classifications"] = [dict(c) for c in _V01_CARD["classifications"]]

    migrate_card(_V01_CARD, _BIAS_LAYER_STUB)

    # Top-level keys unchanged
    assert "event_type" not in _V01_CARD
    # Classification dicts unchanged
    for original, snap in zip(_V01_CARD["classifications"],
                              before_snapshot["classifications"]):
        assert original == snap


def test_migration_idempotent_on_v06_card():
    v06 = dict(_V01_CARD)
    v06["event_type"] = "decision"
    out = migrate_card(v06, _BIAS_LAYER_STUB)
    assert out is v06  # short-circuit returns the same object


def test_category_layer_mapping_covers_l2_and_l3():
    """Sanity: the static mapping in the migrator matches what the
    Failure-Mode Classifier prompt expects (METHODOLOGY §5a)."""
    assert _CATEGORY_TO_LAYER["group"] == "L2"
    assert _CATEGORY_TO_LAYER["informational_environment"] == "L3"
