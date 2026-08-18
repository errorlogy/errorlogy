"""§7b attractor-component detection on a synthetic DAG.

Split out from test_catalog.py because the cowork bash mount pinned that
file's size at first read and refused to grow — see
feedback_cowork_mount_cache_bug. New filename = clean cache slot.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from politic_bar import catalog


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


def _build_chain(cases_dir, n: int) -> list[dict]:
    """A→B→...→N — each card propagated_from its predecessor by AV3."""
    cards = [_stub("CARD-01")]
    for i in range(2, n + 1):
        prev = f"CARD-{i-1:02d}"
        cards.append(_stub(f"CARD-{i:02d}", propagated_from=[
            {"card_id": prev, "channel": "AV3",
             "evidence_excerpt": "x", "source_ref": "x"},
        ]))
    for c in cards:
        _write(cases_dir, c)
    for c in cards[1:]:
        catalog.update_propagates_to(c)
    return cards


def test_emits_flag_when_AT2_AT3_met(iso):
    cards = _build_chain(iso, 4)
    flag = catalog.detect_attractor_component(cards[-1], catalog=catalog.load_catalog())

    assert flag is not None, "AT1+AT2+AT3 met on 4-card chain — flag expected"
    assert set(flag.member_cards) == {f"CARD-{i:02d}" for i in range(1, 5)}
    assert flag.flagged_by_card == "CARD-04"
    assert catalog.FLAGS_FILE.exists()
    lines = catalog.FLAGS_FILE.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1


def test_below_threshold_returns_none(iso):
    cards = _build_chain(iso, 3)  # 3 < ATTRACTOR_MIN_MEMBERS (4)
    flag = catalog.detect_attractor_component(cards[-1], catalog=catalog.load_catalog())
    assert flag is None


def test_existing_attractor_suppresses_reflag(iso):
    cards = _build_chain(iso, 4)
    catalog.ATTRACTORS_DIR.mkdir(parents=True, exist_ok=True)
    (catalog.ATTRACTORS_DIR / "ATR-001.json").write_text(
        json.dumps({"attractor_id": "ATR-001",
                    "member_cards": [f"CARD-{i:02d}" for i in range(1, 5)]},
                   ensure_ascii=False),
        encoding="utf-8",
    )
    flag = catalog.detect_attractor_component(cards[-1], catalog=catalog.load_catalog())
    assert flag is None, "existing attractor must short-circuit re-flag"
