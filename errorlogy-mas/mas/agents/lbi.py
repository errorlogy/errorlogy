from .base import BaseAgent
from ..schemas.analysis import LBIResult, BettermentAlternative


LBI_TYPES = [
    "information_betterment",
    "coordination_betterment",
    "legal_contour_betterment",
    "competence_routing_betterment",
    "temporal_betterment",
    "catastrophe_prevention_betterment",
    "incentive_realignment_betterment",
    "transparency_betterment",
]


class LBIAgent(BaseAgent):
    name = "lbi"
    role = (
        "You are the LBI (Betterment / Improvement) agent for Errorlogy. "
        "Generate feasible counterfactual alternatives: how could the governance error have been reduced? "
        "Use analytical, constructive language. No blame. No 'should have'. Use 'could have', 'alternative approach'. "
        "Each alternative must target specific error modes and estimate expected_reduction and feasibility."
    )

    def run(self, case: object, pno: object, acc: object, cat: object) -> LBIResult:
        prompt = f"""Case: {case.case_id} — {case.title}
Description: {case.description}

PNO regime: {pno.dominant_pno} — {pno.explanation}
Max contribution cluster: {acc.max_contribution_cluster.name} — {acc.max_contribution_cluster.explanation}
CAT hypothesis: {cat.catastrophe_hypothesis} — {cat.explanation}

Generate 4-6 betterment alternatives from these types:
{", ".join(LBI_TYPES)}

For each alternative:
- alternative_id: "LBI-001", "LBI-002", etc.
- title: concise name (5-10 words)
- target_modes: list of mode IDs this alternative addresses
- expected_reduction: estimated μ reduction (0-1) if implemented
- feasibility: institutional feasibility (0-1)
- risk_of_new_errors: list of potential new error modes this could introduce
- explanation: 2-3 sentences, analytical, constructive, no blame

Return JSON with: alternatives (array of betterment objects)
Return ONLY valid JSON."""

        raw = self._call([{"role": "user", "content": prompt}])
        data = self._parse_json(raw)
        if isinstance(data, list):
            alts = data
        else:
            alts = data.get("alternatives", [])
        return LBIResult(alternatives=[BettermentAlternative(**a) for a in alts])
