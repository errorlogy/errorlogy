"""CEP alert query tests."""

from datetime import datetime, timedelta, timezone

from mas.db import init_db, save_signal_point
from mas.engine.cep_alerts import (
    cep_severity,
    count_active_alerts,
    list_cep_alerts,
    signal_trends,
)


def _ts(days_ago: int = 0) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


def test_cep_severity_bands():
    assert cep_severity(0.55) == "low"
    assert cep_severity(0.7) == "medium"
    assert cep_severity(0.85) == "high"


def test_list_cep_alerts_threshold(tmp_path, monkeypatch):
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "alerts.db")
    init_db()

    save_signal_point(
        country="USA", iso3="USA", case_id="C1", doc_id="d1",
        msi=0.4, cep=0.45, echo_pressure=0.3, dominant_pno="PNO-1", cat="CAT-000",
    )
    save_signal_point(
        country="UK", iso3="GBR", case_id="C2", doc_id="d2",
        msi=0.6, cep=0.72, echo_pressure=0.3, dominant_pno="PNO-1", cat="CAT-003",
    )

    low = list_cep_alerts(cep_threshold=0.8)
    assert len(low) == 0

    mid = list_cep_alerts(cep_threshold=0.5)
    assert len(mid) == 1
    assert mid[0]["iso3"] == "GBR"
    assert mid[0]["severity"] == "medium"
    assert mid[0]["doc_id"] == "d2"


def test_count_active_alerts(tmp_path, monkeypatch):
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "count.db")
    init_db()
    save_signal_point(
        country="USA", iso3="USA", case_id="C1", doc_id="d1",
        msi=0.5, cep=0.6, echo_pressure=0.2, dominant_pno="PNO-1", cat="CAT-000",
    )
    assert count_active_alerts(cep_threshold=0.5) == 1
    assert count_active_alerts(cep_threshold=0.9) == 0


def test_signal_trends_delta(tmp_path, monkeypatch):
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "trends.db")
    init_db()

    # Older point — patch recorded_at via direct insert
    save_signal_point(
        country="USA", iso3="USA", case_id="C1", doc_id="d-old",
        msi=0.3, cep=0.4, echo_pressure=0.2, dominant_pno="PNO-1", cat="CAT-000",
    )
    save_signal_point(
        country="USA", iso3="USA", case_id="C2", doc_id="d-new",
        msi=0.5, cep=0.55, echo_pressure=0.2, dominant_pno="PNO-1", cat="CAT-000",
    )

    trends = signal_trends(window_days=7)
    usa = next(t for t in trends if t["iso3"] == "USA")
    assert usa["cep_max"] >= 0.55
    assert usa["signal_count"] >= 2


def test_alerts_filter_iso3(tmp_path, monkeypatch):
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "filter.db")
    init_db()
    save_signal_point(
        country="USA", iso3="USA", case_id="C1", doc_id="d1",
        msi=0.5, cep=0.7, echo_pressure=0.2, dominant_pno="PNO-1", cat="CAT-000",
    )
    save_signal_point(
        country="UK", iso3="GBR", case_id="C2", doc_id="d2",
        msi=0.5, cep=0.7, echo_pressure=0.2, dominant_pno="PNO-1", cat="CAT-000",
    )
    alerts = list_cep_alerts(cep_threshold=0.5, iso3="USA")
    assert len(alerts) == 1
    assert alerts[0]["iso3"] == "USA"
