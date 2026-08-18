"""End-to-end check on the canonical 4-card synthetic DAG fixture.

Verifies that loading tests/fixtures/synthetic_attractor_dag.json into
an isolated catalog reproduces the AT1+AT2+AT3 detection contract.
This is the regression anchor for §7b — if anyone touches the
attractor logic, this test catches drift on a fixture committed to git.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from politic_bar import catalog


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "synthetic_attractor_dag.json"


@pytest.fixture
def loaded(tmp_path, monkeypatch):
    cases = tmp_path / "cases"
    cat = tmp_path / "catalog"
    monkeypatch.setattr(catalog, "CASES_DIR", cases)
    monkeypatch.setattr(catalog, "ACTORS_DIR", tmp_path / "actors")
    monkeypatch.setattr(catalog, "CATALOG_DIR", cat)
    monkeypatch.setattr(catalog, "ATTRACTORS_DIR", cat / "attractors")
    monkeypatch.setattr(catalog, "FLAGS_FILE", cat / "candidate_attractor_flags.jsonl")

    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    cards = fixture["cards"]
    cases.mkdir(parents=True)
    for c in cards:
        d = cases / c["id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "card.json").write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
    # Wire back-refs so detect_attractor_component can walk both ways.
    for c in cards[1:]:
        catalog.update_propagates_to(c)

    return cards


def test_fixture_dag_emits_candidate_attractor_flag(loaded):
    terminal = loaded[-1]
    flag = catalog.detect_attractor_component(terminal, catalog=catalog.load_catalog())
    assert flag is not None
    assert set(flag.member_cards) == {"SYN-A-01", "SYN-B-01", "SYN-C-01", "SYN-D-01"}

    # AT2 hits on dominant L5 subtype OR AV — both are present in the fixture.
    l5 = {e["subtype"]: e["count"] for e in flag.dominant_l5_subtypes}
    av = {e["type"]: e["count"] for e in flag.dominant_asymmetry_vectors}
    assert l5.get("MP-005") == 4 or l5.get("L5c") == 4  # subtype field optional
    assert av.get("AV3") == 4

    # AT3: foreseeability profile majority is documented_in_record.
    profile = flag.foreseeability_profile
    assert profile.get("documented_in_record", 0) == 4


def test_fixture_flag_persisted_to_log(loaded):
    catalog.detect_attractor_component(loaded[-1], catalog=catalog.load_catalog())
    log_path = catalog.FLAGS_FILE
    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["flagged_by_card"] == "SYN-D-01"
