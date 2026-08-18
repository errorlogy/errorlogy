"""WMS taxonomy binding: legacy Scout/heuristic names → WMS-001..020."""

from __future__ import annotations

import re

from .. import taxonomy
from ..schemas.case import GovernanceCase, WeakSignal

WMS_UNK = "WMS-UNK"

_LEGACY_TO_WMS: dict[str, str] = {
    "bureaucratic_opacity": "WMS-011",
    "expert_dissent_suppressed": "WMS-003",
    "regulatory_capture": "WMS-005",
    "metric_gaming": "WMS-015",
    "schedule_pressure": "WMS-006",
    "cost_overrun": "WMS-018",
    "inter_agency_conflict": "WMS-017",
    "legal_ambiguity": "WMS-009",
    "media_silence": "WMS-011",
    "whistleblower_ignored": "WMS-013",
}

_LEGACY_ENV_TO_TAXONOMY: dict[str, str] = {
    "public_record": "media_investigative",
    "contractor": "procurement_contracts",
    "agency": "frontline_operations",
}

_ENV_TO_DEFAULT_WMS: dict[str, str] = {
    "audit_oversight": "WMS-004",
    "legal_judicial": "WMS-009",
    "parliamentary_inquiry": "WMS-009",
    "procurement_contracts": "WMS-005",
    "experts_science": "WMS-003",
    "whistleblowers": "WMS-013",
    "frontline_operations": "WMS-001",
    "citizens_users": "WMS-002",
    "media_investigative": "WMS-012",
    "social_media": "WMS-012",
    "sensor_data_KPI": "WMS-015",
    "international_comparison": "WMS-007",
}

_WMS_ID_RE = re.compile(r"^WMS-\d{3}$")


def _valid_wms_ids() -> set[str]:
    return set(taxonomy.get_wms_signal_types())


def normalize_signal_type(raw: str) -> str:
    """Map legacy or alias signal names to taxonomy WMS-00x IDs."""
    if not raw:
        return WMS_UNK
    key = raw.strip()
    if _WMS_ID_RE.match(key) and key in _valid_wms_ids():
        return key
    mapped = _LEGACY_TO_WMS.get(key.lower().replace("-", "_"))
    if mapped:
        return mapped
    lower = key.lower()
    for legacy, wms_id in _LEGACY_TO_WMS.items():
        if legacy.replace("_", " ") in lower or legacy in lower:
            return wms_id
    for item in taxonomy.get_wms_signal_defs():
        name = (item.get("name") or "").lower()
        if name and name in lower:
            return item["id"]
    return WMS_UNK


def normalize_source_environment(raw: str) -> str:
    """Map ingest/legacy environment labels to taxonomy source_environments."""
    if not raw:
        return ""
    key = raw.strip()
    valid = set(taxonomy.get_wms_source_environments())
    if key in valid:
        return key
    mapped = _LEGACY_ENV_TO_TAXONOMY.get(key.lower())
    if mapped:
        return mapped
    return key


def signal_type_for_source_environment(source_environment: str) -> str:
    """Default WMS signal type implied by an ingest source environment."""
    env = normalize_source_environment(source_environment)
    return _ENV_TO_DEFAULT_WMS.get(env, "WMS-004")


def normalize_weak_signal(signal: WeakSignal) -> WeakSignal:
    return signal.model_copy(
        update={
            "signal_type": normalize_signal_type(signal.signal_type),
            "source_environment": normalize_source_environment(signal.source_environment),
        }
    )


def normalize_case_signals(case: GovernanceCase) -> GovernanceCase:
    if not case.weak_signals:
        return case
    return case.model_copy(
        update={"weak_signals": [normalize_weak_signal(s) for s in case.weak_signals]}
    )


def get_wms_signal_catalog() -> str:
    """Formatted WMS catalog for Scout prompts."""
    lines: list[str] = []
    for item in taxonomy.get_wms_signal_defs():
        sid = item.get("id", "")
        name = item.get("name", "")
        desc = item.get("description", "")
        lines.append(f"- {sid}: {name} — {desc}")
    envs = ", ".join(taxonomy.get_wms_source_environments())
    lines.append(f"\nUse source_environment from: {envs}")
    lines.append(f"If signal type is unclear, use {WMS_UNK}.")
    return "\n".join(lines)


def ingest_metadata_to_signals(metadata: dict | None) -> list[WeakSignal]:
    """Build weak-signal stubs from ingest hit metadata."""
    if not metadata:
        return []
    env = metadata.get("source_environment") or metadata.get("wms_environment") or ""
    if not env:
        return []
    env = normalize_source_environment(env)
    wms_id = signal_type_for_source_environment(env)
    title = metadata.get("title") or metadata.get("doc_title") or ""
    agency = metadata.get("agency") or ""
    desc = title or f"Ingest signal from {env}"
    if agency:
        desc = f"{agency}: {desc}"
    return [
        WeakSignal(
            signal_type=wms_id,
            description=desc,
            source_environment=env,
            strength=0.45,
            reliability=0.65,
            temporal_relevance=0.8,
        )
    ]


def merge_weak_signals(
    primary: list[WeakSignal],
    extra: list[WeakSignal],
) -> list[WeakSignal]:
    """Merge ingest/heuristic signals with Scout output; dedupe by type+environment."""
    merged = [normalize_weak_signal(s) for s in primary]
    seen = {(s.signal_type, s.source_environment) for s in merged}
    for raw in extra:
        s = normalize_weak_signal(raw)
        key = (s.signal_type, s.source_environment)
        if key in seen:
            continue
        merged.append(s)
        seen.add(key)
    return merged
