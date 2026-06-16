import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "llm_eval: live LLM eval tests (require EVAL_LIVE=1 and API keys)",
    )

from mas.schemas.case import GovernanceCase, WeakSignal

CHALLENGER_SNIPPET = """
NASA managers approved the Challenger launch despite engineer dissent about O-ring
performance in cold temperatures. Thiokol engineers recommended no launch below 53F.
Management reversed position after schedule pressure. Groupthink and authority bias
were documented. The Rogers Commission found organizational failure.
"""


@pytest.fixture
def challenger_case() -> GovernanceCase:
    return GovernanceCase(
        case_id="US-NASA-1986-CHALLENGER-01",
        title="STS-51L Challenger",
        description="Pre-launch authorization despite O-ring concerns and engineer dissent.",
        country="US",
        domain="space_agency",
        year=1986,
        source_text=CHALLENGER_SNIPPET,
        weak_signals=[
            WeakSignal(
                signal_type="expert_dissent_suppressed",
                description="Engineers opposed launch in cold weather",
                source_environment="contractor",
                strength=0.85,
                reliability=0.8,
                temporal_relevance=0.9,
            ),
            WeakSignal(
                signal_type="schedule_pressure",
                description="Launch schedule pressure from NASA",
                source_environment="agency",
                strength=0.75,
                reliability=0.7,
                temporal_relevance=0.85,
            ),
        ],
    )
