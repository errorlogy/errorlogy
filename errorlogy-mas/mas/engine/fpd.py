"""Fuzzy Predictive Dynamics forecast (TZ §9.11)."""

from __future__ import annotations

import numpy as np

from ..schemas.analysis import (
    AlphaResult,
    CATResult,
    EarlyWarning,
    FPDResult,
    ModeForecast,
    PNOResult,
    WMSResult,
)


def _sigmoid_trajectory(start: float, steps: int, center: float, width: float) -> np.ndarray:
    x = np.linspace(0, 1, steps)
    return start + (1.0 - start) * (1.0 / (1.0 + np.exp(-(x - center) / max(width, 0.05))))


def _horizon(cat: CATResult, wms: WMSResult) -> str:
    if cat.bifurcation_risk > 0.7 or wms.cep > 0.75:
        return "near"
    if cat.bifurcation_risk > 0.5 or wms.cep > 0.55:
        return "short"
    if cat.bifurcation_risk > 0.35:
        return "medium"
    return "long"


def forecast(
    alpha: AlphaResult,
    wms: WMSResult,
    pno: PNOResult,
    cat: CATResult,
) -> FPDResult:
    horizon = _horizon(cat, wms)
    traj_center = 0.4 + 0.3 * cat.bifurcation_risk
    traj_width = 0.15

    mode_forecasts: list[ModeForecast] = []
    for m in alpha.top_modes[:5]:
        mu0 = m.mu
        traj = _sigmoid_trajectory(mu0, 20, traj_center, traj_width)
        mu_f = float(np.clip(traj[-1] + 0.05 * wms.cep, 0.0, 1.0))
        scenario_p = float(np.clip(0.3 + 0.4 * cat.bifurcation_risk, 0.0, 1.0))
        conf = float(np.clip(0.35 + 0.3 * m.confidence + 0.2 * (1.0 - cat.hysteresis_risk), 0.0, 1.0))
        grade = m.evidence_grade
        if mu_f > 0.65 and grade == "weak":
            grade = "moderate"
        mode_forecasts.append(
            ModeForecast(
                mode_id=m.mode_id,
                mu_forecast=round(mu_f, 4),
                scenario_probability=round(scenario_p, 4),
                confidence=round(conf, 4),
                evidence_grade=grade,
            )
        )

    pno_transition = (
        f"PNO transition hypothesis: regime {pno.dominant_pno} may persist or deepen "
        f"if CEP remains elevated (analytical forecast, not certainty)."
    )

    warnings: list[EarlyWarning] = []
    if wms.cep > 0.5:
        warnings.append(
            EarlyWarning(
                signal="elevated_CEP",
                urgency="high" if wms.cep > 0.65 else "medium",
                description="Cumulative error pressure suggests monitoring for regime shift.",
            )
        )
    if cat.bifurcation_risk > 0.5:
        warnings.append(
            EarlyWarning(
                signal="bifurcation_risk",
                urgency="medium",
                description=f"Catastrophe hypothesis {cat.catastrophe_hypothesis} warrants contingency review.",
            )
        )

    confidence = float(
        np.clip(0.4 + 0.25 * (1.0 - cat.hysteresis_risk) + 0.2 * wms.msi, 0.0, 1.0)
    )

    return FPDResult(
        horizon=horizon,
        mode_forecasts=mode_forecasts,
        pno_transition_forecast=pno_transition,
        early_warnings=warnings,
        confidence=round(confidence, 4),
    )
