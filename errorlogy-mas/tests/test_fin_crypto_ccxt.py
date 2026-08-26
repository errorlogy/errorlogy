"""FIN_CRYPTO CCXT adapter tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from mas.adapters.fin_crypto_ccxt import (
    fetch_market_snapshot,
    ingest_fin_crypto_snapshot,
    record_to_cross_layer_ingress,
)
from mas.db import init_db
from mas.institutional.activation import default_activated_layers, frame_cross_layer_event


@pytest.fixture
def client(tmp_path, monkeypatch):
    pytest.importorskip("itsdangerous")
    pytest.importorskip("authlib")
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "fin_crypto_api.db")
    init_db()
    from api.main import app

    return TestClient(app)


def test_default_layers_memetic_market_before_memetic():
    market = default_activated_layers("memetic_market_coupling_snapshot")
    memetic = default_activated_layers("memetic_propagation_snapshot")
    assert "institution:central-bank-analog" in market
    assert "institution:central-bank-analog" not in memetic
    assert "institution:parliament" in memetic


def test_record_to_cross_layer_ingress():
    record = {
        "record_id": "ccxt:market_snapshot:abc",
        "story_id": "story-1",
        "event_type": "fin_crypto_market_snapshot",
    }
    ingress = record_to_cross_layer_ingress(record, jurisdiction_set=["US"])
    assert ingress["story_id"] == "story-1"
    assert ingress["event_type"] == "fin_crypto_market_snapshot"
    assert ingress["epistemic_label"] == "OPERATIONAL"
    assert ingress["jurisdiction_set"] == ["US"]
    assert ingress["stream_refs"] == ["ccxt:market_snapshot:abc"]


def test_fetch_market_snapshot_mock():
    exchange = MagicMock()
    exchange.fetch_ticker.return_value = {
        "last": 65000.5,
        "quoteVolume": 123456789.0,
        "timestamp": 1_700_000_000_000,
    }
    mock_ccxt = MagicMock()
    mock_ccxt.binance = MagicMock(return_value=exchange)

    with patch.dict("sys.modules", {"ccxt": mock_ccxt}):
        record = fetch_market_snapshot("BTC/USDT", "binance", story_id="btc-test")

    assert record["event_type"] == "fin_crypto_market_snapshot"
    assert record["story_id"] == "btc-test"
    assert record["signal"]["value"] == 65000.5
    assert record["instrument"]["exchange_or_venue"] == "binance"
    assert "public_rest_only" in record["quality_flags"]


def test_fetch_unavailable_on_provider_error():
    exchange = MagicMock()
    exchange.fetch_ticker.side_effect = RuntimeError("network blocked")
    mock_ccxt = MagicMock()
    mock_ccxt.kraken = MagicMock(return_value=exchange)

    with patch.dict("sys.modules", {"ccxt": mock_ccxt}):
        record = fetch_market_snapshot("BTC/USDT", "kraken")

    assert record["event_type"] == "fin_crypto_data_unavailable"
    assert record["signal"]["value"] == "RuntimeError"


def test_ingest_frames_operational_envelope():
    record = {
        "adapter_id": "ccxt:market_snapshot",
        "record_id": "ccxt:market_snapshot:test",
        "story_id": "s1",
        "event_type": "fin_crypto_market_snapshot",
        "observed_at": "2026-08-26T00:00:00+00:00",
    }
    with patch(
        "mas.adapters.fin_crypto_ccxt.fetch_market_snapshot", return_value=record
    ):
        result = ingest_fin_crypto_snapshot("BTC/USDT", "binance", story_id="s1")

    event = result["cross_layer_event"]
    assert event["epistemic_label"] == "OPERATIONAL"
    assert event["event_type"] == "fin_crypto_market_snapshot"
    assert "institution:central-bank-analog" in event["activated_layers"]


@patch("api.routers.cross_layer.persist_fin_crypto_snapshot")
def test_api_fin_crypto_snapshot_endpoint(mock_persist, client):
    mock_persist.return_value = {
        "status": "stored",
        "event_id": "cle-test123",
        "adapter_record": {
            "event_type": "fin_crypto_market_snapshot",
            "record_id": "r1",
        },
        "event": {
            "event_id": "cle-test123",
            "story_id": "api-btc",
            "event_type": "fin_crypto_market_snapshot",
            "epistemic_label": "OPERATIONAL",
            "activated_layers": ["institution:central-bank-analog"],
        },
    }
    resp = client.post(
        "/api/events/fin-crypto/snapshot",
        params={"symbol": "BTC/USDT", "exchange": "binance", "story_id": "api-btc"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "stored"
    assert body["event"]["event_type"] == "fin_crypto_market_snapshot"
    mock_persist.assert_called_once()


@pytest.mark.integration
def test_fetch_public_snapshot_live():
    pytest.importorskip("ccxt")
    record = fetch_market_snapshot("BTC/USDT", "binance", story_id="live-smoke")
    assert record["event_type"] in {
        "fin_crypto_market_snapshot",
        "fin_crypto_data_unavailable",
    }
    framed = frame_cross_layer_event(record_to_cross_layer_ingress(record))
    assert framed["epistemic_label"] == "OPERATIONAL"
