"""Temporal-spatial topology (TZ §9.9)."""

from __future__ import annotations

import re

import numpy as np

from ..schemas.case import GovernanceCase
from ..schemas.analysis import ErrorWorldlinePoint, T4DResult, WMSResult
from .wms_vocabulary import normalize_signal_type

_STAGE_KEYWORDS = {
    "weak_signal": ("concern", "memo", "warning", "risk", "prior", "documented", "flagged", "noted"),
    "ignored_warning": ("overruled", "reversed", "pressure", "dissent", "ignored", "rejected", "dismissed"),
    "escalation": ("launch", "approve", "authorize", "decision", "proceed", "greenlit", "signed"),
    "failure": ("broke", "destroyed", "disaster", "failure", "explosion", "accident", "collapsed"),
    "inquiry": ("commission", "investigation", "inquiry", "report", "hearing", "audit", "review"),
}


def _extract_years(text: str) -> list[int]:
    return [int(y) for y in re.findall(r"\b(19\d{2}|20\d{2})\b", text)]


def _classify_stage(sentence: str) -> str:
    s = sentence.lower()
    scores = {st: sum(1 for kw in kws if kw in s) for st, kws in _STAGE_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "weak_signal"


def _case_text(case: GovernanceCase) -> str:
    base = case.source_text or case.description
    kb = (case.metadata or {}).get("kb_context") or ""
    if kb:
        return f"{base}\n\n{kb}"
    return base


def _build_worldline(case: GovernanceCase) -> list[ErrorWorldlinePoint]:
    text = _case_text(case)
    years = _extract_years(text)
    sentences = [s.strip() for s in re.split(r"[.\n]+", text) if len(s.strip()) > 20]

    points: list[ErrorWorldlinePoint] = []
    used_stages: set[str] = set()

    for i, sent in enumerate(sentences[:12]):
        stage = _classify_stage(sent)
        if stage in used_stages and len(used_stages) < 3:
            continue
        used_stages.add(stage)
        t = str(years[min(i, len(years) - 1)]) if years else f"stage-{i+1}"
        points.append(
            ErrorWorldlinePoint(
                t=t,
                stage=stage,
                modes=[],
                description=sent[:200],
            )
        )
        if len(points) >= 5:
            break

    if not points:
        points = [
            ErrorWorldlinePoint(
                t=str(case.year) if case.year else "unknown",
                stage="escalation",
                modes=[],
                description=case.description[:200],
            )
        ]
    return points


def _changepoint_risk(case: GovernanceCase, wms: WMSResult) -> float:
    years = _extract_years(case.source_text + case.description)
    if len(years) < 4:
        return 0.3 + 0.3 * wms.cep
    try:
        import ruptures as rpt

        series = np.array(sorted(set(years)), dtype=float).reshape(-1, 1)
        if len(series) < 4:
            return 0.4
        algo = rpt.Pelt(model="rbf").fit(series)
        bkps = algo.predict(pen=3)
        return float(np.clip(0.2 + 0.15 * len(bkps), 0.0, 1.0))
    except Exception:
        return float(np.clip(0.25 + 0.5 * wms.cep, 0.0, 1.0))


def build_topology(case: GovernanceCase, wms: WMSResult) -> T4DResult:
    worldline = _build_worldline(case)
    text = (case.source_text + case.description).lower()

    latency_risk = 0.3
    if any(k in text for k in (
        "overruled", "reversed", "pressure", "dissent", "ignored",
        "rejected", "dismissed", "not transmitted",
    )):
        latency_risk += 0.35
    if any(normalize_signal_type(s.signal_type) == "WMS-003" for s in case.weak_signals):
        latency_risk += 0.25
    latency_risk = float(np.clip(latency_risk, 0.0, 1.0))

    stages = [p.stage for p in worldline]
    window_loss = 0.3
    if "ignored_warning" in stages and "failure" in stages:
        window_loss += 0.35
    window_loss = float(np.clip(window_loss + 0.2 * wms.cep, 0.0, 1.0))

    irreversibility = float(np.clip(0.2 + 0.4 * wms.cep + 0.2 * _changepoint_risk(case, wms), 0.0, 1.0))

    return T4DResult(
        worldline=worldline,
        warning_to_action_latency_risk=round(latency_risk, 4),
        intervention_window_loss=round(window_loss, 4),
        irreversibility_threshold_risk=round(irreversibility, 4),
    )
