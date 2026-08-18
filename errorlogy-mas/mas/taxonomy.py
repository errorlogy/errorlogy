import json
import re
from functools import lru_cache
from typing import Any

from .config import TAXONOMY_PATH

_MODE_INDEX: dict[str, dict] | None = None
_KEYWORD_INDEX: dict[str, set[str]] | None = None


@lru_cache(maxsize=1)
def load() -> dict[str, Any]:
    with open(TAXONOMY_PATH, encoding="utf-8") as f:
        data = json.load(f)
    _validate(data)
    _build_indexes(data)
    return data


def _validate(data: dict) -> None:
    assert "max_mode_universe" in data or "atomic_modes" in data, "No modes found"
    ids = [m["id"] for m in data.get("atomic_modes", [])]
    assert len(ids) == len(set(ids)), "Duplicate mode IDs"


def _tokenize(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[a-zA-Z]{3,}", text or "")}


def _build_indexes(data: dict) -> None:
    global _MODE_INDEX, _KEYWORD_INDEX
    _MODE_INDEX = {}
    _KEYWORD_INDEX = {}

    def _register(mode: dict) -> None:
        mid = mode.get("id")
        if not mid:
            return
        _MODE_INDEX[mid] = mode
        text = " ".join(
            str(mode.get(k, ""))
            for k in ("name", "definition", "operational_signal", "government_decision_cue", "description")
        )
        _KEYWORD_INDEX[mid] = _tokenize(text)

    for m in data.get("atomic_modes", []):
        _register(m)
    for m in data.get("max_mode_universe", []):
        if m.get("id") not in _MODE_INDEX:
            _register(m)

    _precompute_embeddings(data)


def _precompute_embeddings(data: dict) -> None:
    try:
        from .engine.embeddings import precompute_modes
        atomic = data.get("atomic_modes", [])
        n = precompute_modes(atomic)
        if n:
            import logging
            logging.getLogger("errorlogy").debug("Precomputed %d mode embeddings", n)
    except Exception:
        pass


def get_mode_index() -> dict[str, dict]:
    load()
    assert _MODE_INDEX is not None
    return _MODE_INDEX


def get_mode(mode_id: str) -> dict | None:
    return get_mode_index().get(mode_id)


def get_mode_name(mode_id: str) -> str:
    m = get_mode(mode_id)
    return m.get("name", mode_id) if m else mode_id


def get_modes_by_family(family: str) -> list[dict]:
    return [m for m in load().get("atomic_modes", []) if m.get("family") == family]


def get_all_atomic_modes() -> list[dict]:
    return list(load().get("atomic_modes", []))


def get_max_mode_universe() -> list[dict]:
    return list(load().get("max_mode_universe", []))


def get_layer_prior(layer: str) -> float:
    priors = {"L1": 0.15, "L2": 0.12, "L3": 0.10, "L4": 0.12, "L5": 0.10, "L6": 0.08}
    return priors.get(layer, 0.05)


def keyword_overlap(mode_id: str, case_text: str) -> float:
    load()
    assert _KEYWORD_INDEX is not None
    mode_kw = _KEYWORD_INDEX.get(mode_id, set())
    if not mode_kw:
        return 0.0
    case_kw = _tokenize(case_text)
    if not case_kw:
        return 0.0
    return len(mode_kw & case_kw) / max(len(mode_kw), 1)


def get_alpha_edges() -> list[dict]:
    data = load()
    seen: set[tuple] = set()
    edges: list[dict] = []

    def _add(e: dict) -> None:
        if not (isinstance(e, dict) and "from" in e and "to" in e):
            return
        key = (e["from"], e["to"])
        if key not in seen:
            seen.add(key)
            edges.append(e)

    for e in data.get("alpha_matrix_max_seed", {}).get("edges", []):
        _add(e)
    for e in data.get("alpha_matrix_spec", {}).get("initial_edges", []):
        _add(e)
    sm = data.get("social_media_layer") or data.get("SOCIAL_MEDIA") or {}
    if isinstance(sm, dict):
        for e in sm.get("integration", {}).get("alpha_examples", []):
            _add(e)

    for section in data.values():
        if isinstance(section, dict):
            e = section.get("alpha_edge_estimate")
            if e:
                _add(e)
        elif isinstance(section, list):
            for item in section:
                if isinstance(item, dict):
                    e = item.get("alpha_edge_estimate")
                    if e:
                        _add(e)

    return edges


def get_alpha_graph():
    import networkx as nx

    g = nx.DiGraph()
    for e in get_alpha_edges():
        g.add_edge(
            e["from"],
            e["to"],
            weight=float(e.get("weight", 0.0)),
            confidence=float(e.get("confidence", 1.0)),
        )
    return g


def get_layers() -> dict[str, str]:
    return load().get("layers", {})


def get_meta_dimensions() -> dict[str, str]:
    return load().get("meta_dimensions", {})


def get_pno_modes() -> list[dict]:
    return load().get("composite_patterns", {}).get("PNO", [])


def get_acc_archetypes() -> list[dict]:
    data = load()
    layer = data.get("agent_contour_contribution_cluster_layer", {})
    archetypes = layer.get("cluster_archetypes", [])
    if archetypes:
        return archetypes
    acc = data.get("ACC", {})
    return acc.get("cluster_archetypes", [])


def get_cat_modes() -> list[dict]:
    layer = load().get("catastrophe_theory_layer", {})
    return layer.get("modes", [])


def get_egd_modes() -> list[dict]:
    layer = load().get("echo_room_group_dynamics_layer", {})
    return layer.get("modes", [])


def get_wms_signal_types() -> list[str]:
    layer = load().get("weak_multisource_signal_layer", {})
    types = layer.get("signal_types", [])
    if types and isinstance(types[0], dict):
        return [t.get("id", t.get("name", "")) for t in types]
    return types if isinstance(types, list) else []


def get_wms_signal_defs() -> list[dict]:
    layer = load().get("weak_multisource_signal_layer", {})
    return list(layer.get("signal_types", []))


def get_wms_source_environments() -> list[str]:
    layer = load().get("weak_multisource_signal_layer", {})
    return list(layer.get("source_environments", []))


def summary() -> dict:
    return load().get("counts", {})
