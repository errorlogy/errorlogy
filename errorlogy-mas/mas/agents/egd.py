from ..engine import egd as egd_engine
from ..engine.types import EngineWarnings
from ..schemas.case import GovernanceCase
from ..schemas.analysis import EGDResult, ModeScore


class EGDAgent:
    name = "egd"

    def run(
        self,
        case: GovernanceCase,
        top_modes: list[ModeScore],
        warnings: EngineWarnings | None = None,
    ) -> EGDResult:
        return egd_engine.analyze(case, top_modes, warnings=warnings)
