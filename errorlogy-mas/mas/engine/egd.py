"""Echo-room / small-group dynamics (TZ §9.8)."""

from __future__ import annotations

import numpy as np

from .. import taxonomy
from ..schemas.case import GovernanceCase
from ..schemas.analysis import EGDResult, ModeScore
from .guards import apply_mode_guards
from .types import EngineWarnings
from .wms_vocabulary import normalize_signal_type

_EGD_SIGNAL_WEIGHTS = {
    "WMS-003": 0.35,
    "WMS-011": 0.25,
    "WMS-013": 0.30,
    "WMS-012": 0.15,
    # legacy compat
    "expert_dissent_suppressed": 0.35,
    "bureaucratic_opacity": 0.25,
    "whistleblower_ignored": 0.30,
    "media_silence": 0.15,
}


def _egd_weight(signal_type: str) -> float:
    sid = normalize_signal_type(signal_type)
    if sid in _EGD_SIGNAL_WEIGHTS:
        return _EGD_SIGNAL_WEIGHTS[sid]
    return _EGD_SIGNAL_WEIGHTS.get(signal_type, 0.05)

_EGD_KEYWORDS = (
    "groupthink",
    "unanim",
    "dissent",
    "closed",
    "caucus",
    "management hat",
    "pressure",
    "echo",
)


def analyze(
    case: GovernanceCase,
    top_modes: list[ModeScore],
    warnings: EngineWarnings | None = None,
) -> EGDResult:
    text = f"{case.description} {case.source_text}".lower()

    echo_pressure = 0.0
    for s in case.weak_signals:
        echo_pressure += _egd_weight(s.signal_type) * s.strength
    for kw in _EGD_KEYWORDS:
        if kw in text:
            echo_pressure += 0.08
    for m in top_modes:
        if m.mode_id in ("CB-019", "CB-028", "CB-027"):
            echo_pressure += 0.12 * m.mu
    echo_pressure = float(np.clip(echo_pressure, 0.0, 1.0))

    hidden_prior = 0.0
    if "dissent" in text or "suppressed" in text or "overruled" in text:
        hidden_prior += 0.35
    if any(normalize_signal_type(s.signal_type) == "WMS-003" for s in case.weak_signals):
        hidden_prior += 0.4
    hidden_prior = float(np.clip(hidden_prior, 0.0, 1.0))

    egd_modes_raw: list[ModeScore] = []
    for m in top_modes:
        if not m.mode_id.startswith("CB-"):
            continue
        mode = taxonomy.get_mode(m.mode_id) or {}
        layer = mode.get("layer", "")
        if layer in ("L2", "L3") or m.mode_id in ("CB-019", "CB-028", "CB-027"):
            egd_modes_raw.append(m)

    likely = apply_mode_guards(egd_modes_raw[:4], warnings)

    return EGDResult(
        echo_room_pressure=round(echo_pressure, 4),
        hidden_signal_prior=round(hidden_prior, 4),
        likely_egd_modes=likely,
    )
