"""Catastrophe theory / bifurcation hypothesis (TZ §9.10)."""

from __future__ import annotations

import numpy as np

from ..schemas.analysis import ACCResult, CATResult, PNOResult, T4DResult, WMSResult

_CAT_RULES = [
    ("CAT-001", lambda w, t, a: w.cep > 0.6 and t.irreversibility_threshold_risk > 0.6),
    ("CAT-002", lambda w, t, a: a.max_contribution_cluster.score > 0.45 and (
        a.max_contribution_cluster.cluster_id in ("ACC-001", "ACC-002", "ACC-003") or
        "capacity" in a.max_contribution_cluster.name.lower() or
        "veto" in a.max_contribution_cluster.name.lower()
    )),
    ("CAT-003", lambda w, t, a: t.intervention_window_loss > 0.55 and t.warning_to_action_latency_risk > 0.5),
    ("CAT-010", lambda w, t, a: w.msi > 0.5 and t.warning_to_action_latency_risk > 0.45),
    ("CAT-015", lambda w, t, a: t.intervention_window_loss > 0.6 and w.cep > 0.5),
]

_CAT_NAMES = {
    "CAT-001": "Fold catastrophe — threshold exceeded",
    "CAT-002": "Cusp catastrophe — blocker + capacity gap",
    "CAT-003": "Swallowtail — path dependence transition",
    "CAT-010": "Critical slowing — backlog / churn signals",
    "CAT-015": "Catastrophic loss of optionality",
}


def _sympy_form(hypothesis_id: str) -> str:
    try:
        from sympy import symbols

        x, a, b, c = symbols("x a b c")
        forms = {
            "CAT-001": f"x**3 + {a}*x",
            "CAT-002": f"x**4 + {a}*x**2 + {b}*x",
            "CAT-003": f"x**5 + {a}*x**3 + {b}*x**2 + {c}*x",
            "CAT-010": f"x**3 - {a}*x",
            "CAT-015": f"x**4 - {a}*x**2",
        }
        return forms.get(hypothesis_id, "generic_fold")
    except Exception:
        return "n/a"


def evaluate(
    wms: WMSResult,
    t4d: T4DResult,
    pno: PNOResult,
    acc: ACCResult,
) -> CATResult:
    hypothesis = "CAT-000"
    for cat_id, rule in _CAT_RULES:
        if rule(wms, t4d, acc):
            hypothesis = cat_id
            break

    bifurcation = float(
        np.clip(
            0.25 * wms.cep
            + 0.25 * t4d.irreversibility_threshold_risk
            + 0.2 * t4d.intervention_window_loss
            + 0.15 * acc.max_contribution_cluster.score
            + 0.15 * max(pno.scores.values()),
            0.0,
            1.0,
        )
    )
    hysteresis = float(
        np.clip(
            0.3 * t4d.warning_to_action_latency_risk + 0.35 * wms.cep + 0.2 * t4d.intervention_window_loss,
            0.0,
            1.0,
        )
    )

    name = _CAT_NAMES.get(hypothesis, hypothesis)
    form = _sympy_form(hypothesis)
    explanation = (
        f"Bifurcation hypothesis {hypothesis} ({name}) is analytically consistent with "
        f"CEP={wms.cep:.2f}, irreversibility={t4d.irreversibility_threshold_risk:.2f}. "
        f"Canonical form reference: {form}. Hypothesis only — not a prediction."
    )

    return CATResult(
        catastrophe_hypothesis=hypothesis,
        bifurcation_risk=round(bifurcation, 4),
        hysteresis_risk=round(hysteresis, 4),
        explanation=explanation,
    )
