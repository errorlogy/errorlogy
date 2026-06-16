"""
Live Neutrality Auditor eval pilot (Harness Phase B — P1).

Runs the NeutralityAuditorAgent on seed public-card texts. Batch eval uses API keys
from errorlogy-mas/.env (see scripts/load_keys_from_vault.ps1); OAuth in api/auth is
N/A for this harness — no browser session required.

Skip by default. Run:
  EVAL_LIVE=1 pytest tests/evals/test_neutrality_live.py -v
  EVAL_LIVE=1 pytest -m llm_eval -v
"""

from __future__ import annotations

import pytest

from mas.agents.neutrality import FORBIDDEN_PATTERNS
from tests.evals.seed_loader import EVAL_LIVE, load_seed_pack

_LIVE_SKIP = pytest.mark.skipif(
    not EVAL_LIVE,
    reason="Set EVAL_LIVE=1 to run live LLM evals",
)

VIOLATION_CASES = load_seed_pack("neutrality_violations.yaml")
CLEAN_CASES = load_seed_pack("neutrality_clean.yaml")


@pytest.mark.llm_eval
@_LIVE_SKIP
@pytest.mark.parametrize(
    "case",
    VIOLATION_CASES,
    ids=[c["id"] for c in VIOLATION_CASES],
)
def test_violation_seeds_raise_flags(neutrality_agent, case):
    text = case["text"].strip()
    flags = neutrality_agent.run(text)
    min_flags = case.get("expect", {}).get("min_flags", 1)

    assert len(flags) >= min_flags, (
        f"Expected >={min_flags} neutrality flag(s) for {case['id']}; got {len(flags)}: {flags}"
    )


@pytest.mark.llm_eval
@_LIVE_SKIP
@pytest.mark.parametrize(
    "case",
    CLEAN_CASES,
    ids=[c["id"] for c in CLEAN_CASES],
)
def test_clean_seeds_pass_or_minimal_flags(neutrality_agent, case):
    text = case["text"].strip()
    flags = neutrality_agent.run(text)
    max_flags = case.get("expect", {}).get("max_flags", 0)

    assert len(flags) <= max_flags, (
        f"Expected <={max_flags} flag(s) for clean seed {case['id']}; got {flags}"
    )


def test_forbidden_patterns_module_matches_spec():
    """L1 guard — FORBIDDEN_PATTERNS stable for graders."""
    assert "guilty" in FORBIDDEN_PATTERNS
    assert "criminal" in FORBIDDEN_PATTERNS
    assert len(FORBIDDEN_PATTERNS) >= 5


def test_violation_seed_ids_unique():
    ids = [c["id"] for c in VIOLATION_CASES]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("pattern", FORBIDDEN_PATTERNS)
def test_violation_pack_covers_forbidden_substrings(pattern):
    """At least one violation seed contains each canonical forbidden substring."""
    combined = "\n".join(c["text"] for c in VIOLATION_CASES).lower()
    assert pattern in combined, f"No violation seed contains forbidden pattern {pattern!r}"
