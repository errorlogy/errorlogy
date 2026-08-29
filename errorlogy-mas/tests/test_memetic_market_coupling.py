"""Memetic ↔ fin-crypto market coupling join tests (Iteration 6)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from mas.adapters.fin_crypto_ccxt import fetch_market_snapshot
from mas.db import init_db
from mas.institutional.activation import default_activated_layers, frame_cross_layer_event
from mas.memetic.market_coupling import (
    build_memetic_market_coupling,
    coupling_to_cross_layer_ingress,
    ingest_memetic_market_coupling,
    normalize_memetic_sidecar,
    persist_memetic_market_coupling,
    resolve_join_key,
    symbol_to_story_id,
)


@pytest.fixture
def client(tmp_path, monkeypatch):
    pytest.importorskip("itsdangerous")
    pytest.importorskip("authlib")
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "memetic_coupling_api.db")
    init_db()
    from api.main import app

    return TestClient(app)


def _sample_market_record(**overrides):
    base = {
        "adapter_id": "ccxt:market_snapshot",
        "record_id": "ccxt:market_snapshot:abc123",
        "story_id": "btc-coupling-story",
        "event_type": "fin_crypto_market_snapshot",
        "observed_at": "2026-08-29T12:00:00+00:00",
        "instrument": {
            "asset_class": "crypto",
            "symbol": "BTC-USDT",
            "exchange_or_venue": "binance",
        },
        "signal": {"name": "last_price", "value": 65000.0, "unit": "USDT"},
    }
    base.update(overrides)
    return base


def test_symbol_to_story_id():
    assert symbol_to_story_id("BTC/USDT") == "fin-crypto-btc-usdt-snapshot"


def test_resolve_join_key_prefers_story_id():
    sid, jtype, jval = resolve_join_key(story_id="explicit-story", symbol="ETH/USDT")
    assert sid == "explicit-story"
    assert jtype == "story_id"
    assert jval == "explicit-story"


def test_resolve_join_key_from_symbol():
    sid, jtype, jval = resolve_join_key(story_id=None, symbol="ETH/USDT")
    assert sid == "fin-crypto-eth-usdt-snapshot"
    assert jtype == "symbol"
    assert jval == "ETH-USDT"


def test_normalize_memetic_sidecar():
    sidecar = normalize_memetic_sidecar(
        {"peak_velocity": 120.0, "decay_tau_hours": 48.0},
        stream_item_id="si-coupling-1",
        story_id="btc-coupling-story",
    )
    assert sidecar is not None
    assert sidecar["peak_velocity"] == 120.0
    assert sidecar["stream_item_id"] == "si-coupling-1"


def test_build_coupling_framed_envelope():
    market = _sample_market_record()
    result = build_memetic_market_coupling(
        market,
        {"peak_velocity": 85.0, "decay_tau_hours": 36.0},
        stream_item_id="si-join-1",
    )
    event = result["cross_layer_event"]
    assert event["event_type"] == "memetic_market_coupling_snapshot"
    assert event["story_id"] == "btc-coupling-story"
    assert event["epistemic_label"] == "INSTITUTIONAL_MODEL"
    assert "institution:central-bank-analog" in event["activated_layers"]
    assert "institution:parliament" in event["activated_layers"]
    assert "institution:regulatory-agency" in event["activated_layers"]
    assert "ccxt:market_snapshot:abc123" in event["stream_refs"]
    assert "si-join-1" in event["stream_refs"]
    assert result["coupling_record"]["join_key"]["type"] == "story_id"


def test_coupling_without_memetic_sidecar():
    market = _sample_market_record(story_id="market-only")
    result = build_memetic_market_coupling(market, None)
    assert result["memetic_sidecar"] is None
    assert "memetic_sidecar_missing" in result["coupling_record"]["quality_flags"]


def test_coupling_ingress_jurisdiction():
    coupling = build_memetic_market_coupling(
        _sample_market_record(),
        {"peak_velocity": 10.0},
        stream_item_id="si-j",
    )
    ingress = coupling_to_cross_layer_ingress(
        coupling["coupling_record"], jurisdiction_set=["US", "EU"]
    )
    assert ingress["jurisdiction_set"] == ["US", "EU"]


def test_default_layers_memetic_market_coupling():
    layers = default_activated_layers("memetic_market_coupling_snapshot")
    assert layers == [
        "institution:central-bank-analog",
        "institution:parliament",
        "institution:regulatory-agency",
    ]


@patch("mas.memetic.market_coupling.fetch_market_snapshot")
def test_ingest_memetic_market_coupling(mock_fetch):
    mock_fetch.return_value = _sample_market_record()
    result = ingest_memetic_market_coupling(
        symbol="BTC/USDT",
        exchange_id="binance",
        memetic_metrics={"peak_velocity": 50.0, "decay_tau_hours": 24.0},
        stream_item_id="si-ingest",
    )
    assert result["cross_layer_event"]["event_type"] == "memetic_market_coupling_snapshot"
    mock_fetch.assert_called_once()


def test_persist_memetic_market_coupling(tmp_path, monkeypatch):
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "coupling_persist.db")
    init_db()
    result = persist_memetic_market_coupling(
        market_record=_sample_market_record(),
        memetic_metrics={"peak_velocity": 30.0},
        stream_item_id="si-persist",
    )
    assert result["status"] == "stored"
    assert result["event_id"].startswith("cle-")


@patch("api.routers.cross_layer.persist_memetic_market_coupling")
def test_api_memetic_market_coupling_endpoint(mock_persist, client):
    mock_persist.return_value = {
        "status": "stored",
        "event_id": "cle-coupling1",
        "coupling_record": {"coupling_id": "memetic_market_coupling:abc"},
        "market_record": _sample_market_record(),
        "memetic_sidecar": {"peak_velocity": 100.0, "stream_item_id": "si-api"},
        "event": {
            "event_id": "cle-coupling1",
            "story_id": "btc-coupling-story",
            "event_type": "memetic_market_coupling_snapshot",
            "epistemic_label": "INSTITUTIONAL_MODEL",
            "activated_layers": ["institution:central-bank-analog"],
        },
    }
    resp = client.post(
        "/api/events/memetic/market-coupling",
        json={
            "symbol": "BTC/USDT",
            "exchange": "binance",
            "story_id": "btc-coupling-story",
            "stream_item_id": "si-api",
            "peak_velocity": 100.0,
            "decay_tau_hours": 48.0,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "stored"
    assert body["event"]["event_type"] == "memetic_market_coupling_snapshot"
    mock_persist.assert_called_once()


def test_fetch_and_couple_live_integration():
    pytest.importorskip("ccxt")
    record = fetch_market_snapshot("BTC/USDT", "binance", story_id="live-coupling")
    result = build_memetic_market_coupling(
        record,
        {"peak_velocity": 42.0, "decay_tau_hours": 72.0},
        stream_item_id="si-live",
    )
    framed = frame_cross_layer_event(result["cross_layer_ingress"])
    assert framed["event_type"] == "memetic_market_coupling_snapshot"
    assert framed["epistemic_label"] == "INSTITUTIONAL_MODEL"
