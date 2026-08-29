"""Sociome / MatrAIx persona cohort sidecar tests (Phase C / Iteration 7)."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from mas.db import init_db
from mas.institutional.activation import frame_cross_layer_event
from mas.memetic.market_coupling import build_memetic_market_coupling
from mas.memetic.sociome_sidecar import (
    attach_sociome_sidecar,
    parse_persona_cohort_id,
    sociome_sidecar_metadata,
)


@pytest.fixture
def client(tmp_path, monkeypatch):
    pytest.importorskip("itsdangerous")
    pytest.importorskip("authlib")
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "sociome_sidecar_api.db")
    init_db()
    from api.main import app

    return TestClient(app)


@pytest.mark.parametrize(
    "slug",
    [
        "matraix-1m-eu-de-n48-seed20260720",
        "eu-edu-strata-2026",
        "cohort_a",
    ],
)
def test_parse_persona_cohort_id_valid(slug):
    assert parse_persona_cohort_id(slug) == slug


@pytest.mark.parametrize(
    "slug",
    [
        "",
        "X",
        "UPPERCASE",
        "bad slug",
        "1starts-with-digit",
        "a" * 65,
    ],
)
def test_parse_persona_cohort_id_invalid(slug):
    with pytest.raises(ValueError, match="persona_cohort_id"):
        parse_persona_cohort_id(slug)


def test_sociome_sidecar_metadata():
    meta = sociome_sidecar_metadata("matraix-1m-eu-de-n48-seed20260720")
    assert meta["persona_cohort_id"] == "matraix-1m-eu-de-n48-seed20260720"
    assert meta["epistemic_label"] == "INSTITUTIONAL_MODEL"


def test_attach_sociome_sidecar():
    out = attach_sociome_sidecar({"story_id": "s1"}, "eu-edu-strata-2026")
    assert out["persona_cohort_id"] == "eu-edu-strata-2026"
    assert out["story_id"] == "s1"


def test_frame_cross_layer_with_persona_cohort_id():
    framed = frame_cross_layer_event(
        {
            "story_id": "sociome-story",
            "event_type": "discourse_fork_detected",
            "persona_cohort_id": "matraix-1m-eu-de-n48-seed20260720",
            "epistemic_label": "INSTITUTIONAL_MODEL",
        }
    )
    assert framed["persona_cohort_id"] == "matraix-1m-eu-de-n48-seed20260720"


def test_market_coupling_with_persona_cohort_id():
    market = {
        "record_id": "ccxt:market_snapshot:test",
        "story_id": "coupling-sociome",
        "event_type": "fin_crypto_market_snapshot",
        "instrument": {"symbol": "BTC-USDT"},
    }
    result = build_memetic_market_coupling(
        market,
        memetic_metrics={"peak_velocity": 12.5, "decay_tau_hours": 48.0},
        persona_cohort_id="matraix-1m-eu-de-n48-seed20260720",
    )
    assert result["coupling_record"]["persona_cohort_id"] == "matraix-1m-eu-de-n48-seed20260720"
    assert (
        result["cross_layer_event"]["persona_cohort_id"]
        == "matraix-1m-eu-de-n48-seed20260720"
    )


def test_post_cross_layer_with_persona_cohort_id(client):
    resp = client.post(
        "/api/events/cross-layer",
        json={
            "story_id": "sociome-cross-layer",
            "event_type": "discourse_fork_detected",
            "persona_cohort_id": "matraix-1m-eu-de-n48-seed20260720",
        },
    )
    assert resp.status_code == 200
    event = resp.json()["event"]
    assert event["persona_cohort_id"] == "matraix-1m-eu-de-n48-seed20260720"


def test_post_cross_layer_invalid_persona_cohort_id(client):
    resp = client.post(
        "/api/events/cross-layer",
        json={
            "story_id": "bad-cohort",
            "event_type": "discourse_fork_detected",
            "persona_cohort_id": "INVALID SLUG",
        },
    )
    assert resp.status_code == 422


def test_post_memetic_fork_with_persona_cohort_id(client):
    resp = client.post(
        "/api/events/memetic/fork",
        json={
            "parent_id": "root-sociome",
            "child_id": "fork-sociome",
            "persona_cohort_id": "eu-edu-strata-2026",
        },
    )
    assert resp.status_code == 200
    fork_event = resp.json()["fork_event"]
    assert fork_event["persona_cohort_id"] == "eu-edu-strata-2026"
    edges = resp.json()["graph"]["edges"]
    tagged = [e for e in edges if e.get("persona_cohort_id") == "eu-edu-strata-2026"]
    assert len(tagged) == 1


def test_post_memetic_market_coupling_with_persona_cohort_id(client):
    market = {
        "record_id": "ccxt:market_snapshot:sociome",
        "story_id": "sociome-market-story",
        "event_type": "fin_crypto_market_snapshot",
        "instrument": {"symbol": "BTC-USDT", "exchange_or_venue": "binance"},
        "signal": {"name": "last_price", "value": 65000.0},
    }
    with patch(
        "mas.memetic.market_coupling.fetch_market_snapshot",
        return_value=market,
    ):
        resp = client.post(
            "/api/events/memetic/market-coupling",
            json={
                "story_id": "sociome-market-story",
                "persona_cohort_id": "matraix-1m-eu-de-n48-seed20260720",
                "peak_velocity": 8.0,
                "market_record": market,
            },
        )
    assert resp.status_code == 200
    event = resp.json()["event"]
    assert event["persona_cohort_id"] == "matraix-1m-eu-de-n48-seed20260720"
