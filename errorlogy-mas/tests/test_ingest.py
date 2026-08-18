"""Ingest layer tests."""

from mas.db import init_db, save_raw_document, list_raw_documents, save_signal_point, ingest_stats
from mas.ingest import ingest_document


def test_ingest_manual_no_analyze(tmp_path, monkeypatch):
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "test.db")
    init_db()

    r = ingest_document(
        source="manual",
        text="NASA management overruled engineers on launch decision under schedule pressure.",
        title="Test ingest",
        country="USA",
        auto_analyze=False,
    )
    assert r["doc_id"]
    assert r["status"] == "stored"

    docs = list_raw_documents(limit=10)
    assert len(docs) == 1
    assert docs[0]["source"] == "manual"


def test_signal_timeseries(tmp_path, monkeypatch):
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "test2.db")
    init_db()
    save_signal_point(
        country="USA",
        iso3="USA",
        case_id="C-1",
        doc_id="d-1",
        msi=0.5,
        cep=0.6,
        echo_pressure=0.4,
        dominant_pno="PNO-1",
        cat="CAT-003",
    )
    stats = ingest_stats()
    assert stats["signals_total"] == 1
