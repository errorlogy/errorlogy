"""PNO system regime scoring (TZ §9.5)."""

from __future__ import annotations

import numpy as np

from .. import taxonomy
from ..schemas.analysis import ModeScore, PNOResult

# Map PNO composite IDs to agent-facing PNO-1..7 keys
PNO_KEYS = [f"PNO-{i}" for i in range(1, 8)]


def display_pno_id(pid: str) -> str:
    """Normalize taxonomy PNO-001 and display PNO-1 to canonical PNO-1..7."""
    if not pid.startswith("PNO-"):
        return pid
    try:
        return f"PNO-{int(pid.split('-')[-1])}"
    except ValueError:
        return pid


def taxonomy_pno_id(display_id: str) -> str:
    """Map display PNO-1..7 to taxonomy PNO-001..007."""
    if not display_id.startswith("PNO-"):
        return display_id
    try:
        return f"PNO-{int(display_id.split('-')[-1]):03d}"
    except ValueError:
        return display_id


def _pno_num(pid: str) -> int:
    try:
        return int(pid.split("-")[-1])
    except ValueError:
        return -1


def score_pno(top_modes: list[ModeScore], propagated_mu: dict[str, float] | None = None) -> PNOResult:
    propagated_mu = propagated_mu or {m.mode_id: m.mu for m in top_modes}
    scores = {k: 0.0 for k in PNO_KEYS}
    pno_defs = taxonomy.get_pno_modes()

    # Score from composite PNO definitions in taxonomy
    for i, pno in enumerate(pno_defs[:7]):
        key = PNO_KEYS[i] if i < 7 else f"PNO-{i+1}"
        components = pno.get("components", {})
        comp_mu: list[float] = []
        for family, ids in components.items():
            for mid in ids:
                comp_mu.append(propagated_mu.get(mid, 0.0))
        if comp_mu:
            scores[key] = float(np.mean(comp_mu))

    # Boost from top activated modes by family
    for m in top_modes:
        mode = taxonomy.get_mode(m.mode_id) or {}
        family = mode.get("family", "CB")
        layer = mode.get("layer", "L1")
        idx_map = {"L1": 0, "L2": 4, "L3": 0, "L4": 1, "L5": 2, "L6": 6}
        idx = idx_map.get(layer, 0)
        key = PNO_KEYS[min(idx, 6)]
        scores[key] += 0.15 * m.mu

    # Normalize to [0,1]
    max_s = max(scores.values()) if scores else 1.0
    if max_s > 0:
        scores = {k: round(v / max_s, 4) for k, v in scores.items()}

    dominant = display_pno_id(max(scores, key=scores.get))
    dominant_num = _pno_num(dominant)
    pno_name = ""
    tax_id = taxonomy_pno_id(dominant)
    for p in pno_defs:
        if p.get("id", "") == tax_id or _pno_num(p.get("id", "")) == dominant_num:
            pno_name = p.get("name", "")
            break

    explanation = (
        f"Analytical regime {dominant} scores highest ({scores[dominant]:.2f}). "
        f"{pno_name or 'Persistent non-optimality pattern'} "
        "is consistent with the activated mode profile — hypothesis only, not a legal finding."
    )

    return PNOResult(dominant_pno=dominant, scores=scores, explanation=explanation)
