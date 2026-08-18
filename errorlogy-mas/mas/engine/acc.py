"""ACC contribution cluster detection (TZ §9.7)."""

from __future__ import annotations

import numpy as np

from .. import taxonomy
from ..schemas.case import GovernanceCase
from ..schemas.analysis import ACCResult, ClusterResult
from .guards import evidence_confidence_from_modes


def _environment_diversity(case: GovernanceCase) -> float:
    envs = {s.source_environment for s in case.weak_signals if s.source_environment}
    if not envs:
        return 0.4
    return float(min(1.0, len(envs) / 6))


def score_clusters(
    propagated_mu: dict[str, float],
    case: GovernanceCase,
) -> ACCResult:
    archetypes = taxonomy.get_acc_archetypes()
    if not archetypes:
        archetypes = [
            {
                "id": "ACC-001",
                "name": "Capacity-veto cluster",
                "signature_modes": ["CB-081", "SF-013"],
            }
        ]

    env_div = _environment_diversity(case)
    clusters: list[ClusterResult] = []

    for arch in archetypes:
        cid = arch.get("id", "ACC-???")
        name = arch.get("name", cid)
        sig = arch.get("signature_modes", [])
        mus = [propagated_mu.get(m, 0.0) for m in sig]
        mean_mu = float(np.mean(mus)) if mus else 0.0
        ev_conf = evidence_confidence_from_modes(sig, propagated_mu)
        score = float(np.clip(mean_mu * ev_conf * env_div, 0.0, 1.0))
        present = [m for m in sig if propagated_mu.get(m, 0.0) > 0.1]
        explanation = (
            f"Analytical contribution cluster {cid}: mean μ={mean_mu:.2f} across "
            f"{len(present)}/{len(sig)} signature modes (hypothesis, not guilt)."
        )
        clusters.append(
            ClusterResult(
                cluster_id=cid,
                name=name,
                score=round(score, 4),
                signature_modes=sig,
                explanation=explanation,
            )
        )

    clusters.sort(key=lambda c: -c.score)
    max_c = clusters[0] if clusters else ClusterResult(
        cluster_id="ACC-000",
        name="None",
        score=0.0,
        signature_modes=[],
        explanation="No cluster scored above threshold.",
    )
    return ACCResult(max_contribution_cluster=max_c, clusters=clusters)
