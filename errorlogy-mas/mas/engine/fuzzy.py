"""Fuzzy membership scoring (TZ §9.3)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .. import taxonomy
from ..schemas.case import GovernanceCase
from ..schemas.analysis import ModeScore
from .embeddings import semantic_similarity
from .guards import apply_mode_guards
from .types import EngineWarnings, FuzzyContext
from .wms_vocabulary import normalize_signal_type

_WEIGHTS_PATH = Path(__file__).parent.parent.parent / "data" / "fuzzy_weights.json"
DEFAULT_WEIGHTS = {"dimension": 0.35, "keyword": 0.25, "signal": 0.20, "layer": 0.10, "boost": 0.10}
_WEIGHTS: dict[str, float] = dict(DEFAULT_WEIGHTS)
_SIGNAL_TYPES = {
    "bureaucratic_opacity",
    "expert_dissent_suppressed",
    "regulatory_capture",
    "metric_gaming",
    "schedule_pressure",
    "cost_overrun",
    "inter_agency_conflict",
    "legal_ambiguity",
    "media_silence",
    "whistleblower_ignored",
}


def get_weights() -> dict[str, float]:
    return dict(_WEIGHTS)


def set_weights(weights: dict[str, float]) -> None:
    global _WEIGHTS
    total = sum(weights.values()) or 1.0
    _WEIGHTS = {k: float(v) / total for k, v in weights.items()}


def load_calibrated_weights() -> bool:
    """Load weights from data/fuzzy_weights.json if present."""
    if not _WEIGHTS_PATH.exists():
        return False
    try:
        data = json.loads(_WEIGHTS_PATH.read_text(encoding="utf-8"))
        w = data.get("weights", data)
        if isinstance(w, dict) and "dimension" in w:
            set_weights(w)
            return True
    except Exception:
        pass
    return False


def save_weights(path: Path | None = None, *, version: str = "calibrated") -> None:
    target = path or _WEIGHTS_PATH
    target.write_text(
        json.dumps({"version": version, "weights": get_weights()}, indent=2),
        encoding="utf-8",
    )


load_calibrated_weights()


def _case_text(case: GovernanceCase) -> str:
    return f"{case.title} {case.description} {case.source_text}"


def _dimension_match(mode: dict, case_text: str) -> float:
    dims = mode.get("meta_dimensions", [])
    if not dims:
        return 0.3
    text = case_text.lower()
    hits = 0
    dim_keywords = {
        "R": ["distort", "filter", "compress", "incomplete", "bias", "signal"],
        "O": ["incentive", "objective", "mandate", "rent", "career"],
        "A": ["aggregat", "vote", "consensus", "committee", "group"],
        "C": ["jurisdiction", "coordination", "veto", "deadlock", "conflict"],
        "T": ["delay", "timeline", "schedule", "temporal", "short-term"],
        "X": ["polariz", "diverg", "echo", "dissent", "unanim"],
    }
    for d in dims:
        kws = dim_keywords.get(d, [])
        if any(k in text for k in kws):
            hits += 1
    return min(1.0, hits / max(len(dims), 1))


def _keyword_match(mode: dict, case_text: str) -> float:
    mode_id = mode.get("id", "")
    overlap = taxonomy.keyword_overlap(mode_id, case_text)

    emb_sim = semantic_similarity(mode, case_text)
    if emb_sim is not None:
        return float(np.clip(0.35 * overlap + 0.65 * emb_sim, 0.0, 1.0))

    signal = mode.get("operational_signal") or mode.get("government_decision_cue") or mode.get("definition", "")
    if not signal.strip():
        return overlap
    try:
        vec = TfidfVectorizer(stop_words="english", max_features=500)
        mat = vec.fit_transform([case_text, signal])
        sim = float(cosine_similarity(mat[0:1], mat[1:2])[0, 0])
        return 0.5 * overlap + 0.5 * max(0.0, sim)
    except ValueError:
        return overlap


def _signal_present(mode: dict, case: GovernanceCase) -> float:
    text = _case_text(case).lower()
    active = {normalize_signal_type(s.signal_type) for s in case.weak_signals if s.strength > 0.3}
    if not active:
        return 0.2
    mode_text = (mode.get("operational_signal") or mode.get("definition") or "").lower()
    score = 0.0
    for st in active:
        if st.startswith("WMS-") and st != "WMS-UNK":
            score += 0.25
        elif st.replace("_", " ") in mode_text or st in _SIGNAL_TYPES:
            score += 0.25
    wms_active = {st for st in active if st.startswith("WMS-") and st != "WMS-UNK"}
    return min(1.0, score + 0.1 * len(wms_active))


def _boost(mode: dict, ctx: FuzzyContext) -> float:
    b = 0.0
    if ctx.wms_msi > 0.5:
        b += 0.03
    if ctx.t4d_latency_risk > 0.5:
        b += 0.03
    if ctx.cat_bifurcation_risk > 0.5:
        b += 0.04
    return min(0.15, b)


def score_mode_components(mode: dict, case: GovernanceCase, ctx: FuzzyContext) -> dict[str, float]:
    text = _case_text(case)
    layer = mode.get("layer", "L1")
    w = get_weights()
    return {
        "dimension": _dimension_match(mode, text),
        "keyword": _keyword_match(mode, text),
        "signal": _signal_present(mode, case),
        "layer": taxonomy.get_layer_prior(layer),
        "boost": _boost(mode, ctx),
        "weights": w,
    }


def score_mode(mode: dict, case: GovernanceCase, ctx: FuzzyContext) -> float:
    c = score_mode_components(mode, case, ctx)
    w = c["weights"]
    mu = (
        w["dimension"] * c["dimension"]
        + w["keyword"] * c["keyword"]
        + w["signal"] * c["signal"]
        + w["layer"] * c["layer"]
        + w["boost"] * c["boost"]
    )
    return float(np.clip(mu, 0.0, 1.0))


def _evidence_grade(mu: float, keyword: float) -> str:
    if mu >= 0.55 and keyword >= 0.35:
        return "strong"
    if mu >= 0.35:
        return "moderate"
    return "weak"


def _confidence(mu: float, keyword: float) -> float:
    return float(np.clip(0.4 + 0.4 * mu + 0.2 * keyword, 0.0, 1.0))


def score_candidates(
    case: GovernanceCase,
    top_n: int = 20,
    ctx: FuzzyContext | None = None,
    warnings: EngineWarnings | None = None,
) -> list[ModeScore]:
    ctx = ctx or FuzzyContext()
    text = _case_text(case)

    candidates: list[dict] = list(taxonomy.get_all_atomic_modes())
    universe = taxonomy.get_max_mode_universe()
    atomic_ids = {m["id"] for m in candidates}

    # Pre-filter universe by keyword overlap (top 100 not already atomic)
    universe_scored = []
    for m in universe:
        mid = m.get("id", "")
        if mid in atomic_ids:
            continue
        universe_scored.append((taxonomy.keyword_overlap(mid, text), m))
    universe_scored.sort(key=lambda x: -x[0])
    for _, m in universe_scored[:100]:
        candidates.append(m)

    scored: list[ModeScore] = []
    for mode in candidates:
        mid = mode.get("id")
        if not mid:
            continue
        kw = _keyword_match(mode, text)
        mu = score_mode(mode, case, ctx)
        if mu < 0.05 and kw < 0.05:
            continue
        scored.append(
            ModeScore(
                mode_id=mid,
                name=taxonomy.get_mode_name(mid),
                mu=round(mu, 4),
                confidence=round(_confidence(mu, kw), 3),
                evidence_grade=_evidence_grade(mu, kw),
                contributing_signals=[s.signal_type for s in case.weak_signals if s.strength > 0.3][:5],
            )
        )

    scored.sort(key=lambda m: -m.mu)
    return apply_mode_guards(scored[:top_n], warnings)
