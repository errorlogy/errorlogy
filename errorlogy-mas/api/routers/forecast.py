"""Stream-level forecast aggregate API (Horizon 2)."""

from __future__ import annotations

import pathlib
import sys

from fastapi import APIRouter

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from mas.forecast_stream import build_stream_forecast
from mas.schemas.forecast_stream import StreamForecastResponse

router = APIRouter(prefix="/api/forecast", tags=["forecast"])


@router.get("/stream", response_model=StreamForecastResponse)
async def get_stream_forecast(
    country: str | None = None,
    iso3: str | None = None,
    window_days: int = 30,
    limit: int = 50,
    cep_threshold: float = 0.5,
):
    return build_stream_forecast(
        country=country,
        iso3=iso3,
        window_days=window_days,
        limit=limit,
        cep_threshold=cep_threshold,
    )
