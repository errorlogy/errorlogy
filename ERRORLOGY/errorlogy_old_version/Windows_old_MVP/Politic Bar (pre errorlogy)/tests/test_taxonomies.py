"""Taxonomy structural tests (METHODOLOGY v0.6).

Verifies that all three taxonomies load, contain unique IDs, and that
subtypes/categories declared at the top of each file are referenced
consistently by their entries. Pure data tests — no LLM, no I/O outside
the taxonomy files.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAX_DIR = ROOT / "taxonomy"


# ---------------------------------------------------------------------------
# Cognitive biases — L1/L2/L3
# ---------------------------------------------------------------------------

def test_cognitive_biases_loads_and_has_unique_ids():
    data = json.loads((TAX_DIR / "cognitive_biases.json").read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert "biases" in data
    biases = data["biases"]
    assert len(biases) >= 180, f"v0.6 README claims 189 biases; got {len(biases)}"

    ids = [b["id"] for b in biases]
    assert len(ids) == len(set(ids)), "duplicate CB-IDs in cognitive_biases.json"

    cb_pattern = re.compile(r"^CB-\d{3}$")
    for b in biases:
        assert cb_pattern.match(b["id"]), f"non-canonical id: {b['id']}"
        assert b.get("name"), f"{b['id']} missing name"
        assert b.get("definition"), f"{b['id']} missing definition"
        assert b.get("category"), f"{b['id']} missing category"


def test_cognitive_biases_categories_are_referenced():
    data = json.loads((TAX_DIR / "cognitive_biases.json").read_text(encoding="utf-8"))
    declared = set(data.get("categories", {}).keys())
    used = {b["category"] for b in data["biases"]}
    unknown = used - declared
    assert not unknown, f"biases reference undeclared categories: {sorted(unknown)}"


# ---------------------------------------------------------------------------
# Strategic failure modes — L4
# ---------------------------------------------------------------------------

def test_strategic_failure_modes_structure():
    data = json.loads((TAX_DIR / "strategic_failure_modes.json").read_text(encoding="utf-8"))
    modes = data["modes"]
    assert len(modes) == 14, f"§5c v0.6 documents 14 SF modes; got {len(modes)}"

    ids = [m["id"] for m in modes]
    assert len(ids) == len(set(ids)), "duplicate SF-IDs"

    declared_subtypes = set(data["subtypes"].keys())
    # v0.4 reserves L4a/L4d/L4f; the 5 active subtypes in v0.6 are L4b, L4c, L4e, L4g, L4h.
    assert declared_subtypes == {"L4b", "L4c", "L4e", "L4g", "L4h"}, (
        f"unexpected L4 subtype set: {declared_subtypes}"
    )

    sf_pattern = re.compile(r"^SF-\d{3}$")
    for m in modes:
        assert sf_pattern.match(m["id"]), f"non-canonical id: {m['id']}"
        assert m["subtype"] in declared_subtypes, (
            f"{m['id']} uses undeclared subtype {m['subtype']}"
        )
        assert m.get("definition"), f"{m['id']} missing definition"
        assert m.get("operational_signature"), f"{m['id']} missing operational_signature"


# ---------------------------------------------------------------------------
# Mechanism pathologies — L5
# ---------------------------------------------------------------------------

def test_mechanism_pathologies_structure():
    data = json.loads((TAX_DIR / "mechanism_pathologies.json").read_text(encoding="utf-8"))
    modes = data["modes"]
    assert len(modes) == 14, f"§5d v0.6 documents 14 MP modes; got {len(modes)}"

    ids = [m["id"] for m in modes]
    assert len(ids) == len(set(ids)), "duplicate MP-IDs"

    declared_subtypes = set(data["subtypes"].keys())
    # §5d v0.6 names L5a through L5h.
    assert declared_subtypes == {f"L5{c}" for c in "abcdefgh"}, (
        f"unexpected L5 subtype set: {declared_subtypes}"
    )

    mp_pattern = re.compile(r"^MP-\d{3}$")
    for m in modes:
        assert mp_pattern.match(m["id"]), f"non-canonical id: {m['id']}"
        assert m["subtype"] in declared_subtypes, (
            f"{m['id']} uses undeclared subtype {m['subtype']}"
        )
        assert m.get("definition"), f"{m['id']} missing definition"
        assert m.get("operational_signature"), f"{m['id']} missing operational_signature"


# ---------------------------------------------------------------------------
# Cross-taxonomy: every mode_id used by a published card resolves
# ---------------------------------------------------------------------------

def test_all_mode_id_namespaces_disjoint():
    """CB-, SF-, MP- prefixes must not collide. The pipeline relies on the
    prefix to route a classification to its taxonomy."""
    cb = json.loads((TAX_DIR / "cognitive_biases.json").read_text(encoding="utf-8"))
    sf = json.loads((TAX_DIR / "strategic_failure_modes.json").read_text(encoding="utf-8"))
    mp = json.loads((TAX_DIR / "mechanism_pathologies.json").read_text(encoding="utf-8"))

    cb_ids = {b["id"] for b in cb["biases"]}
    sf_ids = {m["id"] for m in sf["modes"]}
    mp_ids = {m["id"] for m in mp["modes"]}

    assert cb_ids.isdisjoint(sf_ids)
    assert cb_ids.isdisjoint(mp_ids)
    assert sf_ids.isdisjoint(mp_ids)
