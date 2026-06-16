"""
Live Scout extraction eval (Harness Phase C — P2).

Runs ScoutAgent on seed raw-text snippets and asserts GovernanceCase schema +
field expectations per tests/evals/specs/scout.yaml.

Skip by default. Run:
  EVAL_LIVE=1 pytest tests/evals/test_scout_extraction_live.py -v
  EVAL_LIVE=1 pytest -m llm_eval -v
"""

from __future__ import annotations

import pytest

from mas.agents.neutrality import FORBIDDEN_PATTERNS
from mas.schemas.case import GovernanceCase, WeakSignal
from tests.evals.seed_loader import EVAL_LIVE, load_seed_pack

_LIVE_SKIP = pytest.mark.skipif(
    not EVAL_LIVE,
    reason="Set EVAL_LIVE=1 to run live LLM evals",
)

EXTRACTION_CASES = load_seed_pack("scout_extraction.yaml")

_DEFAULT_REQUIRED = ("case_id", "title", "description", "weak_signals")


def _assert_governance_case(result: GovernanceCase, case: dict) -> None:
    expect = case.get("expect", {})
    required = expect.get("required_fields", list(_DEFAULT_REQUIRED))

    for field in required:
        value = getattr(result, field, None)
        if field == "weak_signals":
            assert isinstance(value, list), f"{case['id']}: weak_signals must be a list"
        elif field in ("case_id", "title", "description"):
            assert value and str(value).strip(), f"{case['id']}: missing {field}"
        else:
            assert value is not None, f"{case['id']}: missing {field}"

    weak_signals_min = expect.get("weak_signals_min", 1)
    assert len(result.weak_signals) >= weak_signals_min, (
        f"{case['id']}: expected >={weak_signals_min} weak signal(s); "
        f"got {len(result.weak_signals)}"
    )

    for signal in result.weak_signals:
        assert isinstance(signal, WeakSignal)
        assert signal.signal_type.strip(), f"{case['id']}: weak signal missing signal_type"
        assert signal.description.strip(), f"{case['id']}: weak signal missing description"
        assert 0.0 <= signal.strength <= 1.0
        assert 0.0 <= signal.reliability <= 1.0
        assert 0.0 <= signal.temporal_relevance <= 1.0

    if case.get("case_id"):
        assert result.case_id == case["case_id"], (
            f"{case['id']}: case_id mismatch (expected {case['case_id']!r}, got {result.case_id!r})"
        )

    description_lower = result.description.lower()
    for pattern in FORBIDDEN_PATTERNS:
        assert pattern not in description_lower, (
            f"{case['id']}: forbidden pattern {pattern!r} in Scout description"
        )


@pytest.mark.llm_eval
@_LIVE_SKIP
@pytest.mark.parametrize(
    "case",
    EXTRACTION_CASES,
    ids=[c["id"] for c in EXTRACTION_CASES],
)
def test_scout_extraction_live(scout_agent, case):
    raw_text = case["raw_text"].strip()
    result = scout_agent.run(
        case_id=case["case_id"],
        raw_text=raw_text,
        title=case.get("title", ""),
        country=case.get("country", ""),
        year=int(case.get("year", 0)),
    )
    assert isinstance(result, GovernanceCase)
    _assert_governance_case(result, case)


def test_extraction_seed_ids_unique():
    ids = [c["id"] for c in EXTRACTION_CASES]
    assert len(ids) == len(set(ids))


def test_extraction_pack_has_minimum_cases():
    assert len(EXTRACTION_CASES) >= 8, "scout_extraction.yaml should have at least 8 cases"


@pytest.mark.parametrize("case", EXTRACTION_CASES, ids=[c["id"] for c in EXTRACTION_CASES])
def test_extraction_seed_structure(case):
    assert case.get("id")
    assert case.get("raw_text", "").strip()
    assert case.get("case_id")
    expect = case.get("expect", {})
    assert expect.get("weak_signals_min", 1) >= 1
