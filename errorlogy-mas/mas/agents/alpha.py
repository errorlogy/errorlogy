from ..engine import alpha as alpha_engine
from ..engine.types import EngineWarnings
from ..schemas.analysis import AlphaResult, ModeScore


class AlphaPropagationAgent:
    """Pure algorithmic agent — delegates to mas.engine.alpha."""

    name = "alpha"

    def run(
        self,
        top_modes: list[ModeScore],
        warnings: EngineWarnings | None = None,
    ) -> AlphaResult:
        return alpha_engine.propagate(top_modes, warnings=warnings)
