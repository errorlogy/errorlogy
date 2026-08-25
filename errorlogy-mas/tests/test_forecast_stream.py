"""Tests for GET /api/forecast/stream aggregate endpoint."""

import pytest
from fastapi.testclient import TestClient

from mas.db import init_db, save_signal_point


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "forecast_stream.db")
    init_db()
    from api.main import app
    return TestClient(app)


def test_stream_forecast_empty_db(client):
    res = client.get("/api/forecast/stream")
    assert res.status_code == 200
    data = res.json()
    assert "generated_at" in data
    assert data["window_days"] == 30
    assert data["taxonomy"]["mode_count"] > 0
    assert data["engine"]["version"] == "v1-math"
    assert "ingest" in data["engine_modules_used"]
    assert data["ingest"]["documents_total"] == 0
    assert data["alerts"] == []
    assert data["horizon_note"]
    assert "μ" in data["methodology"] or "fuzzy" in data["methodology"].lower()
    assert data["methodology"]


def test_stream_forecast_with_signals(client):
    save_signal_point(
        country="USA", iso3="USA", case_id="C1", doc_id="d1",
        msi=0.5, cep=0.72, echo_pressure=0.3, dominant_pno="PNO-1", cat="CAT-000",
    )
    res = client.get("/api/forecast/stream?window_days=7&limit=10&cep_threshold=0.5")
    assert res.status_code == 200
    data = res.json()
    assert len(data["alerts"]) >= 1
    assert data["alerts"][0]["iso3"] == "USA"
    assert len(data["trends"]) >= 1
    assert data["ingest"]["active_alerts_count"] >= 1


def test_stream_forecast_country_filter(client):
    save_signal_point(
        country="USA", iso3="USA", case_id="C1", doc_id="d1",
        msi=0.5, cep=0.72, echo_pressure=0.3, dominant_pno="PNO-1", cat="CAT-000",
    )
    save_signal_point(
        country="UK", iso3="GBR", case_id="C2", doc_id="d2",
        msi=0.4, cep=0.55, echo_pressure=0.2, dominant_pno="PNO-2", cat="CAT-001",
    )
    res = client.get("/api/forecast/stream?iso3=GBR&cep_threshold=0.5")
    assert res.status_code == 200
    data = res.json()
    assert all(a["iso3"] == "GBR" for a in data["alerts"])
    assert all(t["iso3"] == "GBR" for t in data["trends"])
