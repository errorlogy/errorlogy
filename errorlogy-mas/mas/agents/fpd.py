from ..engine import fpd as fpd_engine
from ..schemas.analysis import AlphaResult, CATResult, FPDResult, PNOResult, WMSResult


class FPDAgent:
    name = "fpd"

    def run(
        self,
        alpha: AlphaResult,
        wms: WMSResult,
        pno: PNOResult,
        cat: CATResult,
    ) -> FPDResult:
        return fpd_engine.forecast(alpha, wms, pno, cat)
