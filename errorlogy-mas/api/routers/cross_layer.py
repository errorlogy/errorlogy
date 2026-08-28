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
from mas.memetic.discourse_graph import (
    build_discourse_fork_detected_event,
    build_narrative_lineage_update_event,
    get_discourse_graph,
)

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


class MemeticForkIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parent_id: str = Field(..., min_length=1)
    child_id: str = Field(..., min_length=1)
    edge_type: str = Field("narrative_fork", min_length=1)
    persist_events: bool = Field(True, description="Persist fork + lineage cross-layer events")


@router.post("/memetic/fork")
async def post_memetic_fork(body: MemeticForkIn):
    """Register a narrative fork in the discourse graph (INSTITUTIONAL_MODEL)."""
    graph = get_discourse_graph()
    try:
        graph.add_fork_edge(body.parent_id, body.child_id, edge_type=body.edge_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    lineage = graph.get_lineage(body.child_id)
    fork_event = build_discourse_fork_detected_event(
        body.child_id, parent_id=body.parent_id
    )
    lineage_event = build_narrative_lineage_update_event(body.child_id, lineage)

    stored_fork = stored_lineage = None
    if body.persist_events:
        fork_id = f"cle-{uuid.uuid4().hex[:12]}"
        lineage_id = f"cle-{uuid.uuid4().hex[:12]}"
        stored_fork = case_db.save_cross_layer_event(fork_id, fork_event)
        stored_lineage = case_db.save_cross_layer_event(lineage_id, lineage_event)

    return {
        "status": "registered",
        "note": "INSTITUTIONAL_MODEL discourse graph scaffold — no μ/α run",
        "lineage": lineage,
        "fork_event": stored_fork or fork_event,
        "lineage_event": stored_lineage or lineage_event,
        "graph": graph.to_dict(),
    }


@router.get("/memetic/lineage/{story_id}")
async def get_memetic_lineage(story_id: str):
    """Return root-to-node lineage for a story_id."""
    graph = get_discourse_graph()
    lineage = graph.get_lineage(story_id)
    descendants = graph.descendants(story_id)
    return {
        "story_id": story_id,
        "lineage": lineage,
        "descendants": sorted(descendants),
        "graph": graph.to_dict(),
    }
