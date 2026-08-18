from ..engine import acc as acc_engine
from ..schemas.case import GovernanceCase
from ..schemas.analysis import ACCResult


class ACCAgent:
    name = "acc"

    def run(
        self,
        propagated_mu: dict[str, float],
        case_description: str = "",
        case: GovernanceCase | None = None,
    ) -> ACCResult:
        if case is None:
            from ..schemas.case import GovernanceCase
            case = GovernanceCase(
                case_id="unknown",
                title="",
                description=case_description,
                country="",
                domain="",
                year=0,
                source_text=case_description,
            )
        return acc_engine.score_clusters(propagated_mu, case)
