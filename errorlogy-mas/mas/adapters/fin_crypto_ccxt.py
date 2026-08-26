"""CCXT public market-data adapter → FIN_CRYPTO normalized record → cross-layer envelope.

Market-data only — no API keys, no order placement, no private endpoints.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from mas.institutional.activation import frame_cross_layer_event

ADAPTER_ID = "ccxt:market_snapshot"
DEFAULT_EXCHANGE = os.getenv("FIN_CRYPTO_CCXT_EXCHANGE", "binance")
DEFAULT_SYMBOL = os.getenv("FIN_CRYPTO_CCXT_SYMBOL", "BTC/USDT")
DEFAULT_STORY_ID = os.getenv(
    "FIN_CRYPTO_CCXT_STORY_ID", "fin-crypto-btc-usdt-snapshot"
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _record_id(exchange_id: str, symbol: str, as_of: str) -> str:
    key = f"{exchange_id}:{symbol}:{as_of}"
    digest = hashlib.sha256(key.encode()).hexdigest()[:16]
    return f"{ADAPTER_ID}:{digest}"


def _unavailable_record(
    symbol: str,
    exchange_id: str,
    reason: str,
    *,
    notes: str | None = None,
) -> dict[str, Any]:
    observed = _now_iso()
    return {
        "adapter_id": ADAPTER_ID,
        "record_id": _record_id(exchange_id, symbol, observed),
        "story_id": DEFAULT_STORY_ID,
        "event_type": "fin_crypto_data_unavailable",
        "observed_at": observed,
        "as_of": None,
        "instrument": {
            "asset_class": "crypto",
            "symbol": symbol.replace("/", "-"),
            "exchange_or_venue": exchange_id,
        },
        "timeframe": None,
        "signal": {
            "name": "provider_error",
            "value": reason,
            "unit": None,
        },
        "evidence_grade": "weak",
        "quality_flags": ["error_envelope", "public_rest_only"],
        "uncertainty": {
            "confidence": 0.0,
            "notes": notes or reason,
        },
        "source_refs": {
            "provider_name": f"ccxt:{exchange_id}",
            "tool_call_id": None,
            "raw_payload_ref": None,
        },
    }


def fetch_market_snapshot(
    symbol: str = DEFAULT_SYMBOL,
    exchange_id: str = DEFAULT_EXCHANGE,
    *,
    story_id: str | None = None,
) -> dict[str, Any]:
    """Fetch a public ticker via CCXT and return a FIN_CRYPTO normalized record."""
    story = (story_id or DEFAULT_STORY_ID).strip()
    try:
        import ccxt  # type: ignore[import-not-found]
    except ImportError as exc:
        rec = _unavailable_record(symbol, exchange_id, "ccxt_not_installed", notes=str(exc))
        rec["story_id"] = story
        return rec

    try:
        exchange_class = getattr(ccxt, exchange_id)
    except AttributeError:
        rec = _unavailable_record(
            symbol, exchange_id, "unknown_exchange", notes=f"no ccxt exchange {exchange_id!r}"
        )
        rec["story_id"] = story
        return rec

    exchange = exchange_class({"enableRateLimit": True})
    try:
        ticker = exchange.fetch_ticker(symbol)
    except Exception as exc:  # noqa: BLE001 — provider errors become unavailable records
        rec = _unavailable_record(symbol, exchange_id, type(exc).__name__, notes=str(exc))
        rec["story_id"] = story
        return rec

    as_of_ms = ticker.get("timestamp")
    if as_of_ms:
        as_of = datetime.fromtimestamp(as_of_ms / 1000, tz=timezone.utc).replace(
            microsecond=0
        ).isoformat()
    else:
        as_of = _now_iso()

    observed = _now_iso()
    last = ticker.get("last")
    volume = ticker.get("quoteVolume") or ticker.get("baseVolume")
    quality_flags = ["public_rest_only"]
    if ticker.get("timestamp") is None:
        quality_flags.append("partial_payload")

    return {
        "adapter_id": ADAPTER_ID,
        "record_id": _record_id(exchange_id, symbol, as_of),
        "story_id": story,
        "event_type": "fin_crypto_market_snapshot",
        "observed_at": observed,
        "as_of": as_of,
        "instrument": {
            "asset_class": "crypto",
            "symbol": symbol.replace("/", "-"),
            "exchange_or_venue": exchange_id,
        },
        "timeframe": "24h",
        "signal": {
            "name": "last_price",
            "value": last,
            "unit": symbol.split("/")[-1] if "/" in symbol else None,
        },
        "evidence_grade": "medium" if last is not None else "weak",
        "quality_flags": quality_flags,
        "uncertainty": {
            "confidence": 0.75 if last is not None else 0.2,
            "notes": f"24h quoteVolume={volume}" if volume is not None else None,
        },
        "source_refs": {
            "provider_name": f"ccxt:{exchange_id}",
            "tool_call_id": None,
            "raw_payload_ref": None,
        },
    }


def record_to_cross_layer_ingress(
    record: dict[str, Any],
    *,
    jurisdiction_set: list[str] | None = None,
) -> dict[str, Any]:
    """Map normalized FIN record to partial cross-layer ingress (stub fills layers)."""
    payload: dict[str, Any] = {
        "story_id": record.get("story_id") or DEFAULT_STORY_ID,
        "event_type": record.get("event_type") or "fin_crypto_data_unavailable",
        "epistemic_label": "OPERATIONAL",
        "stream_refs": [record["record_id"]] if record.get("record_id") else None,
    }
    if jurisdiction_set:
        payload["jurisdiction_set"] = jurisdiction_set
    return {k: v for k, v in payload.items() if v is not None}


def ingest_fin_crypto_snapshot(
    symbol: str = DEFAULT_SYMBOL,
    exchange_id: str = DEFAULT_EXCHANGE,
    *,
    story_id: str | None = None,
    jurisdiction_set: list[str] | None = None,
) -> dict[str, Any]:
    """Fetch snapshot, frame cross-layer envelope, return adapter + event payloads."""
    record = fetch_market_snapshot(symbol, exchange_id, story_id=story_id)
    ingress = record_to_cross_layer_ingress(record, jurisdiction_set=jurisdiction_set)
    framed = frame_cross_layer_event(ingress)
    return {
        "adapter_record": record,
        "cross_layer_ingress": ingress,
        "cross_layer_event": framed,
    }


def persist_fin_crypto_snapshot(
    symbol: str = DEFAULT_SYMBOL,
    exchange_id: str = DEFAULT_EXCHANGE,
    *,
    story_id: str | None = None,
    jurisdiction_set: list[str] | None = None,
) -> dict[str, Any]:
    """Fetch, frame, persist to SQLite; return stored envelope + adapter record."""
    from mas import db as case_db

    result = ingest_fin_crypto_snapshot(
        symbol, exchange_id, story_id=story_id, jurisdiction_set=jurisdiction_set
    )
    event_id = f"cle-{uuid.uuid4().hex[:12]}"
    stored = case_db.save_cross_layer_event(event_id, result["cross_layer_event"])
    return {
        "status": "stored",
        "event_id": event_id,
        "adapter_record": result["adapter_record"],
        "event": stored,
    }
