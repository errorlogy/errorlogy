"""Web search via OpenRouter online / Perplexity models (uses OPENROUTER_API_KEY)."""

from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from ...config import OPENROUTER_API_KEY
from ._common import extract_urls, normalize_hit
from . import url as url_fetcher

_SEARCH_MODELS = (
    "perplexity/sonar",
    "openai/gpt-4o-mini:online",
    "google/gemini-2.0-flash-001:online",
)


def is_configured() -> bool:
    return bool(OPENROUTER_API_KEY.strip())


def search(query: str, *, num_results: int = 3) -> list[dict[str, Any]]:
    key = OPENROUTER_API_KEY.strip()
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY not set")

    client = OpenAI(api_key=key, base_url="https://openrouter.ai/api/v1")
    prompt = (
        f"Find {num_results} recent credible articles about: {query}\n"
        "Return ONLY valid JSON array. Each item: "
        '{"title":"...","url":"https://...","summary":"at least 300 words of factual summary"}'
    )

    last_err: Exception | None = None
    raw = ""
    for model in _SEARCH_MODELS:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
                temperature=0.2,
            )
            raw = resp.choices[0].message.content or ""
            if raw.strip():
                break
        except Exception as exc:
            last_err = exc
            continue
    else:
        raise RuntimeError(f"OpenRouter search failed: {last_err}")

    return _hits_from_response(raw, query=query, num_results=num_results)


def _hits_from_response(raw: str, *, query: str, num_results: int) -> list[dict[str, Any]]:
    items = _parse_json_array(raw)
    out: list[dict[str, Any]] = []
    for item in items[:num_results]:
        title = str(item.get("title", "")).strip()
        link = str(item.get("url", "")).strip()
        summary = str(item.get("summary") or item.get("text") or "").strip()

        hit: dict[str, Any] | None = None
        if link.startswith("http"):
            try:
                fetched = url_fetcher.fetch_url(link)
                if fetched:
                    hit = fetched
                    hit["source"] = "openrouter"
                    hit["source_type"] = "web_search"
                    if title:
                        hit["title"] = title
            except Exception:
                pass

        if not hit:
            hit = normalize_hit(
                source="openrouter",
                source_type="web_search",
                url=link,
                title=title or query,
                text=summary,
            )

        if hit:
            out.append(hit)

    if not out:
        for link in extract_urls(raw)[:num_results]:
            try:
                fetched = url_fetcher.fetch_url(link)
                if fetched:
                    fetched["source"] = "openrouter"
                    fetched["source_type"] = "web_search"
                    out.append(fetched)
            except Exception:
                continue

    return out


def _parse_json_array(raw: str) -> list[dict]:
    raw = raw.strip()
    fence = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", raw, re.DOTALL)
    if fence:
        raw = fence.group(1)
    start = raw.find("[")
    end = raw.rfind("]")
    if start >= 0 and end > start:
        raw = raw[start : end + 1]
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []
