"""Fetch public web pages by URL (no API key)."""

from __future__ import annotations

from typing import Any

import httpx

from ._common import html_to_text, normalize_hit

_DEFAULT_HEADERS = {
    "User-Agent": "ErrorlogyIngest/1.0 (+https://errorlogy.local)",
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
}


def is_configured() -> bool:
    return True


def fetch_url(url: str, *, timeout: float = 30.0) -> dict[str, Any] | None:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        raise ValueError("url must start with http:// or https://")

    with httpx.Client(timeout=timeout, follow_redirects=True, headers=_DEFAULT_HEADERS) as client:
        resp = client.get(url)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        body = resp.text

    if "html" in content_type or "<html" in body[:500].lower():
        text = html_to_text(body)
        title = _title_from_html(body) or url
    else:
        text = body.strip()
        title = url

    return normalize_hit(
        source="url",
        source_type="web_page",
        url=url,
        title=title,
        text=text,
    )


def _title_from_html(html: str) -> str:
    import re

    m = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
    return m.group(1).strip() if m else ""
