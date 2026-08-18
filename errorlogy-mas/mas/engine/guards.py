"""Post-processing quality gates for engine outputs."""

from __future__ import annotations

from .. import taxonomy
from ..schemas.analysis import ModeScore
from .types import EngineWarnings

WEAK_MU_CAP = 0.65
LOW_CONFIDENCE_THRESHOLD = 0.4

_GRADE_TO_CONFIDENCE = {"weak": 0.35, "moderate": 0.6, "strong": 0.85}


def apply_mode_guards(
    modes: list[ModeScore],
    warnings: EngineWarnings | None = None,
) -> list[ModeScore]:
    out: list[ModeScore] = []
    for m in modes:
        name = taxonomy.get_mode_name(m.mode_id)
        mu = m.mu
        if m.evidence_grade == "weak" and mu > WEAK_MU_CAP:
            if warnings:
                warnings.add(f"{m.mode_id}: weak evidence capped μ {mu:.3f}→{WEAK_MU_CAP}")
            mu = WEAK_MU_CAP
        if m.confidence < LOW_CONFIDENCE_THRESHOLD and warnings:
            warnings.add(f"{m.mode_id}: low confidence {m.confidence:.2f}")
        out.append(
            ModeScore(
                mode_id=m.mode_id,
                name=name,
                mu=round(mu, 4),
                confidence=m.confidence,
                evidence_grade=m.evidence_grade,
                contributing_signals=m.contributing_signals,
            )
        )
    return out


def evidence_confidence_from_modes(mode_ids: list[str], propagated_mu: dict[str, float]) -> float:
    if not mode_ids:
        return 0.3
    grades: list[float] = []
    for mid in mode_ids:
        mu = propagated_mu.get(mid, 0.0)
        if mu >= 0.6:
            grades.append(_GRADE_TO_CONFIDENCE["strong"])
        elif mu >= 0.35:
            grades.append(_GRADE_TO_CONFIDENCE["moderate"])
        else:
            grades.append(_GRADE_TO_CONFIDENCE["weak"])
    return sum(grades) / len(grades)
