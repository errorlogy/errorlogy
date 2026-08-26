"""Cross-layer institutional event ingress (AI Native Gov contracts).

Does not run analyze/μ pipeline — framing stub only (INSTITUTIONAL_MODEL).
"""

from __future__ import annotations

import pathlib
import sys
import uuid
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from mas import db as case_db
from mas.adapters.fin_crypto_ccxt import persist_fin_crypto_snapshot
from mas.institutional.activation import INSTITUTION_LAYER_IDS, frame_cross_layer_event

router = APIRouter(prefix="/api/events", tags=["events"])

ResolutionStatus = Literal[
    "unresolved", "partially_resolved", "resolved", "not_applicable"
]


class TopologyIntersection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intersection: str = Field(..., min_length=1)
    tension_type: str = Field(..., min_length=1)
    resolution_status: ResolutionStatus | None = None


class CrossLayerEventIn(BaseModel):
    """Umbrella cross-layer-event.json — activated_layers optional (stub-filled)."""

    model_config = ConfigDict(extra="forbid")

    story_id: str = Field(..., min_length=1)
    event_type: str = Field(..., min_length=1)
    activated_layers: list[str] | None = None
    topology_intersections: list[TopologyIntersection] | None = None
    jurisdiction_set: list[str] | None = None
    coordination_forum: str | None = None
    politifi_assets: list[str] | None = None
    stream_refs: list[str] | None = None
    precedent_refs: list[str] | None = None
    certificate_ref: str | None = None
    epistemic_label: str | None = None


@router.post("/cross-layer")
async def post_cross_layer(body: CrossLayerEventIn):
    try:
        framed = frame_cross_layer_event(body.model_dump(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    event_id = f"cle-{uuid.uuid4().hex[:12]}"
    stored = case_db.save_cross_layer_event(event_id, framed)
    return {
        "status": "stored",
        "note": "INSTITUTIONAL_MODEL framing stub — no analyze/μ run",
        "event": stored,
    }


@router.get("/cross-layer")
async def get_cross_layer_list(
    limit: int = Query(50, ge=1, le=500),
    story_id: str | None = None,
    event_type: str | None = None,
):
    events = case_db.list_cross_layer_events(
        limit=limit, story_id=story_id, event_type=event_type
    )
    return {"count": len(events), "events": events}


@router.get("/cross-layer/layers")
async def get_institution_layers():
    layers = sorted(INSTITUTION_LAYER_IDS)
    return {"count": len(layers), "layers": layers}


@router.get("/cross-layer/{event_id}")
async def get_cross_layer_one(event_id: str):
    event = case_db.get_cross_layer_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")
    return event


@router.post("/fin-crypto/snapshot")
async def post_fin_crypto_snapshot(
    symbol: str = Query("BTC/USDT", min_length=3),
    exchange: str = Query("binance", min_length=2),
    story_id: str | None = Query(None),
    jurisdiction: list[str] | None = Query(None),
):
    """Public CCXT ticker → FIN_CRYPTO record → framed cross-layer event (OPERATIONAL)."""
    try:
        result = persist_fin_crypto_snapshot(
            symbol=symbol,
            exchange_id=exchange,
            story_id=story_id,
            jurisdiction_set=jurisdiction,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "status": result["status"],
        "note": "FIN_CRYPTO CCXT adapter — market-data only; no trading surface",
        "adapter_record": result["adapter_record"],
        "event": result["event"],
    }
