from ..engine import wms as wms_engine
from ..schemas.case import GovernanceCase
from ..schemas.analysis import WMSResult


class WMSAgent:
    name = "wms"

    def run(self, case: GovernanceCase, prev_cep: float = 0.0) -> WMSResult:
        return wms_engine.detect(case, prev_cep=prev_cep)
