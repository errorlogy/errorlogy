"""Weak Multisource Signals detector (TZ §9.6)."""

from __future__ import annotations

import numpy as np

from ..schemas.case import GovernanceCase, WeakSignal
from ..schemas.analysis import WMSResult
from .bayesian_fusion import fuse_signals
from .wms_vocabulary import normalize_signal_type, normalize_weak_signal

CEP_DECAY = 0.85
MAX_ENVIRONMENTS = 12


def _signal_contribution(s: WeakSignal, all_signals: list[WeakSignal]) -> float:
    independence = 1.0
    stype = normalize_signal_type(s.signal_type)
    if len(all_signals) > 1:
        same_type = sum(
            1 for o in all_signals if normalize_signal_type(o.signal_type) == stype
        ) - 1
        independence = max(0.3, 1.0 - 0.15 * same_type)
    diversity_factor = 1.0
    envs = {x.source_environment for x in all_signals if x.source_environment}
    if envs:
        diversity_factor = min(1.0, len(envs) / MAX_ENVIRONMENTS)
    raw = (
        s.reliability * s.strength * independence * diversity_factor * s.temporal_relevance
    )
    return raw


def compute_msi(signals: list[WeakSignal]) -> float:
    if not signals:
        return 0.0
    if len(signals) >= 2:
        fused = fuse_signals(signals)
        envs = {x.source_environment for x in signals if x.source_environment}
        env_bonus = 0.08 * max(0, len(envs) - 1)
        effective = min(1.0, fused + env_bonus)
        return float(1.0 / (1.0 + np.exp(-3.0 * (effective - 0.35))))
    total = sum(_signal_contribution(s, signals) for s in signals)
    return float(1.0 / (1.0 + np.exp(-3.0 * (total / max(len(signals), 1) - 0.35))))


def compute_cep(msi: float, prev_cep: float = 0.0) -> float:
    return float(np.clip(CEP_DECAY * prev_cep + msi, 0.0, 1.0))


def detect(case: GovernanceCase, prev_cep: float = 0.0) -> WMSResult:
    signals = [normalize_weak_signal(s) for s in case.weak_signals]
    msi = compute_msi(signals)
    cep = compute_cep(msi, prev_cep)
    active = [normalize_signal_type(s.signal_type) for s in signals if s.strength > 0.3]

    if cep > 0.65:
        hypothesis = (
            "Early-warning hypothesis: cumulative error pressure is elevated; "
            "multiple weak signals may be compounding toward escalation if unaddressed."
        )
    elif msi > 0.4:
        hypothesis = (
            "Early-warning hypothesis: multisource signal index suggests "
            "analytical attention to weak but consistent warning patterns."
        )
    else:
        hypothesis = (
            "Early-warning hypothesis: limited weak-signal accumulation detected; "
            "monitoring remains advisable under uncertainty."
        )

    return WMSResult(
        msi=round(msi, 4),
        cep=round(cep, 4),
        active_signals=active,
        early_warning_hypothesis=hypothesis,
    )
