"""Bayesian log-odds fusion for weak multisource signals (TZ-H2-02 Tier A).

Fuses multiple WeakSignal observations that bear on the same early-warning cluster
before MSI aggregation.  Downstream μ remains a membership degree, not probability.

Formula (log-odds update with reliability weights):

    L0 = logit(p0)                     prior log-odds, p0 = 0.35 neutral baseline
    For observation i with strength s_i, reliability r_i, independence d_i,
    temporal relevance t_i:

        evidence_i = clip(s_i * r_i, ε, 1-ε)
        w_i = r_i * d_i * t_i
        ΔL_i = w_i * logit(evidence_i)

    Correlated observations (shared signal_type) share independence discount d_i.

    L_post = L0 + Σ ΔL_i
    fused_strength = sigmoid(L_post)

Reference: OSINT sensor fusion evidence hierarchy (Bayesian MAP tier).
"""

from __future__ import annotations

import math

import numpy as np

from ..schemas.case import WeakSignal
from .wms_vocabulary import normalize_signal_type

_PRIOR_P = 0.35
_EPS = 1e-6


def _logit(p: float) -> float:
    p = float(np.clip(p, _EPS, 1.0 - _EPS))
    return math.log(p / (1.0 - p))


def _sigmoid(x: float) -> float:
    return float(1.0 / (1.0 + math.exp(-x)))


def _independence(s: WeakSignal, all_signals: list[WeakSignal]) -> float:
    """Estimate source independence; lower when many signals share signal_type."""
    stype = normalize_signal_type(s.signal_type)
    same_type = sum(
        1 for o in all_signals if normalize_signal_type(o.signal_type) == stype
    ) - 1
    envs = {x.source_environment for x in all_signals if x.source_environment}
    env_factor = min(1.0, len(envs) / max(len(all_signals), 1)) if envs else 0.7
    type_factor = max(0.25, 1.0 - 0.2 * same_type)
    explicit = getattr(s, "independence", None)
    if explicit is not None:
        return float(np.clip(explicit * type_factor * env_factor, 0.1, 1.0))
    return float(np.clip(type_factor * env_factor, 0.1, 1.0))


def fuse_signals(signals: list[WeakSignal]) -> float:
    """Fuse ≥1 weak signals into a single posterior strength in [0, 1]."""
    if not signals:
        return 0.0

    l_post = _logit(_PRIOR_P)
    for s in signals:
        evidence = float(np.clip(s.strength * s.reliability, _EPS, 1.0 - _EPS))
        w = s.reliability * _independence(s, signals) * s.temporal_relevance
        l_post += w * _logit(evidence)

    return _sigmoid(l_post)


def fuse_by_cluster(signals: list[WeakSignal]) -> dict[str, float]:
    """Fuse signals grouped by normalized WMS signal_type (cluster key)."""
    buckets: dict[str, list[WeakSignal]] = {}
    for s in signals:
        key = normalize_signal_type(s.signal_type)
        buckets.setdefault(key, []).append(s)
    return {k: fuse_signals(v) for k, v in buckets.items()}
