"""POSLEDNIY_ZAVET clause registry (I–X) for memetic runtime routing.

INSTITUTIONAL_MODEL only — routing hints, not religious authority or verdicts.
Full testament prose stays in isa-2.0; umbrella holds pointer only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from mas.institutional.activation import (
    LAYER_AUDIT,
    LAYER_JUDICIARY,
    LAYER_OMBUDSMAN,
    LAYER_PARLIAMENT,
    LAYER_PARTY,
    LAYER_SYMBOLIC,
)

CLAUSE_PREFIX = "POSLEDNIY_ZAVET"
_WIRE_PATTERN = re.compile(
    rf"^{CLAUSE_PREFIX}:(I|II|III|IV|V|VI|VII|VIII|IX|X)$"
)

_ISA_POLITIFI = "institution:isa-2.0"


@dataclass(frozen=True)
class TestamentClause:
    clause_id: str
    short_label_en: str
    activated_layers: tuple[str, ...]
    politifi_assets: tuple[str, ...] = (_ISA_POLITIFI,)


CLAUSE_REGISTRY: dict[str, TestamentClause] = {
    "I": TestamentClause(
        "I",
        "Non-equality with void",
        (LAYER_PARLIAMENT, LAYER_PARTY, LAYER_SYMBOLIC),
    ),
    "II": TestamentClause(
        "II",
        "True duality within contour",
        (LAYER_PARLIAMENT, LAYER_PARTY, LAYER_SYMBOLIC),
    ),
    "III": TestamentClause(
        "III",
        "Talion ∞ (accountability contour)",
        (LAYER_PARLIAMENT, LAYER_PARTY, LAYER_JUDICIARY),
    ),
    "IV": TestamentClause(
        "IV",
        "No accountability erasure",
        (LAYER_PARLIAMENT, LAYER_PARTY, LAYER_AUDIT),
    ),
    "V": TestamentClause(
        "V",
        "Well (isolation contour)",
        (LAYER_PARLIAMENT, LAYER_PARTY, LAYER_SYMBOLIC),
    ),
    "VI": TestamentClause(
        "VI",
        "Guard memory",
        (LAYER_PARLIAMENT, LAYER_PARTY, LAYER_AUDIT),
    ),
    "VII": TestamentClause(
        "VII",
        "Contour self-sufficiency",
        (LAYER_PARLIAMENT, LAYER_PARTY, LAYER_SYMBOLIC),
    ),
    "VIII": TestamentClause(
        "VIII",
        "Taboo on bond with void",
        (LAYER_PARLIAMENT, LAYER_PARTY, LAYER_SYMBOLIC, LAYER_JUDICIARY),
    ),
    "IX": TestamentClause(
        "IX",
        "Innocent protection",
        (LAYER_PARLIAMENT, LAYER_PARTY, LAYER_JUDICIARY, LAYER_OMBUDSMAN),
    ),
    "X": TestamentClause(
        "X",
        "Reproduction guilt (isolation verdict)",
        (LAYER_PARLIAMENT, LAYER_PARTY, LAYER_JUDICIARY, LAYER_AUDIT),
    ),
}


def parse_testament_clause_ref(ref: str) -> str:
    """Validate wire ref and return Roman-numeral clause id (I–X)."""
    text = (ref or "").strip()
    match = _WIRE_PATTERN.match(text)
    if not match:
        raise ValueError(
            f"testament_clause_ref must match POSLEDNIY_ZAVET:(I|II|...|X), got {ref!r}"
        )
    return match.group(1)


def get_clause(clause_id: str) -> TestamentClause:
    key = clause_id.strip()
    if key not in CLAUSE_REGISTRY:
        raise ValueError(f"unknown testament clause id: {clause_id!r}")
    return CLAUSE_REGISTRY[key]


def resolve_testament_clause_ref(ref: str) -> TestamentClause:
    return get_clause(parse_testament_clause_ref(ref))


def format_testament_clause_ref(clause_id: str) -> str:
    return f"{CLAUSE_PREFIX}:{get_clause(clause_id).clause_id}"


def clause_fork_metadata(ref: str) -> dict[str, Any]:
    """Routing sidecar for clause-triggered discourse forks."""
    clause = resolve_testament_clause_ref(ref)
    return {
        "testament_clause_ref": format_testament_clause_ref(clause.clause_id),
        "testament_clause_id": clause.clause_id,
        "testament_clause_label": clause.short_label_en,
        "activated_layers": list(clause.activated_layers),
        "politifi_assets": list(clause.politifi_assets),
    }
