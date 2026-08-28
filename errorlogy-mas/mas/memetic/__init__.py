"""Memetic runtime scaffold (Phase B) — discourse graph and lineage events."""

from mas.memetic.discourse_graph import (
    DiscourseGraph,
    build_discourse_fork_detected_event,
    build_narrative_lineage_update_event,
    get_discourse_graph,
)

__all__ = [
    "DiscourseGraph",
    "build_discourse_fork_detected_event",
    "build_narrative_lineage_update_event",
    "get_discourse_graph",
]
