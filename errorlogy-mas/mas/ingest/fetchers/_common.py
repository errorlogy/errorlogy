"""Shared helpers for ingest fetchers."""

from __future__ import annotations

import hashlib
import re
from typing import Any

MIN_TEXT_LEN = 200


def make_doc_id(prefix: str, key: str) -> str:
    digest = hashlib.sha256(key.encode()).hexdigest()[:16]
    return f"{prefix}-{digest}"


def html_to_text(html: str) -> str:
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<noscript[^>]*>.*?</noscript>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s\])\"'<>]+", text)


def normalize_hit(
    *,
    source: str,
    source_type: str,
    title: str,
    text: str,
    url: str = "",
    country: str = "",
    doc_id: str | None = None,
    source_environment: str = "",
    agency: str = "",
) -> dict[str, Any] | None:
    text = (text or "").strip()
    if len(text) < MIN_TEXT_LEN:
        return None
    url = (url or "").strip()
    title = (title or url[:80] or source).strip()
    key = url or f"{title}:{text[:120]}"
    hit: dict[str, Any] = {
        "doc_id": doc_id or make_doc_id(source, key),
        "source": source,
        "source_type": source_type,
        "url": url,
        "title": title,
        "country": country,
        "text": text[:12000],
    }
    if source_environment:
        hit["source_environment"] = source_environment
    if agency:
        hit["agency"] = agency
    return hit
