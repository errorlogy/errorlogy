"""Pre-pipeline source discovery via Exa (and optional web-search fallback)."""

from __future__ import annotations

from typing import Any

from .fetchers import exa as exa_fetcher
from .service import _pick_web_search_provider, _search_hits


def build_discovery_query(
    *,
    title: str = "",
    country: str = "",
    year: int = 0,
    raw_text: str = "",
    extra: str = "",
) -> str:
    """Compose a governance-focused search query from case metadata."""
    parts: list[str] = []
    if title:
        parts.append(title.strip())
    if country:
        parts.append(country.strip())
    if year:
        parts.append(str(year))
    if extra:
        parts.append(extra.strip())
    snippet = (raw_text or "").strip().replace("\n", " ")[:240]
    if snippet and not title:
        parts.append(snippet)
    base = " ".join(p for p in parts if p)
    if not base:
        base = "government regulatory failure investigation report"
    if "investigation" not in base.lower() and "inquiry" not in base.lower():
        base = f"{base} official investigation report governance failure"
    return base[:500]


def discover_sources(
    query: str,
    *,
    num_results: int = 3,
    provider: str | None = None,
) -> tuple[list[dict[str, Any]], str]:
    """
    Fetch supplemental source hits for a case query.

    Returns (hits, provider_used). Prefers Exa when configured (or EXA_PREFERRED).
    """
    chosen = provider
    if not chosen:
        if exa_fetcher.is_configured():
            chosen = "exa"
        else:
            chosen = _pick_web_search_provider()

    if not chosen:
        return [], ""

    hits = _search_hits(chosen, query, num_results=num_results)
    return hits, chosen


def format_source_bundle_section(hits: list[dict[str, Any]], *, provider: str) -> str:
    """Render discovered hits as an appendable source-bundle block."""
    if not hits:
        return ""
    lines = [
        "",
        "--- ADDITIONAL SOURCES (automated discovery via "
        f"{provider}) ---",
        "Hypothesis snippets only; not verified evidence.",
    ]
    for i, hit in enumerate(hits, start=1):
        title = hit.get("title", "Untitled")
        url = hit.get("url", "")
        text = (hit.get("text") or "").strip()
        header = f"[{i}] {title}"
        if url:
            header = f"{header} ({url})"
        lines.append(header)
        lines.append(text)
        lines.append("")
    return "\n".join(lines).strip()


def enrich_source_bundle(
    raw_text: str,
    *,
    title: str = "",
    country: str = "",
    year: int = 0,
    num_results: int = 3,
    provider: str | None = None,
    query: str | None = None,
) -> tuple[str, list[dict[str, Any]], str]:
    """
    Append Exa/web-search excerpts to raw_text for Scout + engine.

    Returns (enriched_text, hits, provider_used). If no provider or hits, returns
    original raw_text unchanged.
    """
    q = query or build_discovery_query(
        title=title,
        country=country,
        year=year,
        raw_text=raw_text,
    )
    hits, used = discover_sources(q, num_results=num_results, provider=provider)
    if not hits:
        return raw_text, [], used
    section = format_source_bundle_section(hits, provider=used)
    enriched = f"{raw_text.rstrip()}\n\n{section}"
    return enriched, hits, used
