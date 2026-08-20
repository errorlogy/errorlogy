"""Stub institutional activation: event_type → activated_layers.

INSTITUTIONAL_MODEL only — does not run μ/α analysis or claim legal authority.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

# Valid institution-layer-id enum values (umbrella schemas/institution-layer-id.json)
LAYER_PARLIAMENT = "institution:parliament"
LAYER_EXECUTIVE = "institution:executive"
LAYER_JUDICIARY = "institution:judiciary"
LAYER_INTERPOL = "institution:interpol-analog"
LAYER_TRANSNATIONAL = "institution:transnational-ops"
LAYER_AI_SPEAKER = "institution:ai-speaker"
LAYER_PARTY = "institution:party-coalition"
LAYER_AI_MINISTER = "institution:ai-minister"
LAYER_AI_PM = "institution:ai-pm"
LAYER_AUDIT = "institution:audit"
LAYER_OMBUDSMAN = "institution:ombudsman"
LAYER_CENTRAL_BANK = "institution:central-bank-analog"
LAYER_REGULATORY = "institution:regulatory-agency"
LAYER_EU_PARLIAMENT = "institution:eu-parliament"
LAYER_EU_COMMISSION = "institution:eu-commission"
LAYER_EU_COUNCIL = "institution:eu-council"
LAYER_EU_COURT = "institution:eu-court-of-justice"
LAYER_EU_OPS = "institution:eu-transnational-ops"
LAYER_NATIONAL = "institution:national-instance"
LAYER_SYMBOLIC = "institution:symbolic-visual"

INSTITUTION_LAYER_IDS = frozenset(
    {
        LAYER_PARLIAMENT,
        LAYER_EXECUTIVE,
        LAYER_JUDICIARY,
        LAYER_INTERPOL,
        LAYER_TRANSNATIONAL,
        LAYER_AI_SPEAKER,
        LAYER_PARTY,
        LAYER_AI_MINISTER,
        LAYER_AI_PM,
        LAYER_AUDIT,
        LAYER_OMBUDSMAN,
        LAYER_CENTRAL_BANK,
        LAYER_REGULATORY,
        LAYER_EU_PARLIAMENT,
        LAYER_EU_COMMISSION,
        LAYER_EU_COUNCIL,
        LAYER_EU_COURT,
        LAYER_EU_OPS,
        LAYER_NATIONAL,
        LAYER_SYMBOLIC,
    }
)

EPISTEMIC_LABELS = frozenset(
    {
        "INSTITUTIONAL_MODEL",
        "OPERATIONAL",
        "COMPUTATIONAL_EVIDENCE",
        "PHILOSOPHICAL_INFERENCE",
    }
)

# Prefix / exact → default layers (min 1). First match by longest prefix wins for prefixes.
_EXACT: dict[str, list[str]] = {
    "bilateral_summit": [LAYER_EXECUTIVE, LAYER_PARLIAMENT, LAYER_TRANSNATIONAL],
    "sanctions_coordination": [
        LAYER_EXECUTIVE,
        LAYER_EU_COUNCIL,
        LAYER_TRANSNATIONAL,
        LAYER_JUDICIARY,
    ],
    "domestic_policy": [LAYER_PARLIAMENT, LAYER_EXECUTIVE, LAYER_NATIONAL],
}

_PREFIX: list[tuple[str, list[str]]] = [
    (
        "fin_crypto_",
        [
            LAYER_CENTRAL_BANK,
            LAYER_REGULATORY,
            LAYER_EU_COMMISSION,
            LAYER_EXECUTIVE,
        ],
    ),
    (
        "gov_",
        [
            LAYER_PARLIAMENT,
            LAYER_EU_PARLIAMENT,
            LAYER_NATIONAL,
            LAYER_JUDICIARY,
        ],
    ),
    (
        "symbolic_",
        [LAYER_SYMBOLIC, LAYER_PARLIAMENT, LAYER_AI_PM],
    ),
]

_FALLBACK = [LAYER_EXECUTIVE, LAYER_PARLIAMENT]


def default_activated_layers(event_type: str) -> list[str]:
    if event_type in _EXACT:
        return list(_EXACT[event_type])
    for prefix, layers in _PREFIX:
        if event_type.startswith(prefix):
            return list(layers)
    return list(_FALLBACK)


def frame_cross_layer_event(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize a cross-layer envelope; fill activated_layers / epistemic_label if needed."""
    out = deepcopy(payload)
    story_id = (out.get("story_id") or "").strip()
    event_type = (out.get("event_type") or "").strip()
    if not story_id:
        raise ValueError("story_id is required")
    if not event_type:
        raise ValueError("event_type is required")
    out["story_id"] = story_id
    out["event_type"] = event_type

    layers = out.get("activated_layers")
    if not layers:
        out["activated_layers"] = default_activated_layers(event_type)
    elif not isinstance(layers, list) or len(layers) < 1:
        raise ValueError("activated_layers must be a non-empty array when provided")
    else:
        if not all(isinstance(x, str) and x for x in layers):
            raise ValueError("activated_layers items must be non-empty strings")
        bad = [x for x in layers if x not in INSTITUTION_LAYER_IDS]
        if bad:
            raise ValueError(f"invalid activated_layers: {bad}")

    label = out.get("epistemic_label") or "INSTITUTIONAL_MODEL"
    if label not in EPISTEMIC_LABELS:
        raise ValueError(f"epistemic_label must be one of {sorted(EPISTEMIC_LABELS)}")
    out["epistemic_label"] = label

    # Drop unknown keys to honor additionalProperties: false on umbrella schema
    allowed = {
        "story_id",
        "event_type",
        "activated_layers",
        "topology_intersections",
        "jurisdiction_set",
        "coordination_forum",
        "politifi_assets",
        "stream_refs",
        "precedent_refs",
        "certificate_ref",
        "epistemic_label",
    }
    return {k: v for k, v in out.items() if k in allowed and v is not None}
