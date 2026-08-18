from ..engine import cat as cat_engine
from ..schemas.analysis import ACCResult, CATResult, PNOResult, T4DResult, WMSResult


class CATAgent:
    name = "cat"

    def run(
        self,
        wms: WMSResult,
        t4d: T4DResult,
        pno: PNOResult,
        acc: ACCResult,
    ) -> CATResult:
        return cat_engine.evaluate(wms, t4d, pno, acc)
