"""Memetic ↔ fin-crypto market coupling join (Iteration 6).

Joins CCXT market snapshot records with optional memetic velocity sidecar
(peak_velocity, decay_tau_hours) on shared ``story_id`` or instrument symbol.

INSTITUTIONAL_MODEL framing — coupling is modeled context, not a trading signal.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from mas.adapters.fin_crypto_ccxt import fetch_market_snapshot, ingest_fin_crypto_snapshot
from mas.institutional.activation import frame_cross_layer_event

JoinKeyType = Literal["story_id", "symbol"]
_DEFAULT_EPISTEMIC = "INSTITUTIONAL_MODEL"
_COUPLING_EVENT_TYPE = "memetic_market_coupling_snapshot"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def symbol_to_story_id(symbol: str) -> str:
    """Default story anchor from instrument symbol when no explicit story_id."""
    normalized = symbol.replace("/", "-").replace(" ", "").lower()
    return f"fin-crypto-{normalized}-snapshot"


def resolve_join_key(
    *,
    story_id: str | None,
    symbol: str | None,
    market_record: dict[str, Any] | None = None,
) -> tuple[str, JoinKeyType, str]:
    """Resolve join key — prefer explicit story_id, else symbol from record or arg."""
    if story_id and story_id.strip():
        sid = story_id.strip()
        return sid, "story_id", sid

    record_symbol = None
    if market_record:
        instrument = market_record.get("instrument") or {}
        record_symbol = instrument.get("symbol")
        record_story = market_record.get("story_id")
        if record_story and str(record_story).strip():
            sid = str(record_story).strip()
            return sid, "story_id", sid
        if record_symbol:
            sym = str(record_symbol).replace("-", "/")
            return symbol_to_story_id(sym), "symbol", str(record_symbol)

    if symbol and symbol.strip():
        sym = symbol.strip()
        return symbol_to_story_id(sym), "symbol", sym.replace("/", "-")

    raise ValueError("join key required: provide story_id or symbol (or market_record with either)")


def normalize_memetic_sidecar(
    memetic_metrics: dict[str, Any] | None = None,
    *,
    stream_item_id: str | None = None,
    story_id: str | None = None,
) -> dict[str, Any] | None:
    """Normalize optional memetic metrics from politic-bar shape or API body."""
    if not memetic_metrics and stream_item_id is None:
        return None

    metrics = dict(memetic_metrics or {})
    sidecar: dict[str, Any] = {
        "stream_item_id": stream_item_id or metrics.get("stream_item_id"),
        "story_id": story_id or metrics.get("story_id"),
        "peak_velocity": metrics.get("peak_velocity"),
        "decay_tau_hours": metrics.get("decay_tau_hours"),
        "first_seen": metrics.get("first_seen"),
        "variant_of": metrics.get("variant_of"),
        "platform_contour": metrics.get("platform_contour"),
    }
    if sidecar["stream_item_id"] is None and sidecar["peak_velocity"] is None:
        return None
    return {k: v for k, v in sidecar.items() if v is not None}


def _coupling_record_id(story_id: str, market_record_id: str, observed_at: str) -> str:
    key = f"{story_id}:{market_record_id}:{observed_at}"
    digest = hashlib.sha256(key.encode()).hexdigest()[:16]
    return f"memetic_market_coupling:{digest}"


def build_coupling_record(
    market_record: dict[str, Any],
    memetic_sidecar: dict[str, Any] | None,
    *,
    join_key_type: JoinKeyType,
    join_key_value: str,
    story_id: str,
    persona_cohort_id: str | None = None,
) -> dict[str, Any]:
    """Full coupling join record (returned alongside cross-layer envelope)."""
    observed = _now_iso()
    market_rid = market_record.get("record_id") or "unknown"
    record = {
        "coupling_id": _coupling_record_id(story_id, market_rid, observed),
        "event_type": _COUPLING_EVENT_TYPE,
        "observed_at": observed,
        "join_key": {"type": join_key_type, "value": join_key_value},
        "story_id": story_id,
        "market_record": market_record,
        "memetic_sidecar": memetic_sidecar,
        "epistemic_label": _DEFAULT_EPISTEMIC,
        "quality_flags": _coupling_quality_flags(market_record, memetic_sidecar),
    }
    if persona_cohort_id:
        record["persona_cohort_id"] = persona_cohort_id
    return record


def _coupling_quality_flags(
    market_record: dict[str, Any],
    memetic_sidecar: dict[str, Any] | None,
) -> list[str]:
    flags: list[str] = ["institutional_model_join"]
    if market_record.get("event_type") == "fin_crypto_data_unavailable":
        flags.append("market_partial")
    if memetic_sidecar is None:
        flags.append("memetic_sidecar_missing")
    elif memetic_sidecar.get("decay_tau_hours") is None:
        flags.append("decay_tau_estimated_missing")
    return flags


def coupling_to_cross_layer_ingress(
    coupling_record: dict[str, Any],
    *,
    jurisdiction_set: list[str] | None = None,
    persona_cohort_id: str | None = None,
) -> dict[str, Any]:
    """Map coupling join → partial cross-layer ingress (stub fills layers)."""
    stream_refs: list[str] = []
    market = coupling_record.get("market_record") or {}
    if market.get("record_id"):
        stream_refs.append(str(market["record_id"]))
    sidecar = coupling_record.get("memetic_sidecar")
    if sidecar and sidecar.get("stream_item_id"):
        stream_refs.append(str(sidecar["stream_item_id"]))

    payload: dict[str, Any] = {
        "story_id": coupling_record["story_id"],
        "event_type": _COUPLING_EVENT_TYPE,
        "epistemic_label": _DEFAULT_EPISTEMIC,
    }
    if stream_refs:
        payload["stream_refs"] = stream_refs
    if jurisdiction_set:
        payload["jurisdiction_set"] = jurisdiction_set
    cohort = persona_cohort_id or coupling_record.get("persona_cohort_id")
    if cohort:
        payload["persona_cohort_id"] = cohort
    return payload


def build_memetic_market_coupling(
    market_record: dict[str, Any],
    memetic_metrics: dict[str, Any] | None = None,
    *,
    story_id: str | None = None,
    symbol: str | None = None,
    stream_item_id: str | None = None,
    jurisdiction_set: list[str] | None = None,
    persona_cohort_id: str | None = None,
) -> dict[str, Any]:
    """Join market record with memetic sidecar; return coupling + framed envelope."""
    sid, join_type, join_value = resolve_join_key(
        story_id=story_id,
        symbol=symbol,
        market_record=market_record,
    )
    if market_record.get("story_id") != sid:
        market_record = {**market_record, "story_id": sid}

    sidecar = normalize_memetic_sidecar(
        memetic_metrics,
        stream_item_id=stream_item_id,
        story_id=sid,
    )
    coupling_record = build_coupling_record(
        market_record,
        sidecar,
        join_key_type=join_type,
        join_key_value=join_value,
        story_id=sid,
        persona_cohort_id=persona_cohort_id,
    )
    ingress = coupling_to_cross_layer_ingress(
        coupling_record,
        jurisdiction_set=jurisdiction_set,
        persona_cohort_id=persona_cohort_id,
    )
    framed = frame_cross_layer_event(ingress)
    return {
        "coupling_record": coupling_record,
        "market_record": market_record,
        "memetic_sidecar": sidecar,
        "cross_layer_ingress": ingress,
        "cross_layer_event": framed,
    }


def ingest_memetic_market_coupling(
    *,
    symbol: str = "BTC/USDT",
    exchange_id: str = "binance",
    story_id: str | None = None,
    memetic_metrics: dict[str, Any] | None = None,
    stream_item_id: str | None = None,
    market_record: dict[str, Any] | None = None,
    jurisdiction_set: list[str] | None = None,
    persona_cohort_id: str | None = None,
) -> dict[str, Any]:
    """Fetch or accept market record, join memetic sidecar, frame coupling envelope."""
    record = market_record or fetch_market_snapshot(
        symbol, exchange_id, story_id=story_id
    )
    return build_memetic_market_coupling(
        record,
        memetic_metrics,
        story_id=story_id or record.get("story_id"),
        symbol=symbol if not story_id and not record.get("story_id") else None,
        stream_item_id=stream_item_id,
        jurisdiction_set=jurisdiction_set,
        persona_cohort_id=persona_cohort_id,
    )


def persist_memetic_market_coupling(
    *,
    symbol: str = "BTC/USDT",
    exchange_id: str = "binance",
    story_id: str | None = None,
    memetic_metrics: dict[str, Any] | None = None,
    stream_item_id: str | None = None,
    market_record: dict[str, Any] | None = None,
    jurisdiction_set: list[str] | None = None,
    persona_cohort_id: str | None = None,
) -> dict[str, Any]:
    """Join, frame, persist coupling cross-layer event to SQLite."""
    from mas import db as case_db

    result = ingest_memetic_market_coupling(
        symbol=symbol,
        exchange_id=exchange_id,
        story_id=story_id,
        memetic_metrics=memetic_metrics,
        stream_item_id=stream_item_id,
        market_record=market_record,
        jurisdiction_set=jurisdiction_set,
        persona_cohort_id=persona_cohort_id,
    )
    event_id = f"cle-{uuid.uuid4().hex[:12]}"
    stored = case_db.save_cross_layer_event(event_id, result["cross_layer_event"])
    return {
        "status": "stored",
        "event_id": event_id,
        "coupling_record": result["coupling_record"],
        "market_record": result["market_record"],
        "memetic_sidecar": result["memetic_sidecar"],
        "event": stored,
    }


def ingest_from_fin_crypto_and_memetic(
    symbol: str = "BTC/USDT",
    exchange_id: str = "binance",
    *,
    story_id: str | None = None,
    memetic_metrics: dict[str, Any] | None = None,
    stream_item_id: str | None = None,
    jurisdiction_set: list[str] | None = None,
) -> dict[str, Any]:
    """Convenience: run fin-crypto ingest then coupling join on same snapshot."""
    fin = ingest_fin_crypto_snapshot(
        symbol, exchange_id, story_id=story_id, jurisdiction_set=jurisdiction_set
    )
    return build_memetic_market_coupling(
        fin["adapter_record"],
        memetic_metrics,
        story_id=story_id or fin["adapter_record"].get("story_id"),
        stream_item_id=stream_item_id,
        jurisdiction_set=jurisdiction_set,
    )
