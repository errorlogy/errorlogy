"""CourtListener REST fetcher — adapted from democracy-monitor (MIT)."""

from __future__ import annotations

import os
import re
import time
from typing import Any

import httpx

from mas import config

from ._common import MIN_TEXT_LEN, normalize_hit

_CL_BASE = "https://www.courtlistener.com"
_CL_API = f"{_CL_BASE}/api/rest/v4"
_DEFAULT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "ErrorlogyIngest/1.0 (civic monitoring)",
}
_RATE_LIMIT_S = 2.0
_PROCEDURAL_TYPES = frozenset({"050addendum", "060remittitur", "090onmotiontostrike"})


def is_configured() -> bool:
    return True


def fetch_recent(
    *,
    limit: int = 5,
    search_type: str = "r",
    nature_of_suit: str | None = None,
    query: str | None = None,
    timeout: float = 30.0,
    source_environment: str = "legal_judicial",
) -> list[dict[str, Any]]:
    """Fetch recent CourtListener docket search results."""
    params: dict[str, str] = {
        "type": search_type,
        "order_by": "-dateFiled",
    }
    if nature_of_suit:
        params["nature_of_suit"] = nature_of_suit
    if query:
        params["q"] = query

    headers = _auth_headers()
    out: list[dict[str, Any]] = []

    with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
        resp = client.get(f"{_CL_API}/search/", params=params)
        resp.raise_for_status()
        results = resp.json().get("results", [])

        for doc in results[:limit]:
            hit = _docket_to_hit(doc, client=client, source_environment=source_environment)
            if hit:
                out.append(hit)
            time.sleep(_RATE_LIMIT_S)

    return out


def _auth_headers() -> dict[str, str]:
    headers = dict(_DEFAULT_HEADERS)
    token = getattr(config, "COURTLISTENER_API_TOKEN", "") or os.environ.get("COURTLISTENER_API_TOKEN", "")
    if token:
        headers["Authorization"] = f"Token {token}"
    return headers


def _docket_to_hit(
    doc: dict[str, Any],
    *,
    client: httpx.Client,
    source_environment: str,
) -> dict[str, Any] | None:
    title = (doc.get("caseName") or "(untitled case)").strip()
    raw_url = doc.get("docket_absolute_url") or ""
    url = raw_url if raw_url.startswith("http") else f"{_CL_BASE}{raw_url}" if raw_url else ""
    court = (doc.get("court") or "Federal Court").strip()
    cause = (doc.get("cause") or "").strip()
    suit_nature = (doc.get("suitNature") or "").strip()
    docket_number = (doc.get("docketNumber") or "").strip()
    docket_id = doc.get("docket_id")

    text = ""
    if docket_id:
        text = _fetch_opinion_text(client, int(docket_id))
    if not text:
        text = _build_summary_text(
            title=title,
            court=court,
            cause=cause,
            suit_nature=suit_nature,
            docket_number=docket_number,
            date_filed=doc.get("dateFiled") or "",
        )

    doc_id = f"cl-{docket_id}" if docket_id else None
    return normalize_hit(
        source="courtlistener",
        source_type="gov_api",
        url=url,
        title=title,
        text=text,
        country="USA",
        doc_id=doc_id,
        source_environment=source_environment,
        agency=court,
    )


def _build_summary_text(
    *,
    title: str,
    court: str,
    cause: str,
    suit_nature: str,
    docket_number: str,
    date_filed: str,
) -> str:
    parts = [
        f"Federal court docket: {title}.",
        f"Court: {court}.",
    ]
    if docket_number:
        parts.append(f"Docket number: {docket_number}.")
    if date_filed:
        parts.append(f"Date filed: {date_filed}.")
    if cause:
        parts.append(f"Cause: {cause}.")
    if suit_nature:
        parts.append(f"Nature of suit: {suit_nature}.")
    text = " ".join(parts)
    if len(text) < MIN_TEXT_LEN:
        filler = "Federal court public docket record for oversight and legal-judicial monitoring."
        text = f"{text} {filler}"
    return text[:12000]


def _fetch_opinion_text(client: httpx.Client, docket_id: int) -> str:
    try:
        cluster_params = {
            "docket": str(docket_id),
            "fields": "id,case_name,date_filed,sub_opinions",
            "page_size": "1",
            "order_by": "-date_filed",
        }
        resp = client.get(f"{_CL_API}/clusters/", params=cluster_params)
        if not resp.is_success:
            return ""
        cluster = (resp.json().get("results") or [None])[0]
        if not cluster:
            return ""

        sub_opinions = cluster.get("sub_opinions") or []
        texts: list[str] = []
        for sub_url in sub_opinions[:3]:
            op_id = _extract_opinion_id(sub_url)
            if not op_id:
                continue
            op_resp = client.get(
                f"{_CL_API}/opinions/{op_id}/",
                params={"fields": "plain_text,type"},
            )
            if not op_resp.is_success:
                continue
            op = op_resp.json()
            if op.get("type") in _PROCEDURAL_TYPES:
                continue
            plain = (op.get("plain_text") or "").replace("\0", "").strip()
            if plain:
                texts.append(plain)
            time.sleep(_RATE_LIMIT_S)

        return "\n\n".join(texts)
    except Exception:
        return ""


def _extract_opinion_id(url: str) -> str | None:
    match = re.search(r"/opinions/(\d+)/", url or "")
    return match.group(1) if match else None
