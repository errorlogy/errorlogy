"""Aggregate stream-level forecast from ingest, signals, cases, taxonomy, engine."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from . import db as case_db, taxonomy
from .engine import ENGINE_VERSION
from .engine.cep_alerts import list_cep_alerts, signal_trends
from .ingest.service import fetcher_status

HORIZON_NOTE = (
    "Stream forecast does not compute absolute calendar dates — only the direction "
    "of CEP/MSI pressure over the observation window and aggregates by country/case."
)

METHODOLOGY = (
    "Stream forecast (Horizon 2) aggregates ingest signals and CEP trends by country. "
    "Case forecast FPD (Horizon 1) is built separately for each GovernanceCase "
    "by the FPD/T4D module and returns μ_forecast by mode — μ is fuzzy "
    "membership degree, not probability."
)

STREAM_ENGINE_MODULES = [
    "ingest",
    "signals",
    "wms",
    "cep",
    "msi",
    "taxonomy",
    "pno",
    "egd",
]


def _dominant_modes_from_cases(cases: list[dict], *, top_n: int = 8) -> list[dict]:
    counter: Counter[str] = Counter()
    names: dict[str, str] = {}
    mus: dict[str, list[float]] = {}
    for case in cases:
        for m in case.get("top_modes") or []:
            mid = m.get("mode_id")
            if not mid:
                continue
            counter[mid] += 1
            names[mid] = m.get("name") or names.get(mid, mid)
            mus.setdefault(mid, []).append(float(m.get("mu") or 0))
    ranked = counter.most_common(top_n)
    return [
        {
            "mode_id": mid,
            "name": names.get(mid, mid),
            "case_hits": hits,
            "avg_mu": round(sum(mus.get(mid, [0])) / max(len(mus.get(mid, [])), 1), 4),
        }
        for mid, hits in ranked
    ]


def _recent_cases_with_modes(limit: int) -> list[dict]:
    out: list[dict] = []
    for row in case_db.list_cases(limit=limit):
        full = case_db.get_case(row["case_id"])
        top_modes: list[dict] = []
        if full:
            top_modes = [
                {
                    "mode_id": m.get("mode_id"),
                    "name": m.get("name"),
                    "mu": m.get("mu"),
                }
                for m in (full.get("top_modes") or [])[:5]
            ]
        out.append({**row, "top_modes": top_modes})
    return out


def _filter_countries(
    countries: list[dict],
    *,
    country: str | None,
    iso3: str | None,
) -> list[dict]:
    if iso3:
        key = iso3.upper()
        return [c for c in countries if (c.get("iso3") or "").upper() == key]
    if country:
        needle = country.lower()
        return [
            c for c in countries
            if needle in (c.get("name") or "").lower()
            or needle in (c.get("iso3") or "").lower()
        ]
    return countries


def _filter_trends(
    trends: list[dict],
    *,
    country: str | None,
    iso3: str | None,
) -> list[dict]:
    if iso3:
        key = iso3.upper()
        return [t for t in trends if (t.get("iso3") or "").upper() == key]
    if country:
        needle = country.lower()
        return [
            t for t in trends
            if needle in (t.get("country") or "").lower()
            or needle in (t.get("iso3") or "").lower()
        ]
    return trends


def build_stream_forecast(
    *,
    country: str | None = None,
    iso3: str | None = None,
    window_days: int = 30,
    limit: int = 50,
    cep_threshold: float = 0.5,
) -> dict:
    """Build aggregate stream forecast from real persisted data."""
    now = datetime.now(timezone.utc)
    stats = case_db.ingest_stats()
    fetchers = fetcher_status()

    alerts = list_cep_alerts(
        cep_threshold=cep_threshold,
        country=country,
        iso3=iso3,
        limit=limit,
        window_days=window_days,
    )
    trends = _filter_trends(
        signal_trends(window_days=window_days, limit=limit),
        country=country,
        iso3=iso3,
    )

    if case_db.case_count() > 0:
        globe = case_db.country_stats_globe()
        countries = _filter_countries(
            globe.get("countries", []),
            country=country,
            iso3=iso3,
        )[:limit]
    else:
        countries = []

    recent_cases = _recent_cases_with_modes(limit=min(limit, 20))
    tax_data = taxonomy.load()
    counts = tax_data.get("counts") or {}
    mode_count = int(counts.get("atomic_total") or len(tax_data.get("atomic_modes") or []))

    from mas.engine.cep_alerts import count_active_alerts

    return {
        "generated_at": now,
        "window_days": window_days,
        "filters": {"country": country, "iso3": iso3},
        "taxonomy": {
            "version": tax_data.get("version"),
            "mode_count": mode_count,
            "counts": counts,
            "alpha_edges": len(taxonomy.get_alpha_edges()),
            "dominant_modes": _dominant_modes_from_cases(recent_cases),
        },
        "ingest": {
            "documents_total": stats["documents_total"],
            "pending": stats["documents_pending"],
            "analyzed": stats["documents_analyzed"],
            "signals_total": stats["signals_total"],
            "last_ingest_at": stats["last_ingest_at"],
            "sources_breakdown": stats["sources"],
            "active_alerts_count": count_active_alerts(
                cep_threshold=cep_threshold,
                window_days=window_days,
            ),
            "fetchers_configured": fetchers,
        },
        "engine": {
            "version": ENGINE_VERSION,
            "modules": STREAM_ENGINE_MODULES,
        },
        "engine_modules_used": STREAM_ENGINE_MODULES,
        "alerts": alerts,
        "trends": trends,
        "countries": countries,
        "recent_cases": recent_cases,
        "horizon_note": HORIZON_NOTE,
        "methodology": METHODOLOGY,
    }
