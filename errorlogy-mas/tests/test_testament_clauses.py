"""POSLEDNIY_ZAVET clause registry tests (Iteration 5)."""

import pytest
from fastapi.testclient import TestClient

from mas.memetic.discourse_graph import DiscourseGraph
from mas.memetic.testament_clauses import (
    CLAUSE_REGISTRY,
    clause_fork_metadata,
    format_testament_clause_ref,
    parse_testament_clause_ref,
    resolve_testament_clause_ref,
)


def test_registry_has_ten_clauses():
    assert set(CLAUSE_REGISTRY.keys()) == {
        "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"
    }


@pytest.mark.parametrize(
    "ref,expected_id",
    [
        ("POSLEDNIY_ZAVET:I", "I"),
        ("POSLEDNIY_ZAVET:IV", "IV"),
        ("POSLEDNIY_ZAVET:X", "X"),
    ],
)
def test_parse_testament_clause_ref_valid(ref, expected_id):
    assert parse_testament_clause_ref(ref) == expected_id


@pytest.mark.parametrize(
    "ref",
    [
        "POSLEDNIY_ZAVET:XI",
        "POSLEDNIY_ZAVET:1",
        "invalid",
    ],
)
def test_parse_testament_clause_ref_invalid(ref):
    with pytest.raises(ValueError, match="testament_clause_ref"):
        parse_testament_clause_ref(ref)


def test_clause_iv_metadata():
    meta = clause_fork_metadata("POSLEDNIY_ZAVET:IV")
    assert meta["testament_clause_ref"] == "POSLEDNIY_ZAVET:IV"
    assert meta["testament_clause_id"] == "IV"
    assert meta["testament_clause_label"] == "No accountability erasure"
    assert "institution:parliament" in meta["activated_layers"]
    assert "institution:audit" in meta["activated_layers"]
    assert meta["politifi_assets"] == ["institution:isa-2.0"]


def test_clause_ix_includes_ombudsman():
    clause = resolve_testament_clause_ref("POSLEDNIY_ZAVET:IX")
    assert "institution:ombudsman" in clause.activated_layers


def test_format_testament_clause_ref():
    assert format_testament_clause_ref("III") == "POSLEDNIY_ZAVET:III"


@pytest.fixture(autouse=True)
def reset_graph():
    import mas.memetic.discourse_graph as dg

    dg._graph_singleton = DiscourseGraph()
    yield
    dg._graph_singleton = None


@pytest.fixture
def client(tmp_path, monkeypatch):
    pytest.importorskip("itsdangerous")
    pytest.importorskip("authlib")
    monkeypatch.setattr("mas.db.DB_PATH", tmp_path / "testament_api.db")
    from mas.db import init_db
    from api.main import app

    init_db()
    return TestClient(app)


def test_api_memetic_fork_with_clause(client):
    resp = client.post(
        "/api/events/memetic/fork",
        json={
            "parent_id": "canon-root",
            "child_id": "fork-variant-a",
            "testament_clause_ref": "POSLEDNIY_ZAVET:IV",
            "persist_events": True,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    fork_event = body["fork_event"]
    assert fork_event["testament_clause_ref"] == "POSLEDNIY_ZAVET:IV"
    assert fork_event["epistemic_label"] == "INSTITUTIONAL_MODEL"
    assert "institution:audit" in fork_event["activated_layers"]
    assert fork_event["politifi_assets"] == ["institution:isa-2.0"]

    edges = body["graph"]["edges"]
    tagged = [e for e in edges if e.get("testament_clause_ref") == "POSLEDNIY_ZAVET:IV"]
    assert len(tagged) == 1
    assert tagged[0]["testament_clause_id"] == "IV"


def test_api_memetic_fork_rejects_bad_clause(client):
    resp = client.post(
        "/api/events/memetic/fork",
        json={
            "parent_id": "p1",
            "child_id": "c1",
            "testament_clause_ref": "POSLEDNIY_ZAVET:XI",
        },
    )
    assert resp.status_code == 422
