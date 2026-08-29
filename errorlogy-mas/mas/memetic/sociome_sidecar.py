"""Sociome / MatrAIx persona cohort sidecar (Phase C / Iteration 7).

INSTITUTIONAL_MODEL only — cohort tags for diversity conditioning, not citizens or voters.
Full Persona 1M adapter post-MVP; sidecar slug validation only in this slice.
"""

from __future__ import annotations

import re
from typing import Any

_SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{2,63}$")
_DEFAULT_EPISTEMIC = "INSTITUTIONAL_MODEL"


def parse_persona_cohort_id(cohort_id: str) -> str:
    """Validate and normalize a persona cohort slug."""
    text = cohort_id.strip()
    if not _SLUG_PATTERN.match(text):
        raise ValueError(
            "persona_cohort_id must be a lowercase slug "
            "(3-64 chars, start with a-z, then [a-z0-9_-]), "
            f"got {cohort_id!r}"
        )
    return text


def sociome_sidecar_metadata(persona_cohort_id: str) -> dict[str, Any]:
    """Metadata block for fork / coupling / cross-layer events."""
    slug = parse_persona_cohort_id(persona_cohort_id)
    return {
        "persona_cohort_id": slug,
        "epistemic_label": _DEFAULT_EPISTEMIC,
    }


def attach_sociome_sidecar(
    payload: dict[str, Any],
    persona_cohort_id: str | None,
) -> dict[str, Any]:
    """Validate and attach persona_cohort_id to an event dict (shallow copy)."""
    out = dict(payload)
    if persona_cohort_id is not None:
        out["persona_cohort_id"] = parse_persona_cohort_id(persona_cohort_id)
    return out
