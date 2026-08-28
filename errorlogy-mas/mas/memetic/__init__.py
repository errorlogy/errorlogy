"""Memetic runtime scaffold (Phase B) — discourse graph and lineage events."""

from mas.memetic.discourse_graph import (
    DiscourseGraph,
    build_discourse_fork_detected_event,
    build_narrative_lineage_update_event,
    get_discourse_graph,
)
from mas.memetic.egd_hm_bridge import egd_to_memetic_propagation_snapshot

__all__ = [
    "DiscourseGraph",
    "build_discourse_fork_detected_event",
    "build_narrative_lineage_update_event",
    "egd_to_memetic_propagation_snapshot",
    "get_discourse_graph",
]
