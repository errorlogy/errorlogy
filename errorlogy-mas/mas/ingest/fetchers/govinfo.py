"""GovInfo API fetcher — adapted from democracy-monitor (MIT)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import httpx

from mas import config

from ._common import html_to_text, normalize_hit

_API_BASE = "https://api.govinfo.gov"
_DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "ErrorlogyIngest/1.0 (civic monitoring)",
}


def is_configured() -> bool:
    return bool(getattr(config, "GOVINFO_API_KEY", ""))


def fetch_recent(
    *,
    limit: int = 5,
    collection: str = "GAOREPORTS",
    days_back: int = 30,
    timeout: float = 30.0,
    source_environment: str = "audit_oversight",
) -> list[dict[str, Any]]:
    """Fetch recent GovInfo packages for a collection."""
    api_key = getattr(config, "GOVINFO_API_KEY", "")
    if not api_key:
        return []

    start_date = (date.today() - timedelta(days=days_back)).isoformat()
    query = f"collection:{collection} publishdate:range({start_date},)"
    body = {
        "query": query,
        "pageSize": str(max(limit, 1)),
        "offsetMark": "*",
        "sorts": [{"field": "publishdate", "sortOrder": "DESC"}],
    }

    with httpx.Client(timeout=timeout, follow_redirects=True, headers=_DEFAULT_HEADERS) as client:
        resp = client.post(f"{_API_BASE}/search?api_key={api_key}", json=body)
        resp.raise_for_status()
        results = resp.json().get("results", [])

        out: list[dict[str, Any]] = []
        for item in results[:limit]:
            hit = _result_to_hit(item, client=client, api_key=api_key, source_environment=source_environment)
            if hit:
                out.append(hit)
        return out


def _result_to_hit(
    item: dict[str, Any],
    *,
    client: httpx.Client,
    api_key: str,
    source_environment: str,
) -> dict[str, Any] | None:
    title = (item.get("title") or "(GovInfo document)").strip()
    package_id = item.get("packageId") or ""
    download = item.get("download") or {}
    url = (
        download.get("pdfLink")
        or download.get("txtLink")
        or (f"https://www.govinfo.gov/app/details/{package_id}" if package_id else "")
    )
    agency = (item.get("governmentAuthor") or ["U.S. Government"])[0]
    collection = item.get("collectionCode") or "CRPT"

    text = _fetch_package_text(client, package_id, api_key) if package_id else ""
    if not text:
        text = (
            f"{title}. Government publication from {agency}. "
            f"Collection: {collection}. Package ID: {package_id}. "
            f"Issued: {item.get('dateIssued') or 'unknown'}. "
            "Oversight and accountability document for government management error analysis."
        )

    return normalize_hit(
        source="govinfo",
        source_type="gov_api",
        url=url,
        title=title,
        text=text,
        country="USA",
        doc_id=f"gi-{package_id}" if package_id else None,
        source_environment=source_environment,
        agency=agency,
    )


def _fetch_package_text(client: httpx.Client, package_id: str, api_key: str) -> str:
    try:
        pkg_url = f"{_API_BASE}/packages/{package_id}/htm?api_key={api_key}"
        resp = client.get(pkg_url)
        if resp.is_success:
            return html_to_text(resp.text)

        granules_url = (
            f"{_API_BASE}/packages/{package_id}/granules"
            f"?offsetMark=*&pageSize=1&api_key={api_key}"
        )
        g_resp = client.get(granules_url)
        if not g_resp.is_success:
            return ""
        granule_id = (g_resp.json().get("granules") or [{}])[0].get("granuleId")
        if not granule_id:
            return ""
        g_url = f"{_API_BASE}/packages/{package_id}/granules/{granule_id}/htm?api_key={api_key}"
        g2 = client.get(g_url)
        if g2.is_success:
            return html_to_text(g2.text)
    except Exception:
        return ""
    return ""
