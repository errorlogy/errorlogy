"""OIG report list fetcher — adapted from democracy-monitor (MIT)."""

from __future__ import annotations

import re
from typing import Any

import httpx

from ._common import html_to_text, normalize_hit

_OFFICES: dict[str, dict[str, str]] = {
    "doj": {
        "base_url": "https://oig.justice.gov",
        "reports_path": "/reports",
        "agency": "DOJ Office of the Inspector General",
        "source_environment": "audit_oversight",
    },
}
_DEFAULT_HEADERS = {
    "User-Agent": "ErrorlogyIngest/1.0 (civic monitoring)",
    "Accept": "text/html",
}


def is_configured() -> bool:
    return True


def fetch_recent(
    *,
    limit: int = 5,
    office: str = "doj",
    timeout: float = 30.0,
    source_environment: str | None = None,
) -> list[dict[str, Any]]:
    """Scrape recent OIG report listings (DOJ OIG by default)."""
    cfg = _OFFICES.get(office)
    if not cfg:
        return []

    wms_env = source_environment or cfg["source_environment"]
    page_url = f"{cfg['base_url']}{cfg['reports_path']}"

    with httpx.Client(timeout=timeout, follow_redirects=True, headers=_DEFAULT_HEADERS) as client:
        resp = client.get(page_url)
        resp.raise_for_status()
        reports = _parse_doj_reports(resp.text, base_url=cfg["base_url"])

        out: list[dict[str, Any]] = []
        for report in reports[:limit]:
            text = _fetch_report_text(client, report["url"], report=report)
            hit = normalize_hit(
                source="oig",
                source_type="gov_scrape",
                url=report["url"],
                title=report["title"],
                text=text,
                country="USA",
                doc_id=f"oig-{office}-{report['published_at'][:10]}-{hash(report['url']) & 0xFFFF:x}",
                source_environment=wms_env,
                agency=report.get("component") or cfg["agency"],
            )
            if hit:
                out.append(hit)
        return out


def _parse_doj_reports(html: str, *, base_url: str) -> list[dict[str, str]]:
    reports: list[dict[str, str]] = []
    blocks = re.findall(r'<div class="views-row">.*?</div>\s*</div>\s*</div>', html, re.DOTALL)
    if not blocks:
        blocks = re.findall(r'<div class="views-row">.*?</div>', html, re.DOTALL)

    for block in blocks:
        date_match = re.search(r'<time[^>]+datetime="([^"]+)"', block)
        title_match = re.search(
            r'class="views-field-title[^"]*".*?<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>',
            block,
            re.DOTALL,
        )
        if not date_match or not title_match:
            continue
        href, title = title_match.group(1), title_match.group(2).strip()
        url = href if href.startswith("http") else f"{base_url}{href}"
        type_match = re.search(r"Type:\s*</span>\s*<span[^>]*>([^<]+)</span>", block)
        component_match = re.search(
            r'class="views-field-field-doj-component[^"]*".*?<div class="field-content">([^<]+)</div>',
            block,
            re.DOTALL,
        )
        reports.append({
            "title": title,
            "url": url,
            "published_at": date_match.group(1),
            "report_type": (type_match.group(1).strip() if type_match else "Report"),
            "component": (component_match.group(1).strip() if component_match else "DOJ OIG"),
        })
    return reports


def _fetch_report_text(client: httpx.Client, url: str, *, report: dict[str, str]) -> str:
    header = (
        f"{report['title']}. {report['report_type']} from {report['component']}. "
        f"Published {report['published_at'][:10]}."
    )
    try:
        resp = client.get(url)
        if resp.is_success:
            page = html_to_text(resp.text)
            if page:
                return f"{header}\n\n{page}"
    except Exception:
        pass
    return header + " Inspector General oversight report listing for government accountability review."
