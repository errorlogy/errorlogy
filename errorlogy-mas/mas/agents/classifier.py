from ..engine import fuzzy
from ..engine.types import EngineWarnings, FuzzyContext
from ..schemas.analysis import ModeScore
from ..schemas.case import GovernanceCase


class FuzzyClassifierAgent:
    name = "classifier"

    def run(
        self,
        case: GovernanceCase,
        top_n: int = 20,
        ctx: FuzzyContext | None = None,
        warnings: EngineWarnings | None = None,
    ) -> list[ModeScore]:
        return fuzzy.score_candidates(case, top_n=top_n, ctx=ctx, warnings=warnings)
