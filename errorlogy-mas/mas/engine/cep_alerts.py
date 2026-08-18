"""CEP early-warning alerts from persisted signal_timeseries (TZ-H2)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .. import db as case_db

DEFAULT_WINDOW_DAYS = 7


def cep_severity(cep: float) -> str:
    """Map CEP level to alert severity (CEP is cumulative error pressure, not probability)."""
    if cep >= 0.8:
        return "high"
    if cep >= 0.65:
        return "medium"
    return "low"


def _parse_ts(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)


def _window_cutoff(days: int) -> str:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return cutoff.isoformat()


def list_cep_alerts(
    *,
    cep_threshold: float = 0.5,
    country: str | None = None,
    iso3: str | None = None,
    limit: int = 50,
    window_days: int = DEFAULT_WINDOW_DAYS,
) -> list[dict]:
    """Return alerts where latest or window-max CEP exceeds threshold per iso3 stream."""
    rows = case_db.list_signal_timeseries(country=country, iso3=iso3, limit=5000)
    if not rows:
        return []

    cutoff = _parse_ts(_window_cutoff(window_days))
    by_iso: dict[str, list[dict]] = {}
    for row in rows:
        key = row.get("iso3") or row.get("country") or "UNK"
        by_iso.setdefault(key, []).append(row)

    alerts: list[dict] = []
    for iso_key, points in by_iso.items():
        points.sort(key=lambda r: r.get("recorded_at", ""), reverse=True)
        latest = points[0]
        latest_cep = float(latest.get("cep") or 0)
        window_points = [
            p for p in points
            if _parse_ts(p.get("recorded_at", "")) >= cutoff
        ]
        max_window_cep = max((float(p.get("cep") or 0) for p in window_points), default=latest_cep)
        trigger_cep = max(latest_cep, max_window_cep)

        if trigger_cep < cep_threshold:
            continue

        alerts.append({
            "country": latest.get("country") or iso_key,
            "iso3": latest.get("iso3") or iso_key,
            "cep": round(trigger_cep, 4),
            "latest_cep": round(latest_cep, 4),
            "max_cep_window": round(max_window_cep, 4),
            "doc_id": latest.get("doc_id") or "",
            "case_id": latest.get("case_id") or "",
            "recorded_at": latest.get("recorded_at") or "",
            "severity": cep_severity(trigger_cep),
            "signal_count_window": len(window_points),
        })

    alerts.sort(key=lambda a: a["cep"], reverse=True)
    return alerts[:limit]


def count_active_alerts(
    *,
    cep_threshold: float = 0.5,
    window_days: int = DEFAULT_WINDOW_DAYS,
) -> int:
    return len(list_cep_alerts(
        cep_threshold=cep_threshold,
        limit=10_000,
        window_days=window_days,
    ))


def signal_trends(
    *,
    window_days: int = DEFAULT_WINDOW_DAYS,
    limit: int = 100,
) -> list[dict]:
    """Per-country CEP trend summary for Globe / ingest dashboards."""
    rows = case_db.list_signal_timeseries(limit=5000)
    if not rows:
        return []

    cutoff = _parse_ts(_window_cutoff(window_days))
    by_iso: dict[str, list[dict]] = {}
    for row in rows:
        key = row.get("iso3") or ""
        if not key:
            continue
        by_iso.setdefault(key, []).append(row)

    trends: list[dict] = []
    for iso_key, points in by_iso.items():
        points.sort(key=lambda r: r.get("recorded_at", ""))
        latest = points[-1]
        latest_cep = float(latest.get("cep") or 0)
        window_points = [
            p for p in points
            if _parse_ts(p.get("recorded_at", "")) >= cutoff
        ]
        cep_max = max((float(p.get("cep") or 0) for p in points), default=latest_cep)
        if window_points:
            oldest_in_window = window_points[0]
            cep_delta = latest_cep - float(oldest_in_window.get("cep") or 0)
        else:
            cep_delta = 0.0

        trends.append({
            "iso3": iso_key,
            "country": latest.get("country") or iso_key,
            "cep_max": round(cep_max, 4),
            "cep_latest": round(latest_cep, 4),
            "cep_delta_7d": round(cep_delta, 4),
            "signal_count": len(window_points) if window_points else len(points),
            "last_signal_at": latest.get("recorded_at") or "",
        })

    trends.sort(key=lambda t: t["cep_max"], reverse=True)
    return trends[:limit]
