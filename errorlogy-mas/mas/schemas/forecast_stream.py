"""Pydantic models for stream-level forecast aggregate (Horizon 2)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TaxonomySummary(BaseModel):
    version: str | None = None
    mode_count: int = 0
    counts: dict[str, int | float] = Field(default_factory=dict)
    alpha_edges: int = 0
    dominant_modes: list[dict[str, Any]] = Field(default_factory=list)


class IngestSummary(BaseModel):
    documents_total: int = 0
    pending: int = 0
    analyzed: int = 0
    signals_total: int = 0
    last_ingest_at: str | None = None
    sources_breakdown: dict[str, int] = Field(default_factory=dict)
    active_alerts_count: int = 0
    fetchers_configured: dict[str, bool] = Field(default_factory=dict)


class EngineInfo(BaseModel):
    version: str
    modules: list[str] = Field(default_factory=list)


class StreamForecastResponse(BaseModel):
    generated_at: datetime
    window_days: int
    filters: dict[str, str | None]
    taxonomy: TaxonomySummary
    ingest: IngestSummary
    engine: EngineInfo
    engine_modules_used: list[str]
    alerts: list[dict[str, Any]]
    trends: list[dict[str, Any]]
    countries: list[dict[str, Any]]
    recent_cases: list[dict[str, Any]]
    horizon_note: str
    methodology: str
