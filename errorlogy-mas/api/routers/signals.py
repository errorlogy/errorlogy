"""Signal alerts and CEP trend API (Horizon 2)."""

from __future__ import annotations

import pathlib
import sys

from fastapi import APIRouter

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from mas.engine.cep_alerts import list_cep_alerts, signal_trends

router = APIRouter(prefix="/api/signals", tags=["signals"])


@router.get("/alerts")
async def get_alerts(
    cep_threshold: float = 0.5,
    country: str | None = None,
    iso3: str | None = None,
    limit: int = 50,
    window_days: int = 7,
):
    alerts = list_cep_alerts(
        cep_threshold=cep_threshold,
        country=country,
        iso3=iso3,
        limit=limit,
        window_days=window_days,
    )
    return {
        "cep_threshold": cep_threshold,
        "window_days": window_days,
        "count": len(alerts),
        "alerts": alerts,
    }


@router.get("/trends")
async def get_trends(
    window_days: int = 7,
    limit: int = 100,
):
    trends = signal_trends(window_days=window_days, limit=limit)
    return {
        "window_days": window_days,
        "count": len(trends),
        "trends": trends,
    }
