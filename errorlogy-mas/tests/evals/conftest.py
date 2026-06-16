"""Shared fixtures for eval harness (Phase B+)."""

from __future__ import annotations

import pytest

from mas.agents.base import set_router
from mas.config import Config
from mas.providers import build_router
from tests.evals.seed_loader import EVAL_LIVE


def _live_eval_skip_reason() -> str | None:
    if not EVAL_LIVE:
        return "Set EVAL_LIVE=1 to run live LLM evals"
    cfg = Config()
    if not cfg.available_providers():
        return "No LLM API keys loaded (run scripts/load_keys_from_vault.ps1)"
    return None


@pytest.fixture(scope="module")
def llm_router():
    reason = _live_eval_skip_reason()
    if reason:
        pytest.skip(reason)
    router = build_router(Config())
    set_router(router)
    return router


@pytest.fixture(scope="module")
def neutrality_agent(llm_router):
    from mas.agents.neutrality import NeutralityAuditorAgent

    return NeutralityAuditorAgent()


@pytest.fixture(scope="module")
def scout_agent(llm_router):
    from mas.agents.scout import ScoutAgent

    return ScoutAgent()
