"""Web search via Gemini Google Search grounding (uses GOOGLE_API_KEY)."""

from __future__ import annotations

import json
import re
from typing import Any

from google import genai
from google.genai import types

from ...config import GOOGLE_API_KEY
from ._common import extract_urls, normalize_hit
from . import url as url_fetcher


def is_configured() -> bool:
    return bool(GOOGLE_API_KEY.strip())


def search(query: str, *, num_results: int = 3) -> list[dict[str, Any]]:
    key = GOOGLE_API_KEY.strip()
    if not key:
        raise RuntimeError("GOOGLE_API_KEY not set")

    client = genai.Client(api_key=key)
    prompt = (
        f"Find {num_results} recent credible news or government reports about: {query}\n"
        "Return ONLY valid JSON array. Each item: "
        '{"title":"...","url":"https://...","summary":"at least 300 words"}'
    )
    config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.2,
        max_output_tokens=4096,
    )
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=config,
    )
    raw = response.text or ""
    hits = _hits_from_response(raw, query=query, num_results=num_results)

    grounding_urls = _grounding_urls(response)
    for link in grounding_urls:
        if len(hits) >= num_results:
            break
        if any(h.get("url") == link for h in hits):
            continue
        try:
            fetched = url_fetcher.fetch_url(link)
            if fetched:
                fetched["source"] = "gemini"
                fetched["source_type"] = "web_search"
                hits.append(fetched)
        except Exception:
            continue

    return hits[:num_results]


def _grounding_urls(response: Any) -> list[str]:
    urls: list[str] = []
    for cand in getattr(response, "candidates", []) or []:
        meta = getattr(cand, "grounding_metadata", None)
        if not meta:
            continue
        for chunk in getattr(meta, "grounding_chunks", []) or []:
            web = getattr(chunk, "web", None)
            if web and getattr(web, "uri", ""):
                urls.append(web.uri)
    return urls


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
                    hit["source"] = "gemini"
                    hit["source_type"] = "web_search"
                    if title:
                        hit["title"] = title
            except Exception:
                pass

        if not hit:
            hit = normalize_hit(
                source="gemini",
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
                    fetched["source"] = "gemini"
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
