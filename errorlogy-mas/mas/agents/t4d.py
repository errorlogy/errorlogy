from ..engine import t4d as t4d_engine
from ..schemas.case import GovernanceCase
from ..schemas.analysis import T4DResult, WMSResult


class T4DAgent:
    name = "t4d"

    def run(self, case: GovernanceCase, wms_result: WMSResult) -> T4DResult:
        return t4d_engine.build_topology(case, wms_result)
