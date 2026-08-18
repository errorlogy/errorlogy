import json
from .base import BaseAgent
from ..schemas.case import GovernanceCase, WeakSignal
from ..engine.wms_vocabulary import get_wms_signal_catalog, normalize_weak_signal


class ScoutAgent(BaseAgent):
    name = "scout"
    role = (
        "You are the Scout agent for Errorlogy. "
        "Your task: extract structured information from a raw governance event description. "
        "Identify weak multisource signals, key actors, timeline events, and domain. "
        "Output must be valid JSON matching the GovernanceCase schema."
    )

    def run(self, case_id: str, raw_text: str, title: str = "", country: str = "", year: int = 0) -> GovernanceCase:
        catalog = get_wms_signal_catalog()
        prompt = f"""Analyze the following governance event and return a JSON object.

Case ID: {case_id}
Title: {title}
Country: {country}
Year: {year}

Raw source text:
---
{raw_text}
---

Return a JSON object with fields:
- case_id (string)
- title (string, concise)
- description (string, 2-4 sentences, analytical, no accusations)
- country (string, ISO code or name)
- domain (string, e.g. "space_agency", "nuclear_safety", "public_health")
- year (int)
- source_text (string, keep original)
- weak_signals (array of objects with: signal_type, description, source_environment, strength 0-1, reliability 0-1, temporal_relevance 0-1)

For weak_signals use signal_type values from taxonomy WMS IDs (WMS-001..020):
{catalog}

Return ONLY valid JSON, no markdown fences."""

        raw = self._call([{"role": "user", "content": prompt}])
        data = self._parse_json(raw)
        signals = [normalize_weak_signal(WeakSignal(**s)) for s in data.pop("weak_signals", [])]
        return GovernanceCase(**data, weak_signals=signals)
