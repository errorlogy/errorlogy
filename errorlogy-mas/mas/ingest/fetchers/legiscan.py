"""LegiScan API fetcher — adapted from democracy-monitor (MIT)."""

from __future__ import annotations

from typing import Any

import httpx

from mas import config

from ._common import normalize_hit

_API_BASE = "https://api.legiscan.com/"
_DEFAULT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "ErrorlogyIngest/1.0 (civic monitoring)",
}


def is_configured() -> bool:
    return bool(getattr(config, "LEGISCAN_API_KEY", ""))


def fetch_recent(
    *,
    limit: int = 5,
    state: str = "US",
    timeout: float = 30.0,
    source_environment: str = "parliamentary_inquiry",
) -> list[dict[str, Any]]:
    """Fetch recent US congressional bills via LegiScan master list + getBill."""
    api_key = getattr(config, "LEGISCAN_API_KEY", "")
    if not api_key:
        return []

    with httpx.Client(timeout=timeout, follow_redirects=True, headers=_DEFAULT_HEADERS) as client:
        master = _api_get(client, api_key, op="getMasterList", state=state)
        masterlist = master.get("masterlist") or {}
        bill_ids = [
            int(entry["bill_id"])
            for key, entry in masterlist.items()
            if key.isdigit() and entry.get("bill_id")
        ][:limit]

        out: list[dict[str, Any]] = []
        for bill_id in bill_ids:
            bill_data = _api_get(client, api_key, op="getBill", id=str(bill_id))
            bill = (bill_data.get("bill") or {})
            hit = _bill_to_hit(bill, source_environment=source_environment)
            if hit:
                out.append(hit)
        return out


def _api_get(client: httpx.Client, api_key: str, **params: str) -> dict[str, Any]:
    query = {"key": api_key, **params}
    resp = client.get(_API_BASE, params=query)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "OK":
        msg = (data.get("alert") or {}).get("message", "LegiScan API error")
        raise RuntimeError(msg)
    return data


def _bill_to_hit(bill: dict[str, Any], *, source_environment: str) -> dict[str, Any] | None:
    title = (bill.get("title") or "(LegiScan bill)").strip()
    description = (bill.get("description") or "").strip()
    url = (bill.get("url") or bill.get("state_link") or "").strip()
    chamber = _infer_chamber(bill)
    text = f"{title}\n\n{description}".strip()
    if bill.get("status_date"):
        text += f"\n\nStatus date: {bill['status_date']}."
    if bill.get("bill_number"):
        text += f" Bill: {bill['bill_number']}."

    bill_id = bill.get("bill_id")
    return normalize_hit(
        source="legiscan",
        source_type="gov_api",
        url=url,
        title=title,
        text=text,
        country="USA",
        doc_id=f"ls-{bill_id}" if bill_id else None,
        source_environment=source_environment,
        agency=chamber,
    )


def _infer_chamber(bill: dict[str, Any]) -> str:
    body = (bill.get("body") or bill.get("current_body") or "").lower()
    if "senate" in body or body == "s":
        return "US Senate"
    if "house" in body or body == "h":
        return "US House"
    return "US Congress"
