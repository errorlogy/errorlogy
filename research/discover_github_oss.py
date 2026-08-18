#!/usr/bin/env python3
"""Discover OSS candidates on GitHub for the Errorlogy funnel (Discover stage).

Uses GitHub REST API search/repositories. Dry-run by default; pass --apply to
merge new rows into research/oss-candidates.yaml.

Rate limits (search API):
  - Unauthenticated: ~10 requests/minute
  - GITHUB_TOKEN set: ~30 requests/minute

No token is required for occasional manual runs; set GITHUB_TOKEN for batch/CI.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]


def _load_repo_dotenv() -> None:
    """Load KEY=value lines from repo root .env if vars not already in environ."""
    path = ROOT / ".env"
    if not path.is_file():
        return
    try:
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    except OSError:
        pass

TRACKER = ROOT / "research" / "oss-candidates.yaml"
API_BASE = "https://api.github.com"

# Tailored to Errorlogy MVP gaps (ingest, engine-adjacent libs, GUI codegen, infra).
SEARCH_PROFILES: list[dict[str, str]] = [
    {
        "query": "hawkes process python",
        "category": "time-series",
        "target_area": "mas",
    },
    {
        "query": "fastapi multi-agent",
        "category": "agent-orchestration",
        "target_area": "mas",
    },
    {
        "query": "openapi typescript codegen",
        "category": "api-codegen",
        "target_area": "gui",
    },
    {
        "query": "topic:forecasting language:python stars:>50",
        "category": "forecasting",
        "target_area": "mas",
    },
    {
        "query": "topic:change-point-detection language:python",
        "category": "change-point",
        "target_area": "mas",
    },
    {
        "query": "complex event processing python",
        "category": "cep",
        "target_area": "mas",
    },
    {
        "query": "rss feed ingest python stars:>20",
        "category": "ingest",
        "target_area": "mas",
    },
    {
        "query": "governance analytics dashboard open source",
        "category": "governance",
        "target_area": "gui",
    },
    {
        "query": "opentelemetry fastapi python",
        "category": "observability",
        "target_area": "infra",
    },
    {
        "query": "time series forecasting python stars:>100",
        "category": "forecasting",
        "target_area": "mas",
    },
]

EMPTY_SCORE = {
    "coupling": None,
    "duplication": None,
    "test_safety": None,
    "blast_radius": None,
    "license": None,
    "maintenance": None,
    "engine_llm_fit": None,
    "old_sketch_risk": None,
    "total": None,
}


def normalize_repo_url(url: str) -> str:
    u = url.strip().rstrip("/").lower()
    if u.endswith(".git"):
        u = u[:-4]
    return u


def slug_id(full_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", full_name.lower()).strip("-")
    return slug or "unknown-repo"


def github_request(path: str, token: str | None) -> tuple[dict[str, Any], dict[str, str]]:
    url = f"{API_BASE}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "errorlogy-oss-discover",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            hdrs = {k.lower(): v for k, v in resp.headers.items()}
            return json.loads(body), hdrs
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(err_body)
        except json.JSONDecodeError:
            payload = {"message": err_body}
        raise RuntimeError(f"GitHub API {exc.code}: {payload.get('message', err_body)}") from exc


def wait_for_rate_limit(headers: dict[str, str]) -> None:
    remaining = headers.get("x-ratelimit-remaining")
    reset = headers.get("x-ratelimit-reset")
    if remaining is not None and int(remaining) <= 1 and reset:
        sleep_for = max(0, int(reset) - int(time.time()) + 1)
        if sleep_for > 0:
            print(f"Rate limit low; sleeping {sleep_for}s until reset...", file=sys.stderr)
            time.sleep(sleep_for)


def search_repositories(
    query: str,
    *,
    token: str | None,
    per_page: int,
    max_pages: int,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    last_headers: dict[str, str] = {}

    for page in range(1, max_pages + 1):
        params = urllib.parse.urlencode(
            {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": per_page,
                "page": page,
            }
        )
        payload, last_headers = github_request(f"/search/repositories?{params}", token)
        items = payload.get("items") or []
        results.extend(items)
        if len(items) < per_page:
            break
        wait_for_rate_limit(last_headers)
        time.sleep(0.5)

    return results


def existing_repo_urls(candidates: list[dict[str, Any]]) -> set[str]:
    urls: set[str] = set()
    for c in candidates:
        if c.get("repo_url"):
            urls.add(normalize_repo_url(str(c["repo_url"])))
    return urls


def build_candidate(item: dict[str, Any], profile: dict[str, str], discovered_at: str) -> dict[str, Any]:
    full_name = item.get("full_name") or item.get("name") or "unknown/unknown"
    repo_url = item.get("html_url") or f"https://github.com/{full_name}"
    description = (item.get("description") or "").strip()
    stars = item.get("stargazers_count")
    license_spdx = (item.get("license") or {}).get("spdx_id")
    pushed_at = item.get("pushed_at") or ""

    notes_lines = [
        f"Автообнаружение GitHub ({profile['query']}).",
        f"Звёзды: {stars}; последний push: {pushed_at or '—'}.",
    ]
    if license_spdx:
        notes_lines.append(f"Лицензия (API): {license_spdx}.")
    if description:
        notes_lines.append(f"Описание: {description}")

    return {
        "id": slug_id(full_name),
        "name": item.get("name") or full_name.split("/")[-1],
        "repo_url": repo_url,
        "category": profile["category"],
        "target_area": profile["target_area"],
        "stage": "discover",
        "source": "github-search",
        "search_query": profile["query"],
        "discovered_at": discovered_at,
        "github_stars": stars,
        "decision": "pending",
        "review_after": None,
        "score": dict(EMPTY_SCORE),
        "notes_ru": "\n".join(notes_lines) + "\n",
    }


def load_tracker(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Tracker not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8-sig"))


def merge_candidates(
    data: dict[str, Any],
    discovered: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates = list(data.get("candidates") or [])
    known = existing_repo_urls(candidates)
    added: list[dict[str, Any]] = []

    for cand in discovered:
        key = normalize_repo_url(str(cand["repo_url"]))
        if key in known:
            continue
        # Avoid id collision with suffix.
        base_id = cand["id"]
        existing_ids = {c.get("id") for c in candidates}
        if base_id in existing_ids:
            suffix = 2
            while f"{base_id}-{suffix}" in existing_ids:
                suffix += 1
            cand["id"] = f"{base_id}-{suffix}"
        candidates.append(cand)
        known.add(key)
        existing_ids.add(cand["id"])
        added.append(cand)

    data["candidates"] = candidates
    return added, candidates


def format_candidate_block(cand: dict[str, Any]) -> str:
    """Render one list item; keeps top-of-file comments when appending."""
    body = yaml.safe_dump(
        cand,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=120,
    ).rstrip()
    return "\n".join(f"  {line}" if line else "" for line in body.splitlines())


def append_candidates(path: Path, new_candidates: list[dict[str, Any]]) -> None:
    if not new_candidates:
        return
    text = path.read_text(encoding="utf-8-sig").rstrip() + "\n"
    for cand in new_candidates:
        text += "\n" + format_candidate_block(cand) + "\n"
    path.write_text(text, encoding="utf-8")


def print_summary(added: list[dict[str, Any]], skipped: int) -> None:
    print(f"\nNew candidates: {len(added)} | Skipped (duplicate): {skipped}")
    for c in added:
        print(f"  + {c['id']:40} {c['repo_url']}")
    if not added:
        print("  (none)")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="GitHub OSS discover for Errorlogy funnel")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write merged candidates to oss-candidates.yaml (default: dry-run)",
    )
    parser.add_argument("--tracker", type=Path, default=TRACKER)
    parser.add_argument(
        "--max-per-query",
        type=int,
        default=5,
        help="Max repos to take per search query (default: 5)",
    )
    parser.add_argument(
        "--query",
        action="append",
        dest="queries",
        metavar="Q",
        help="Run only this search query (repeatable); default: built-in profile list",
    )
    parser.add_argument(
        "--list-queries",
        action="store_true",
        help="Print built-in search profiles and exit",
    )
    args = parser.parse_args()

    _load_repo_dotenv()

    if args.list_queries:
        for p in SEARCH_PROFILES:
            print(f"{p['query']}\t→ {p['category']} / {p['target_area']}")
        return 0

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        print("Using GITHUB_TOKEN (authenticated search rate limits).")
    else:
        print("No GITHUB_TOKEN — unauthenticated limits (~10 search req/min).")

    profiles = SEARCH_PROFILES
    if args.queries:
        qset = set(args.queries)
        profiles = [p for p in SEARCH_PROFILES if p["query"] in qset]
        missing = qset - {p["query"] for p in profiles}
        for q in sorted(missing):
            profiles.append({"query": q, "category": "uncategorized", "target_area": "mas"})

    data = load_tracker(args.tracker)
    known = existing_repo_urls(data.get("candidates") or [])
    discovered_at = date.today().isoformat()

    collected: list[dict[str, Any]] = []
    skipped = 0

    print(f"Running {len(profiles)} search profile(s), max {args.max_per_query} repo(s) each...")
    for profile in profiles:
        query = profile["query"]
        print(f"\n→ {query}")
        try:
            items = search_repositories(
                query,
                token=token,
                per_page=min(30, max(1, args.max_per_query)),
                max_pages=1,
            )
        except RuntimeError as exc:
            print(f"  ! {exc}", file=sys.stderr)
            continue

        taken = 0
        for item in items:
            if taken >= args.max_per_query:
                break
            url = normalize_repo_url(str(item.get("html_url") or ""))
            if not url:
                continue
            if url in known or any(
                normalize_repo_url(str(c.get("repo_url", ""))) == url for c in collected
            ):
                skipped += 1
                continue
            cand = build_candidate(item, profile, discovered_at)
            collected.append(cand)
            taken += 1
            print(f"  + {cand['id']} ({item.get('stargazers_count', '?')}★)")

    added, _ = merge_candidates(data, collected)
    print_summary(added, skipped)

    if args.apply:
        if added:
            append_candidates(args.tracker, added)
            print(f"\nWrote {len(added)} new candidate(s) to {args.tracker}")
        else:
            print("\n--apply: no new candidates; tracker unchanged.")
    else:
        print("\nDry-run only. Re-run with --apply to update oss-candidates.yaml.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
