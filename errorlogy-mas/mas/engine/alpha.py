"""Alpha propagation through the taxonomy error graph."""

from __future__ import annotations

import networkx as nx

from .. import taxonomy
from ..config import ALPHA_STEPS, ALPHA_DAMPING, ALPHA_THRESHOLD
from ..schemas.analysis import AlphaResult, AlphaEdgeActivated, ModeScore
from .guards import apply_mode_guards
from .types import EngineWarnings


def propagate(
    top_modes: list[ModeScore],
    warnings: EngineWarnings | None = None,
) -> AlphaResult:
    if not top_modes:
        return AlphaResult(
            initial_mu={},
            propagated_mu={},
            activated_edges=[],
            top_modes=[],
        )

    mu: dict[str, float] = {m.mode_id: m.mu for m in top_modes}
    initial_mu = dict(mu)
    graph = taxonomy.get_alpha_graph()
    activated: list[AlphaEdgeActivated] = []
    seen_edges: set[tuple[str, str, int]] = set()

    for step in range(ALPHA_STEPS):
        delta: dict[str, float] = {}
        for src, dst, data in graph.edges(data=True):
            w = float(data.get("weight", 0.0)) * float(data.get("confidence", 1.0))
            mu_src = mu.get(src, 0.0)
            mu_dst = mu.get(dst, 0.0)
            d = w * mu_src * (1.0 - mu_dst) * ALPHA_DAMPING
            if abs(d) > ALPHA_THRESHOLD:
                key = (src, dst, step)
                if key not in seen_edges:
                    seen_edges.add(key)
                    activated.append(
                        AlphaEdgeActivated(
                            from_id=src,
                            to_id=dst,
                            weight=w,
                            delta_mu=round(d, 4),
                        )
                    )
                delta[dst] = delta.get(dst, 0.0) + d
        for node, d in delta.items():
            mu[node] = max(0.0, min(1.0, mu.get(node, 0.0) + d))

    mode_lookup = {m.mode_id: m for m in top_modes}
    top_result: list[ModeScore] = []
    for mode_id, mu_val in sorted(mu.items(), key=lambda x: -x[1])[:20]:
        base = mode_lookup.get(mode_id)
        top_result.append(
            ModeScore(
                mode_id=mode_id,
                name=taxonomy.get_mode_name(mode_id) if not base else base.name,
                mu=round(mu_val, 4),
                confidence=base.confidence if base else 0.5,
                evidence_grade=base.evidence_grade if base else "weak",
                contributing_signals=base.contributing_signals if base else [],
            )
        )

    guarded = apply_mode_guards(top_result, warnings)

    return AlphaResult(
        initial_mu=initial_mu,
        propagated_mu=mu,
        activated_edges=activated,
        top_modes=guarded,
    )
