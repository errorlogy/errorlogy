"""Smoke test for POST /api/analyze?engine_only=true (no LLM keys)."""

import pytest
from fastapi.testclient import TestClient

from mas.schemas.analysis import CaseAnalysis
from mas.schemas.case import GovernanceCase


@pytest.fixture(autouse=True)
def deterministic_engine(monkeypatch):
    monkeypatch.setenv("ERRORLOGY_USE_EMBEDDINGS", "0")


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "api_analyze.db")
    from mas.db import init_db

    init_db()

    from mas.orchestrator import Orchestrator
    from api.routers import analysis as analysis_router

    monkeypatch.setattr(analysis_router, "_orchestrator", Orchestrator(init_llm=False))

    from api.main import app

    return TestClient(app)


def _analyze_body(case: GovernanceCase) -> dict:
    return {
        "case_id": case.case_id,
        "raw_text": case.source_text,
        "title": case.title,
        "country": case.country,
        "year": case.year,
    }


def test_analyze_engine_only(client, challenger_case):
    res = client.post(
        "/api/analyze",
        params={"engine_only": True},
        json=_analyze_body(challenger_case),
    )
    assert res.status_code == 200, res.text

    validated = CaseAnalysis.model_validate(res.json())
    assert validated.case_id == challenger_case.case_id
    assert validated.metadata.get("engine_only") is True
    assert validated.wms.msi >= 0.0
    assert validated.pno.dominant_pno.startswith("PNO-")
    assert len(validated.top_modes) >= 1
