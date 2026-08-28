"""Discourse graph scaffold for memetic Phase B runtime.

INSTITUTIONAL_MODEL — tracks narrative forks and lineage; does not claim verdict authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import networkx as nx

from mas.institutional.activation import default_activated_layers, frame_cross_layer_event

_DEFAULT_EPISTEMIC = "INSTITUTIONAL_MODEL"


class DiscourseGraph:
    """In-memory directed graph of story nodes and fork edges."""

    def __init__(self) -> None:
        self._graph = nx.DiGraph()

    def add_story_node(self, story_id: str, **attrs: Any) -> None:
        sid = story_id.strip()
        if not sid:
            raise ValueError("story_id is required")
        node_attrs = {k: v for k, v in attrs.items() if v is not None}
        if sid in self._graph:
            self._graph.nodes[sid].update(node_attrs)
        else:
            self._graph.add_node(sid, **node_attrs)

    def add_fork_edge(
        self,
        parent_id: str,
        child_id: str,
        *,
        edge_type: str = "narrative_fork",
        **attrs: Any,
    ) -> None:
        parent = parent_id.strip()
        child = child_id.strip()
        if not parent or not child:
            raise ValueError("parent_id and child_id are required")
        if parent == child:
            raise ValueError("parent_id and child_id must differ")
        self.add_story_node(parent)
        self.add_story_node(child)
        edge_attrs = {"edge_type": edge_type, **{k: v for k, v in attrs.items() if v is not None}}
        self._graph.add_edge(parent, child, **edge_attrs)

    def get_lineage(self, story_id: str) -> list[str]:
        """Return root-to-node path for story_id (longest upstream chain)."""
        sid = story_id.strip()
        if not sid or sid not in self._graph:
            return [sid] if sid else []
        roots = [n for n in self._graph.nodes if self._graph.in_degree(n) == 0]
        if sid in roots:
            return [sid]
        best: list[str] = []
        for root in roots:
            if not nx.has_path(self._graph, root, sid):
                continue
            path = nx.shortest_path(self._graph, root, sid)
            if len(path) > len(best):
                best = path
        return best if best else [sid]

    def detect_fork(self, story_id: str, variant_of: str | None) -> bool:
        """True when variant_of references an existing parent distinct from story_id."""
        sid = story_id.strip()
        parent = (variant_of or "").strip()
        if not sid or not parent or sid == parent:
            return False
        return parent in self._graph

    def descendants(self, story_id: str) -> list[str]:
        sid = story_id.strip()
        if sid not in self._graph:
            return []
        return list(nx.descendants(self._graph, sid))

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_count": self._graph.number_of_nodes(),
            "edge_count": self._graph.number_of_edges(),
            "nodes": list(self._graph.nodes),
            "edges": [
                {"parent": u, "child": v, **data}
                for u, v, data in self._graph.edges(data=True)
            ],
        }


_graph_singleton: DiscourseGraph | None = None


def get_discourse_graph() -> DiscourseGraph:
    global _graph_singleton
    if _graph_singleton is None:
        _graph_singleton = DiscourseGraph()
    return _graph_singleton


def build_discourse_fork_detected_event(
    story_id: str,
    *,
    parent_id: str,
    activated_layers: list[str] | None = None,
    epistemic_label: str = _DEFAULT_EPISTEMIC,
) -> dict[str, Any]:
    """Build framed cross-layer envelope for discourse_fork_detected."""
    payload: dict[str, Any] = {
        "story_id": story_id,
        "event_type": "discourse_fork_detected",
        "epistemic_label": epistemic_label,
    }
    if activated_layers:
        payload["activated_layers"] = activated_layers
    framed = frame_cross_layer_event(payload)
    framed["fork"] = {
        "parent_id": parent_id,
        "child_id": story_id,
        "detected_at": datetime.now(timezone.utc).isoformat(),
    }
    return framed


def build_narrative_lineage_update_event(
    story_id: str,
    lineage: list[str],
    *,
    activated_layers: list[str] | None = None,
    epistemic_label: str = _DEFAULT_EPISTEMIC,
) -> dict[str, Any]:
    """Build framed cross-layer envelope for narrative_lineage_update."""
    payload: dict[str, Any] = {
        "story_id": story_id,
        "event_type": "narrative_lineage_update",
        "epistemic_label": epistemic_label,
    }
    if activated_layers:
        payload["activated_layers"] = activated_layers
    framed = frame_cross_layer_event(payload)
    if not activated_layers:
        framed["activated_layers"] = default_activated_layers("narrative_lineage_update")
    framed["lineage"] = lineage
    return framed
