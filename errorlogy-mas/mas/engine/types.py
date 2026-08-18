"""Shared types for the deterministic analytics engine."""

from dataclasses import dataclass, field

from ..schemas.case import GovernanceCase
from ..schemas.analysis import ModeScore


@dataclass
class FuzzyContext:
    """Optional boosts passed into fuzzy scoring."""

    wms_msi: float = 0.0
    t4d_latency_risk: float = 0.0
    cat_bifurcation_risk: float = 0.0


@dataclass
class EngineWarnings:
    flags: list[str] = field(default_factory=list)

    def add(self, msg: str) -> None:
        self.flags.append(msg)
