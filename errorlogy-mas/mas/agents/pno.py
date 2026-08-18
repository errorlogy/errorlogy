from ..engine import pno as pno_engine
from ..schemas.analysis import ModeScore, PNOResult


class PNOAgent:
    name = "pno"

    def run(
        self,
        top_modes: list[ModeScore],
        case_description: str = "",
        propagated_mu: dict[str, float] | None = None,
    ) -> PNOResult:
        return pno_engine.score_pno(top_modes, propagated_mu=propagated_mu)
