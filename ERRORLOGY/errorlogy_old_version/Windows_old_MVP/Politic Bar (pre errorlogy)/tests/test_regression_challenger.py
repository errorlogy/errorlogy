"""Regression test: the v0.6 CHALLENGER pipeline outputs deserialize cleanly.

Reads cases/US-NASA-1986-CHALLENGER-V06-01/_pipeline/*.json and
cases/US-NASA-1986-CHALLENGER-V06-01/card.json — does NOT touch the
network or the LLM. If any pipeline stage's output ever drifts away
from models.py, this test catches it before the next real run.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from politic_bar.models import (
    Citation,
    Classification,
    ConstitutiveRole,
    CounterArgument,
    ErrorCard,
    NeutralityAudit,
    PropagationLink,
    Source,
    AsymmetryVector,
    VerificationResult,
)

ROOT = Path(__file__).resolve().parent.parent
CASE_DIR = ROOT / "cases" / "US-NASA-1986-CHALLENGER-V06-01"
PIPELINE_DIR = CASE_DIR / "_pipeline"


# Skip the entire module if the regression fixture has been removed
# (e.g. the analyst archived the case). Pipeline regressions on a missing
# fixture would be noise, not signal.
pytestmark = pytest.mark.skipif(
    not (CASE_DIR / "card.json").exists(),
    reason="CHALLENGER v0.6 regression fixture not present",
)


def _load(stage: str):
    return json.loads((PIPELINE_DIR / f"{stage}.json").read_text(encoding="utf-8"))


def test_classifications_deserialize_to_models():
    raw = _load("04_classifications")
    assert isinstance(raw, list)
    assert len(raw) > 0
    for item in raw:
        c = Classification(**item)
        assert c.layer in ("L1", "L2", "L3", "L4", "L5")
        assert c.confidence in ("high", "medium", "low")
        assert c.mode_id.startswith(("CB-", "SF-", "MP-"))


def test_classifications_mode_ids_resolve_in_their_taxonomy():
    raw = _load("04_classifications")

    cb_ids = {b["id"] for b in json.loads(
        (ROOT / "taxonomy" / "cognitive_biases.json").read_text(encoding="utf-8"))["biases"]}
    sf_ids = {m["id"] for m in json.loads(
        (ROOT / "taxonomy" / "strategic_failure_modes.json").read_text(encoding="utf-8"))["modes"]}
    mp_ids = {m["id"] for m in json.loads(
        (ROOT / "taxonomy" / "mechanism_pathologies.json").read_text(encoding="utf-8"))["modes"]}

    for c in raw:
        mid = c["mode_id"]
        if mid.startswith("CB-"):
            assert mid in cb_ids, f"CHALLENGER cites unknown CB-id {mid}"
        elif mid.startswith("SF-"):
            assert mid in sf_ids, f"CHALLENGER cites unknown SF-id {mid}"
        elif mid.startswith("MP-"):
            assert mid in mp_ids, f"CHALLENGER cites unknown MP-id {mid}"
        else:
            pytest.fail(f"unknown mode_id namespace: {mid}")


def test_chain_mapper_outputs_deserialize():
    raw = _load("03_chain_mapper")
    for v in raw.get("asymmetry_vectors", []):
        AsymmetryVector(**v)
    for p in raw.get("propagation_links", []):
        PropagationLink(**p)


def test_counter_arguments_deserialize():
    raw = _load("05_counter_arguments")
    assert isinstance(raw, list)
    for item in raw:
        ca = CounterArgument(**item)
        assert ca.target_kind in (
            "classification", "asymmetry_vector", "propagation_link",
            "foreseeability", "gap",
        )


def test_verifications_deserialize():
    raw = _load("06_verifications")
    assert isinstance(raw, list)
    for item in raw:
        VerificationResult(**item)


def test_neutrality_audit_passed():
    raw = _load("07_neutrality_audit")
    audit = NeutralityAudit(**raw)
    assert audit.passed, (
        "CHALLENGER v0.6 fixture should ship with neutrality_audit.passed=True; "
        f"violations: {audit.violations}"
    )


def test_published_card_deserializes_and_has_v06_fields():
    """The published card must round-trip into ErrorCard with all v0.6
    fields populated according to schema, not just present-as-empty."""
    raw = json.loads((CASE_DIR / "card.json").read_text(encoding="utf-8"))

    # Reconstruct nested dataclasses by hand — ErrorCard.__init__ takes
    # typed lists and we want to fail loudly if any element is malformed.
    classifications = [Classification(**c) for c in raw.get("classifications", [])]
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
        event_type=raw.get("event_type", "decision"),
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

    assert card.event_type == "decision"
    assert card.classifications, "v0.6 CHALLENGER must have at least one classification"
    assert card.constitutive_roles, "v0.6 CHALLENGER must have constitutive_roles populated"
    assert card.asymmetry_vectors, "v0.6 CHALLENGER must have asymmetry_vectors populated"
    # Sanity: every classification carries explicit layer (no v0.1 holdover).
    assert all(c.layer in ("L1", "L2", "L3", "L4", "L5") for c in card.classifications)
