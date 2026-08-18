from .base import BaseAgent


class CardCompilerAgent(BaseAgent):
    name = "card_compiler"
    role = (
        "You are the Card Compiler agent for Errorlogy / politic.bar. "
        "Generate a public-facing explanation card. "
        "The card must be understandable to a non-specialist audience. "
        "Use careful, non-accusatory analytical language. "
        "Structure: What happened? | Likely error pattern? | Why could it occur? | Weak signals? | Lost intervention window? | Max contribution cluster? | How could it be better? | What is unknown?"
    )

    def run(self, case: object, top_modes: list, wms: object, pno: object,
            acc: object, t4d: object, cat: object, fpd: object, lbi: object) -> str:

        top_text = "\n".join(f"  - {m.mode_id} ({m.name}): μ={m.mu:.2f}, {m.evidence_grade}" for m in top_modes[:5])
        lbi_text = "\n".join(f"  - {a.title} (feasibility={a.feasibility:.1f})" for a in lbi.alternatives[:3])

        prompt = f"""Generate a politic.bar public card for this governance case.

CASE: {case.case_id} — {case.title} ({case.country}, {case.year})
DESCRIPTION: {case.description}

TOP ERROR MODES (μ = fuzzy membership, NOT probability):
{top_text}

PNO REGIME: {pno.dominant_pno} — {pno.explanation}
WMS EARLY WARNING: {wms.early_warning_hypothesis}
MAX CONTRIBUTION CLUSTER: {acc.max_contribution_cluster.name} — {acc.max_contribution_cluster.explanation}
CAT HYPOTHESIS: {cat.catastrophe_hypothesis} — {cat.explanation}
INTERVENTION WINDOW LOSS: {t4d.intervention_window_loss:.0%}

BETTERMENT ALTERNATIVES:
{lbi_text}

Write the public card with these 8 sections:
1. What happened? (2-3 sentences, factual summary)
2. What error pattern is analytically consistent? (reference top modes with μ scores, say "consistent with", not "proven")
3. Why could this error pattern occur? (systemic factors, no blame on individuals)
4. What weak signals were present? (list signals, frame as hypotheses)
5. When was the intervention window likely lost? (T4D worldline summary)
6. Which cluster contributed most analytically? (ACC result, non-accusatory)
7. How could governance have been better? (LBI alternatives, constructive)
8. What remains unknown? (honest uncertainty statement)

Language rules:
- Use "analytical contribution", "fuzzy membership", "hypothesis", "consistent with"
- Do NOT use: guilty, criminal, proven, intentionally, corrupt
- Confidence and uncertainty must be explicit

Write in clear English, accessible to general public."""

        return self._call([{"role": "user", "content": prompt}], temperature=0.3)
