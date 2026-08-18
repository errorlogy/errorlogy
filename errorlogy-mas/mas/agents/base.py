import time
import json
from typing import Any
from ..providers.router import LLMRouter
from ..config import MAX_TOKENS
from .. import metrics as pipeline_metrics

LANGUAGE_RULES = """
LANGUAGE RULES (mandatory):
- NEVER write: guilty, criminal, proven guilt, corrupt
- ALWAYS use: analytical contribution, fuzzy membership μ, confidence, evidence_grade
- Weak signals are hypotheses, NOT proof
- μ score is degree of membership, NOT probability
- Distinguish: mu_forecast / scenario_probability / confidence / evidence_grade
- All claims require: "analytical contribution", "possible", "hypothesis", "early-warning"
"""

# Module-level shared router — injected once at startup by Orchestrator
_router: LLMRouter | None = None


def set_router(router: LLMRouter) -> None:
    global _router
    _router = router


def get_router() -> LLMRouter:
    if _router is None:
        raise RuntimeError("LLMRouter not initialised. Call set_router() before using agents.")
    return _router


class BaseAgent:
    name: str = "base"
    role: str = ""

    def _system_prompt(self) -> str:
        return f"{self.role}\n\n{LANGUAGE_RULES}"

    def _call(
        self,
        messages: list[dict],
        temperature: float = 0.2,
    ) -> str:
        t0 = time.perf_counter()
        resp = get_router().complete(
            agent_name=self.name,
            system=self._system_prompt(),
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
        )
        pipeline_metrics.record_llm(self.name, resp, (time.perf_counter() - t0) * 1000)
        return resp.text

    @staticmethod
    def _parse_json(text: str) -> Any:
        text = text.strip()
        # strip markdown fences
        if "```" in text:
            lines = text.splitlines()
            text = "\n".join(l for l in lines if not l.startswith("```")).strip()

        # find whichever JSON structure appears first in the text
        idx_obj = text.find("{")
        idx_arr = text.find("[")
        candidates = sorted(
            [(i, c) for i, c in [(idx_obj, "{"), (idx_arr, "[")] if i != -1],
            key=lambda x: x[0],
        )
        decoder = json.JSONDecoder()
        for idx, _ in candidates:
            try:
                obj, _ = decoder.raw_decode(text, idx)
                return obj
            except json.JSONDecodeError:
                continue

        raise ValueError(f"No valid JSON found in agent output:\n{text[:400]}")
