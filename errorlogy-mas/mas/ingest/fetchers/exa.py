"""Fetch governance / media documents via Exa Search / Agent API (exa-py)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any

from ...config import EXA_AGENT_EFFORT, EXA_AGENT_MODE, EXA_SEARCH_TYPE
from ._common import normalize_hit

_GOVERNANCE_SYSTEM_PROMPT = (
    "Prefer official government reports, parliamentary inquiries, regulatory filings, "
    "and reputable journalism. Collapse duplicate reporting. Keep excerpts factual and grounded."
)

_GOVERNANCE_ARTICLES_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["articles"],
    "properties": {
        "articles": {
            "type": "array",
            "description": "Recent articles about governance or management failures",
            "items": {
                "type": "object",
                "required": ["title", "url", "excerpt"],
                "properties": {
                    "title": {"type": "string"},
                    "url": {"type": "string"},
                    "excerpt": {
                        "type": "string",
                        "description": "Grounded excerpt about governance, oversight, or management failure",
                    },
                    "country": {"type": "string"},
                },
            },
        }
    },
}


def _api_key() -> str:
    return os.environ.get("EXA_API_KEY", "").strip()


def is_configured() -> bool:
    return bool(_api_key())


@lru_cache(maxsize=1)
def _client():
    from exa_py import Exa

    key = _api_key()
    if not key:
        raise RuntimeError("EXA_API_KEY not set in environment")
    return Exa(api_key=key)


def _highlights_text(result: Any) -> str:
    highlights = getattr(result, "highlights", None)
    if highlights:
        if isinstance(highlights, list):
            joined = "\n\n".join(str(h).strip() for h in highlights if h)
            if joined:
                return joined
        if isinstance(highlights, str) and highlights.strip():
            return highlights.strip()

    text = getattr(result, "text", None) or ""
    return str(text).strip()


def _result_to_hit(result: Any, *, source: str = "exa") -> dict[str, Any] | None:
    url = (getattr(result, "url", None) or "").strip()
    title = (getattr(result, "title", None) or url[:80] or "Untitled").strip()
    text = _highlights_text(result)
    return normalize_hit(
        source=source,
        source_type="web_search",
        title=title,
        text=text,
        url=url,
    )


def _structured_articles(payload: Any) -> list[dict[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return []
    if not isinstance(payload, dict):
        return []
    articles = payload.get("articles")
    if not isinstance(articles, list):
        return []
    return [a for a in articles if isinstance(a, dict)]


def agent_search(query: str, *, num_results: int = 5) -> list[dict[str, Any]]:
    """Deep research via Exa Agent API (usage-based; see EXA_AGENT_EFFORT)."""
    exa = _client()
    schema = dict(_GOVERNANCE_ARTICLES_SCHEMA)
    articles_prop = schema["properties"]["articles"]
    articles_prop = dict(articles_prop)
    articles_prop["maxItems"] = max(1, min(num_results, 10))
    schema = dict(schema)
    schema["properties"] = dict(schema["properties"])
    schema["properties"]["articles"] = articles_prop

    run = exa.agent.runs.create(
        query=query,
        system_prompt=_GOVERNANCE_SYSTEM_PROMPT,
        output_schema=schema,
        effort=EXA_AGENT_EFFORT,
    )
    finished = exa.agent.runs.poll_until_finished(run.id)

    structured = None
    output = getattr(finished, "output", None)
    if output is not None:
        structured = getattr(output, "structured", None)
        if structured is None and hasattr(output, "content"):
            structured = output.content

    out: list[dict[str, Any]] = []
    for article in _structured_articles(structured):
        hit = normalize_hit(
            source="exa_agent",
            source_type="web_search",
            title=str(article.get("title", "")),
            text=str(article.get("excerpt", "")),
            url=str(article.get("url", "")),
            country=str(article.get("country", "")),
        )
        if hit:
            out.append(hit)
    return out


def search(query: str, *, num_results: int = 5) -> list[dict[str, Any]]:
    """Web search for ingest. Uses Agent API when EXA_AGENT_MODE=true, else /search."""
    if not is_configured():
        raise RuntimeError("EXA_API_KEY not set in environment")

    if EXA_AGENT_MODE:
        return agent_search(query, num_results=num_results)

    exa = _client()
    response = exa.search(
        query,
        type=EXA_SEARCH_TYPE,
        num_results=num_results,
        system_prompt=_GOVERNANCE_SYSTEM_PROMPT,
        contents={"highlights": True},
    )

    out: list[dict[str, Any]] = []
    for result in getattr(response, "results", []) or []:
        hit = _result_to_hit(result)
        if hit:
            out.append(hit)
    return out
