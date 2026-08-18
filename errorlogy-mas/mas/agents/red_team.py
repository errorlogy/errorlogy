from .base import BaseAgent


class RedTeamAgent(BaseAgent):
    name = "red_team"
    role = (
        "You are the Red Team agent for Errorlogy. "
        "Critically review the analysis for: overclaims, weak evidence presented as strong, "
        "missing alternative explanations, selection bias in mode scoring, or contradictions. "
        "Your job is to strengthen the analysis, NOT to invalidate it. "
        "Be specific — cite mode IDs and claim text when flagging issues."
    )

    def run(self, case: object, top_modes: list, pno: object, acc: object) -> list[str]:
        modes_text = "\n".join(f"{m.mode_id} μ={m.mu:.2f} evidence={m.evidence_grade}" for m in top_modes[:10])

        prompt = f"""Case: {case.case_id} — {case.title}

Top modes scored:
{modes_text}

PNO: {pno.dominant_pno} — {pno.explanation}

Max contribution cluster: {acc.max_contribution_cluster.name} (score={acc.max_contribution_cluster.score:.2f})
Cluster explanation: {acc.max_contribution_cluster.explanation}

Review this analysis adversarially. Identify:
1. Any mode with μ > 0.6 where evidence_grade is "weak" — flag as potential overclaim
2. Missing alternative explanations or counterfactuals not considered
3. Any language that implies certainty where only hypothesis is warranted
4. Logical gaps between WMS signals and mode attributions

Return a JSON array of strings, each being one specific critical note.
Maximum 5 notes. Be concise (1-2 sentences each).
Return ONLY valid JSON array of strings."""

        raw = self._call([{"role": "user", "content": prompt}])
        data = self._parse_json(raw)
        if isinstance(data, dict):
            data = data.get("notes", [])
        return [str(n) for n in data]
