"""Federal Register API fetcher — adapted from democracy-monitor (MIT)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import httpx

from ._common import MIN_TEXT_LEN, html_to_text, normalize_hit

_API_BASE = "https://www.federalregister.gov/api/v1/documents.json"
_FIELDS = [
    "title",
    "html_url",
    "publication_date",
    "agencies",
    "type",
    "subtype",
    "action",
    "abstract",
    "raw_text_url",
    "document_number",
]
_DEFAULT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "ErrorlogyIngest/1.0 (civic monitoring)",
}


def is_configured() -> bool:
    return True


def fetch_recent(
    *,
    limit: int = 5,
    days_back: int = 30,
    timeout: float = 30.0,
    source_environment: str = "legal_judicial",
) -> list[dict[str, Any]]:
    """Fetch recent Federal Register documents."""
    date_to = date.today().isoformat()
    date_from = (date.today() - timedelta(days=days_back)).isoformat()
    params: list[tuple[str, str]] = [
        ("per_page", str(max(limit, 1))),
        ("page", "1"),
        ("order", "newest"),
        ("conditions[publication_date][gte]", date_from),
        ("conditions[publication_date][lte]", date_to),
    ]
    for field in _FIELDS:
        params.append(("fields[]", field))

    with httpx.Client(timeout=timeout, follow_redirects=True, headers=_DEFAULT_HEADERS) as client:
        resp = client.get(_API_BASE, params=params)
        resp.raise_for_status()
        data = resp.json()

        out: list[dict[str, Any]] = []
        for doc in data.get("results", [])[:limit]:
            hit = _doc_to_hit(doc, client=client, source_environment=source_environment)
            if hit:
                out.append(hit)
        return out


def _doc_to_hit(
    doc: dict[str, Any],
    *,
    client: httpx.Client,
    source_environment: str,
) -> dict[str, Any] | None:
    title = (doc.get("title") or "(Federal Register document)").strip()
    url = (doc.get("html_url") or "").strip()
    agencies = doc.get("agencies") or []
    agency = ", ".join(a.get("name", "") for a in agencies if a.get("name"))
    text = _resolve_text(doc, client=client)
    if not text:
        return None

    parts = [text]
    for label, value in (
        ("Type", doc.get("type")),
        ("Subtype", doc.get("subtype")),
        ("Action", doc.get("action")),
        ("Agency", agency),
        ("Published", doc.get("publication_date")),
    ):
        if value:
            parts.append(f"{label}: {value}")
    combined = "\n\n".join(parts)

    doc_num = doc.get("document_number") or url
    return normalize_hit(
        source="federal_register",
        source_type="gov_api",
        url=url,
        title=title,
        text=combined,
        country="USA",
        doc_id=f"fr-{doc_num}" if doc_num else None,
        source_environment=source_environment,
        agency=agency,
    )


def _resolve_text(doc: dict[str, Any], *, client: httpx.Client) -> str:
    abstract = html_to_text(doc.get("abstract") or "")
    if len(abstract) >= MIN_TEXT_LEN:
        return abstract

    raw_url = (doc.get("raw_text_url") or "").strip()
    if raw_url:
        raw_text = _fetch_page_text(client, raw_url)
        if len(raw_text) >= MIN_TEXT_LEN:
            return raw_text
        if raw_text:
            abstract = f"{abstract} {raw_text}".strip() if abstract else raw_text

    html_url = (doc.get("html_url") or "").strip()
    if html_url and len(abstract) < MIN_TEXT_LEN:
        page_text = _fetch_page_text(client, html_url)
        if page_text:
            abstract = f"{abstract} {page_text}".strip() if abstract else page_text

    return abstract


def _fetch_page_text(client: httpx.Client, url: str) -> str:
    try:
        resp = client.get(url)
        resp.raise_for_status()
        return html_to_text(resp.text)
    except Exception:
        return ""
