"""Memetic runtime scaffold (Phase B) — discourse graph and lineage events."""

from mas.memetic.discourse_graph import (
    DiscourseGraph,
    build_discourse_fork_detected_event,
    build_narrative_lineage_update_event,
    get_discourse_graph,
)
from mas.memetic.egd_hm_bridge import egd_to_memetic_propagation_snapshot
from mas.memetic.market_coupling import (
    build_memetic_market_coupling,
    ingest_memetic_market_coupling,
    persist_memetic_market_coupling,
)
from mas.memetic.sociome_sidecar import (
    attach_sociome_sidecar,
    parse_persona_cohort_id,
    sociome_sidecar_metadata,
)
from mas.memetic.testament_clauses import (
    CLAUSE_REGISTRY,
    clause_fork_metadata,
    parse_testament_clause_ref,
    resolve_testament_clause_ref,
)

__all__ = [
    "CLAUSE_REGISTRY",
    "DiscourseGraph",
    "attach_sociome_sidecar",
    "build_discourse_fork_detected_event",
    "build_memetic_market_coupling",
    "build_narrative_lineage_update_event",
    "clause_fork_metadata",
    "egd_to_memetic_propagation_snapshot",
    "get_discourse_graph",
    "ingest_memetic_market_coupling",
    "parse_persona_cohort_id",
    "parse_testament_clause_ref",
    "persist_memetic_market_coupling",
    "resolve_testament_clause_ref",
    "sociome_sidecar_metadata",
]
