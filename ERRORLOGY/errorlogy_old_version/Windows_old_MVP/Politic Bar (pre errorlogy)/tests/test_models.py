"""Schema round-trip tests for politic_bar.models (METHODOLOGY v0.6).

For every dataclass that ships in a published card or pipeline stage:
construct → asdict → reconstruct must be identity-preserving for flat
dataclasses, and ErrorCard.to_dict() must round-trip through json.
"""

from __future__ import annotations

import json
from dataclasses import asdict

from politic_bar.models import (
    ActorProfile,
    ActorProfileEntry,
    AsymmetryVector,
    AttractorRecord,
    CandidateAttractorFlag,
    Citation,
    Classification,
    ConstitutiveRole,
    CounterArgument,
    ErrorCard,
    FramedCase,
    NeutralityAudit,
    PropagationLink,
    Skeleton,
    Source,
    VerificationResult,
)


# ---------------------------------------------------------------------------
# Flat dataclasses: construct → asdict → reconstruct is identity
# ---------------------------------------------------------------------------

def test_source_round_trip():
    s = Source(title="Rogers Commission Report Vol. I",
               url="https://history.nasa.gov/rogersrep/v1ch5.htm",
               published_date="1986-06-06",
               source_type="primary")
    assert Source(**asdict(s)) == s


def test_citation_round_trip():
    c = Citation(source_id="rogers_v1", excerpt="Take off your engineering hat",
                 locator="Vol. I, Ch. V")
    assert Citation(**asdict(c)) == c


def test_skeleton_default_event_type_is_decision():
    sk = Skeleton(country="US", branch="executive", level="national",
                  body="NASA Marshall", decision_date="1986-01-28")
    assert sk.event_type == "decision"


def test_classification_legacy_aliases():
    """Older seed cards used bias_id / bias_name; the dataclass exposes
    those as @property aliases over mode_id / mode_name."""
    c = Classification(mode_id="CB-019", mode_name="Groupthink", layer="L2",
                       evidence_excerpt="...", source_ref="Rogers Vol I",
                       confidence="high", justification="...")
    assert c.bias_id == "CB-019"
    assert c.bias_name == "Groupthink"


def test_counter_argument_default_kind():
    ca = CounterArgument(targets="CB-019", strongest_counter="...",
                         does_it_survive=True)
    assert ca.target_kind == "classification"


def test_asymmetry_vector_round_trip():
    av = AsymmetryVector(type="AV1", between="Thiokol mgmt / Thiokol engineers",
                         evidence_excerpt="...", source_ref="Rogers Vol I")
    assert AsymmetryVector(**asdict(av)) == av


def test_propagation_link_round_trip():
    pl = PropagationLink(card_id="US-NASA-1986-CHALLENGER-V06-01", channel="AV3",
                         evidence_excerpt="...", source_ref="...",
                         justification="...")
    assert PropagationLink(**asdict(pl)) == pl


def test_constitutive_role_foreseeability_literal():
    """Foreseeability is one of the three §3 N6 literal values."""
    r = ConstitutiveRole(actor="Robert Lund", action_or_inaction="reversed recommendation",
                         contribution="signed off", foreseeability="documented_in_record",
                         evidence_excerpt="...", source_ref="...")
    assert r.foreseeability == "documented_in_record"


def test_verification_result_round_trip():
    v = VerificationResult(source_id="rogers_v1", excerpt="...", resolves=True,
                           quote_matches=True)
    assert VerificationResult(**asdict(v)) == v


def test_neutrality_audit_round_trip():
    n = NeutralityAudit(passed=True)
    assert NeutralityAudit(**asdict(n)) == n


# ---------------------------------------------------------------------------
# ErrorCard: full to_dict/json round-trip
# ---------------------------------------------------------------------------

def _minimal_card() -> ErrorCard:
    return ErrorCard(
        id="TEST-CASE-01",
        version=1,
        country="US",
        branch="executive",
        level="national",
        body="Test Body",
        decision_date="2026-04-26",
        event_type="decision",
        summary="Test summary.",
        claimed="Test claimed.",
        known_or_knowable="Test known.",
        decision="Test decision.",
        gap="Test gap.",
        sources=[Source(title="Test", url="https://example.invalid")],
    )


def test_error_card_to_dict_is_json_round_trippable():
    card = _minimal_card()
    d = card.to_dict()
    serialized = json.dumps(d, default=str, ensure_ascii=False)
    parsed = json.loads(serialized)

    # Required v0.6 fields all present (even if empty list).
    for k in ("asymmetry_vectors", "propagated_from", "propagates_to",
              "constitutive_roles", "classifications", "counter_arguments",
              "event_type"):
        assert k in parsed
    assert parsed["event_type"] == "decision"
    assert parsed["id"] == "TEST-CASE-01"


def test_error_card_compiled_at_is_iso_utc():
    card = _minimal_card()
    assert card.compiled_at.endswith("Z")
    assert "T" in card.compiled_at


# ---------------------------------------------------------------------------
# Derived views (§7a, §7b)
# ---------------------------------------------------------------------------

def test_actor_profile_round_trip():
    entry = ActorProfileEntry(card_id="TEST-01", decision_date="2026-04-26",
                              body="X", branch="executive", level="national",
                              role="principal")
    profile = ActorProfile(actor_id="x", display_name="X", entries=[entry])
    d = profile.to_dict()
    assert d["entries"][0]["card_id"] == "TEST-01"
    assert d["entries"][0]["role"] == "principal"


def test_attractor_record_requires_documented_exit_for_publication():
    """Schema permits empty documented_exit (a record under construction);
    publication policy enforces non-empty (tested elsewhere). We only
    verify that the field exists and is a list."""
    a = AttractorRecord(attractor_id="ATR-001", scope="test")
    d = a.to_dict()
    assert d["documented_exit"] == []
    assert "compiled_at" in d


def test_candidate_attractor_flag_default_timestamp():
    flag = CandidateAttractorFlag(component_signature="a||b||c||d",
                                  member_cards=["a", "b", "c", "d"])
    assert flag.flagged_at.endswith("Z")
