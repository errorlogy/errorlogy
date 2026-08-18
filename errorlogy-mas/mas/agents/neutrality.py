from .base import BaseAgent

FORBIDDEN_PATTERNS = [
    "guilty", "criminal", "corrupt", "proven guilty", "intentionally",
    "malicious", "fraudulent", "deliberately caused",
]


class NeutralityAuditorAgent(BaseAgent):
    name = "neutrality"
    role = (
        "You are the Neutrality Auditor for Errorlogy. "
        "Your task: scan all text for violations of the public language rules. "
        "Flag any sentence that makes legal accusations, asserts intent without evidence, "
        "presents fuzzy scores as facts, or uses prohibited terminology. "
        "Suggest a corrected phrasing for each flag."
    )

    def run(self, public_card: str) -> list[str]:
        forbidden = ", ".join(f'"{w}"' for w in FORBIDDEN_PATTERNS)

        prompt = f"""Review the following public explanation for Errorlogy language rule violations.

Forbidden: {forbidden}
Also flag: assertions of intent, fuzzy scores presented as facts, certainty claims without evidence_grade

Text to audit:
---
{public_card}
---

Return a JSON array. Each item is a string: "FLAG: [quoted offending phrase] → SUGGEST: [correction]"
If no violations found, return an empty array [].
Return ONLY valid JSON array."""

        raw = self._call([{"role": "user", "content": prompt}])
        data = self._parse_json(raw)
        if isinstance(data, dict):
            data = data.get("flags", [])
        return [str(f) for f in data]
