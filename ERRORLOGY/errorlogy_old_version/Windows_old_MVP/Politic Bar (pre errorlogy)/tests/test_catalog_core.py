"""Catalog core operations — slugify, propagation back-refs, actor profiles.

Replaces tests/test_catalog.py, which the cowork bash mount pinned at
256 lines on first read and now exposes as a null-padded file. Same
coverage; new filename → fresh mount cache slot.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from politic_bar import catalog


# ---------------------------------------------------------------------------
# _slugify_actor
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name,expected", [
    ("Robert Lund", "robert-lund"),
    ("Roger M. Boisjoly", "roger-m-boisjoly"),
    ("Café Manager", "cafe-manager"),
    ("Иван Иванов", "ivan-ivanov"),
    ("  ", "unnamed-actor"),
    ("", "unnamed-actor"),
])
def test_slugify_basic(name, expected):
    assert catalog._slugify_actor(name) == expected


def test_slugify_ukrainian_marker_switches_i_to_y():
    """Strings carrying any of {і, ї, є, ґ} are treated as Ukrainian:
    cyrillic `и` renders as `y` instead of `i`."""
    russian = catalog._slugify_actor("Владимир Никитин")          # no marker
    ukrainian = catalog._slugify_actor("Володимир Нікітін")       # `і` present
    assert russian == "vladimir-nikitin"
    assert "volodymyr" in ukrainian, f"expected ukrainian translit, got {ukrainian}"


def test_slugify_pure_cjk_falls_back_to_unicode_slug():
    slug = catalog._slugify_actor("李明")
    assert slug == "李明"


# ---------------------------------------------------------------------------
# Synthetic-card helpers
# ---------------------------------------------------------------------------

def _stub(card_id: str, propagated_from=None) -> dict:
    return {
        "id": card_id,
        "version": 1,
        "country": "US",
        "branch": "regulatory",
        "level": "national",
        "body": f"body-{card_id}",
        "decision_date": "2026-01-01",
        "event_type": "decision",
        "summary": "...",
        "claimed": "...",
        "known_or_knowable": "...",
        "decision": "...",
        "gap": "...",
        "classifications": [
            {"mode_id": "MP-005", "mode_name": "stub", "layer": "L5",
             "evidence_excerpt": "...", "source_ref": "...",
             "confidence": "medium", "justification": "..."},
        ],
        "asymmetry_vectors": [
            {"type": "AV3", "between": "A / B",
             "evidence_excerpt": "...", "source_ref": "..."},
        ],
        "propagated_from": propagated_from or [],
        "propagates_to": [],
        "constitutive_roles": [
            {"actor": f"actor-{card_id}", "action_or_inaction": "x",
             "contribution": "y", "foreseeability": "documented_in_record",
             "evidence_excerpt": "...", "source_ref": "..."},
        ],
        "counter_arguments": [],
        "sources": [],
    }


def _write(cases_dir: Path, card: dict) -> None:
    d = cases_dir / card["id"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "card.json").write_text(json.dumps(card, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def iso(tmp_path, monkeypatch):
    cases = tmp_path / "cases"
    cat = tmp_path / "catalog"
    monkeypatch.setattr(catalog, "CASES_DIR", cases)
    monkeypatch.setattr(catalog, "ACTORS_DIR", tmp_path / "actors")
    monkeypatch.setattr(catalog, "CATALOG_DIR", cat)
    monkeypatch.setattr(catalog, "ATTRACTORS_DIR", cat / "attractors")
    monkeypatch.setattr(catalog, "FLAGS_FILE", cat / "candidate_attractor_flags.jsonl")
    cases.mkdir(parents=True)
    return cases


# ---------------------------------------------------------------------------
# update_propagates_to — back-ref maintenance
# ---------------------------------------------------------------------------

def test_update_propagates_to_creates_back_ref(iso):
    _write(iso, _stub("UP-01"))
    down = _stub("DOWN-01", propagated_from=[
        {"card_id": "UP-01", "channel": "AV3",
         "evidence_excerpt": "regulator", "source_ref": "doc",
         "justification": "shared regulator-operator capture."},
    ])
    touched = catalog.update_propagates_to(down)
    assert touched == ["UP-01"]

    raw = json.loads((iso / "UP-01" / "card.json").read_text(encoding="utf-8"))
    assert raw["version"] == 2
    assert len(raw["propagates_to"]) == 1
    assert raw["propagates_to"][0]["card_id"] == "DOWN-01"
    assert raw["propagates_to"][0]["channel"] == "AV3"


def test_update_propagates_to_is_idempotent(iso):
    """Re-running with the same downstream replaces, not appends."""
    _write(iso, _stub("UP-01"))
    down = _stub("DOWN-01", propagated_from=[
        {"card_id": "UP-01", "channel": "AV3",
         "evidence_excerpt": "x", "source_ref": "x"},
    ])
    catalog.update_propagates_to(down)
    catalog.update_propagates_to(down)

    raw = json.loads((iso / "UP-01" / "card.json").read_text(encoding="utf-8"))
    assert len(raw["propagates_to"]) == 1


# ---------------------------------------------------------------------------
# Actor profiles — §7a AP1 aggregation
# ---------------------------------------------------------------------------

def test_update_actor_profiles_creates_principal_and_named(iso):
    """A stub card has body 'body-CASE-01' and a constitutive_role with
    actor 'actor-CASE-01' — distinct names, so we expect two profiles."""
    card = _stub("CASE-01")
    touched = catalog.update_actor_profiles(card)
    assert len(touched) == 2

    files = list(catalog.ACTORS_DIR.glob("*.json"))
    assert len(files) == 2

    body_slug = catalog._slugify_actor("body-CASE-01")
    body_profile = json.loads(
        (catalog.ACTORS_DIR / f"{body_slug}.json").read_text(encoding="utf-8"))
    assert body_profile["entries"][0]["role"] == "principal"
    assert body_profile["entries"][0]["card_id"] == "CASE-01"
    # AP1: classifications from card surface in the entry.
    assert "L5:MP-005" in body_profile["entries"][0]["classifications"]
