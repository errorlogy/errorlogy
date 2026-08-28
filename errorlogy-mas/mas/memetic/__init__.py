"""Memetic runtime scaffold (Phase B) — discourse graph and lineage events."""

from mas.memetic.discourse_graph import (
    DiscourseGraph,
    build_discourse_fork_detected_event,
    build_narrative_lineage_update_event,
    get_discourse_graph,
)
from mas.memetic.egd_hm_bridge import egd_to_memetic_propagation_snapshot
from mas.memetic.testament_clauses import (
    CLAUSE_REGISTRY,
    clause_fork_metadata,
    parse_testament_clause_ref,
    resolve_testament_clause_ref,
)

__all__ = [
    "CLAUSE_REGISTRY",
    "DiscourseGraph",
    "build_discourse_fork_detected_event",
    "build_narrative_lineage_update_event",
    "clause_fork_metadata",
    "egd_to_memetic_propagation_snapshot",
    "get_discourse_graph",
    "parse_testament_clause_ref",
    "resolve_testament_clause_ref",
]
