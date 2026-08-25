"""Cross-layer institutional event stub tests."""

import pytest
from fastapi.testclient import TestClient

from mas.db import init_db, save_cross_layer_event, list_cross_layer_events, get_cross_layer_event
from mas.institutional.activation import (
    INSTITUTION_LAYER_IDS,
    default_activated_layers,
    frame_cross_layer_event,
)


@pytest.fixture
def client(tmp_path, monkeypatch):
    pytest.importorskip("itsdangerous")
    pytest.importorskip("authlib")
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "cle_api.db")
    init_db()
    from api.main import app

    return TestClient(app)


def test_institution_layers_enum():
    assert len(INSTITUTION_LAYER_IDS) >= 19
    assert "institution:parliament" in INSTITUTION_LAYER_IDS


def test_api_layers_endpoint(client):
    resp = client.get("/api/events/cross-layer/layers")
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == len(INSTITUTION_LAYER_IDS)
    assert set(body["layers"]) == INSTITUTION_LAYER_IDS


def test_api_post_and_list_cross_layer(client):
    resp = client.post(
        "/api/events/cross-layer",
        json={"story_id": "api-test", "event_type": "gov_legislative_document"},
    )
    assert resp.status_code == 200
    event = resp.json()["event"]
    assert event["story_id"] == "api-test"
    assert event["epistemic_label"] == "INSTITUTIONAL_MODEL"

    listed = client.get("/api/events/cross-layer", params={"story_id": "api-test"})
    assert listed.status_code == 200
    assert listed.json()["count"] >= 1


def test_default_layers_fin_crypto():
    layers = default_activated_layers("fin_crypto_market_snapshot")
    assert "institution:central-bank-analog" in layers
    assert len(layers) >= 1


def test_frame_fills_layers_and_label():
    framed = frame_cross_layer_event(
        {
            "story_id": "  test-story  ",
            "event_type": "gov_legislative_document",
            "extra_ignored": True,
        }
    )
    assert "extra_ignored" not in framed
    assert framed["story_id"] == "test-story"
    assert framed["epistemic_label"] == "INSTITUTIONAL_MODEL"
    assert len(framed["activated_layers"]) >= 1
    assert "institution:parliament" in framed["activated_layers"]


def test_frame_rejects_invalid_layer():
    try:
        frame_cross_layer_event(
            {
                "story_id": "s",
                "event_type": "bilateral_summit",
                "activated_layers": ["institution:not-a-real-layer"],
            }
        )
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "invalid activated_layers" in str(exc)


def test_persist_cross_layer(tmp_path, monkeypatch):
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "cle.db")
    init_db()
    framed = frame_cross_layer_event(
        {"story_id": "s1", "event_type": "fin_crypto_market_snapshot"}
    )
    stored = save_cross_layer_event("cle-test1", framed)
    assert stored["event_id"] == "cle-test1"
    listed = list_cross_layer_events(limit=10, story_id="s1")
    assert len(listed) == 1
    one = get_cross_layer_event("cle-test1")
    assert one is not None
    assert one["event_type"] == "fin_crypto_market_snapshot"
