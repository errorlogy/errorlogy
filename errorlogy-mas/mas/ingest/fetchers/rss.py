"""Parse RSS/Atom feeds (no API key). Follow article URLs when summaries are too short."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

import httpx

from ._common import MIN_TEXT_LEN, html_to_text, normalize_hit
from . import url as url_fetcher

_DEFAULT_HEADERS = {"User-Agent": "ErrorlogyIngest/1.0"}


def is_configured() -> bool:
    return True


def fetch_feed(
    feed_url: str,
    *,
    max_items: int = 5,
    timeout: float = 30.0,
    follow_links: bool = True,
) -> list[dict[str, Any]]:
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=_DEFAULT_HEADERS) as client:
        resp = client.get(feed_url)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

    items = _parse_feed_items(root)
    out: list[dict[str, Any]] = []
    for item in items[:max_items]:
        title = item.get("title", "")
        link = item.get("url", "").strip()
        text = _resolve_item_text(item, follow_links=follow_links)
        hit = normalize_hit(
            source="rss",
            source_type="rss_feed",
            url=link,
            title=title,
            text=text,
            country=item.get("country", ""),
        )
        if hit:
            out.append(hit)
    return out


def _resolve_item_text(item: dict[str, str], *, follow_links: bool) -> str:
    text = item.get("text", "")
    if "<" in text and ">" in text:
        text = html_to_text(text)
    text = text.strip()

    link = item.get("url", "").strip()
    if not follow_links or len(text) >= MIN_TEXT_LEN or not link.startswith("http"):
        return text

    try:
        fetched = url_fetcher.fetch_url(link)
    except Exception:
        return text

    if not fetched:
        return text

    page_text = (fetched.get("text") or "").strip()
    if len(page_text) >= MIN_TEXT_LEN:
        return page_text
    if page_text:
        return f"{text} {page_text}".strip() if text else page_text
    return text


def _parse_feed_items(root: ET.Element) -> list[dict[str, str]]:
    tag = _strip_ns(root.tag).lower()
    if tag == "rss":
        return [_rss_item(el) for el in root.findall(".//item")]
    if tag == "feed":
        return [_atom_entry(el) for el in root.findall("{*}entry")]
    if root.find(".//item") is not None:
        return [_rss_item(el) for el in root.findall(".//item")]
    if root.find("{*}entry") is not None:
        return [_atom_entry(el) for el in root.findall("{*}entry")]
    return []


def _rss_item(el: ET.Element) -> dict[str, str]:
    return {
        "title": _text(el, "title"),
        "url": _text(el, "link") or _attr(el, "link", "href"),
        "text": _text(el, "description") or _text(el, "content:encoded") or _text(el, "summary"),
        "country": "",
    }


def _atom_entry(el: ET.Element) -> dict[str, str]:
    link = ""
    for lnk in el.findall("{*}link"):
        if lnk.attrib.get("rel", "alternate") in ("alternate", ""):
            link = lnk.attrib.get("href", "")
            break
    return {
        "title": _text(el, "title"),
        "url": link,
        "text": _text(el, "summary") or _text(el, "content"),
        "country": "",
    }


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _text(el: ET.Element, name: str) -> str:
    for child in el:
        if _strip_ns(child.tag) == name.split(":")[-1]:
            return (child.text or "").strip()
    return ""


def _attr(el: ET.Element, name: str, attr: str) -> str:
    for child in el:
        if _strip_ns(child.tag) == name:
            return child.attrib.get(attr, "")
    return ""
