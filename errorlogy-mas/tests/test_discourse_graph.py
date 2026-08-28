"""Discourse graph scaffold tests (Phase B memetic runtime)."""

import pytest
from fastapi.testclient import TestClient

from mas.memetic.discourse_graph import (
    DiscourseGraph,
    build_discourse_fork_detected_event,
    build_narrative_lineage_update_event,
    get_discourse_graph,
)


@pytest.fixture(autouse=True)
def reset_graph():
    import mas.memetic.discourse_graph as dg

    dg._graph_singleton = DiscourseGraph()
    yield
    dg._graph_singleton = None


def test_add_story_node_and_fork_edge():
    g = DiscourseGraph()
    g.add_story_node("story-a", label="root")
    g.add_fork_edge("story-a", "story-b", edge_type="narrative_fork")
    assert g.get_lineage("story-b") == ["story-a", "story-b"]


def test_symbolic_variant_edge():
    """symbolic_variant tracks media-carrier forks; API accepts edge_type on POST /memetic/fork."""
    g = DiscourseGraph()
    g.add_story_node("carrier-root", carrier="broadcast")
    g.add_fork_edge(
        "carrier-root",
        "carrier-tv",
        edge_type="symbolic_variant",
        carrier="television",
    )
    g.add_fork_edge(
        "carrier-root",
        "carrier-social",
        edge_type="symbolic_variant",
        carrier="social_media",
    )
    assert g.get_lineage("carrier-tv") == ["carrier-root", "carrier-tv"]
    edges = g.to_dict()["edges"]
    symbolic = [e for e in edges if e.get("edge_type") == "symbolic_variant"]
    assert len(symbolic) == 2
    assert symbolic[0]["carrier"] in ("television", "social_media")


def test_detect_fork():
    g = DiscourseGraph()
    g.add_story_node("parent")
    assert g.detect_fork("child", "parent") is True
    assert g.detect_fork("parent", "parent") is False
    assert g.detect_fork("child", "missing") is False


def test_build_discourse_fork_event():
    event = build_discourse_fork_detected_event("child-1", parent_id="parent-1")
    assert event["event_type"] == "discourse_fork_detected"
    assert event["story_id"] == "child-1"
    assert event["epistemic_label"] == "INSTITUTIONAL_MODEL"
    assert "institution:judiciary" in event["activated_layers"]
    assert event["fork"]["parent_id"] == "parent-1"


def test_build_lineage_update_event():
    event = build_narrative_lineage_update_event("leaf", ["root", "leaf"])
    assert event["event_type"] == "narrative_lineage_update"
    assert event["lineage"] == ["root", "leaf"]


@pytest.fixture
def client(tmp_path, monkeypatch):
    pytest.importorskip("itsdangerous")
    pytest.importorskip("authlib")
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "memetic_api.db")
    from mas.db import init_db
    from api.main import app

    init_db()
    return TestClient(app)


def test_api_memetic_endpoints(client):
    resp = client.post(
        "/api/events/memetic/fork",
        json={"parent_id": "p1", "child_id": "c1"},
    )
    assert resp.status_code == 200
    assert resp.json()["lineage"] == ["p1", "c1"]

    resp2 = client.get("/api/events/memetic/lineage/c1")
    assert resp2.status_code == 200
    assert resp2.json()["lineage"] == ["p1", "c1"]

    resp3 = client.post(
        "/api/events/memetic/fork",
        json={
            "parent_id": "p1",
            "child_id": "c2",
            "edge_type": "symbolic_variant",
            "persist_events": False,
        },
    )
    assert resp3.status_code == 200
    graph_edges = resp3.json()["graph"]["edges"]
    assert any(
        e["child"] == "c2" and e.get("edge_type") == "symbolic_variant"
        for e in graph_edges
    )
