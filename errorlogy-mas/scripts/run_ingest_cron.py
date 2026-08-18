"""Scheduled ingest runner for Errorlogy MAS (TZ-H1-03).

Runs US gov fetchers + RSS (default) or full fetch-all on an interval.
Logs append to errorlogy-mas/logs/ingest_YYYYMMDD.log.

Usage:
  python scripts/run_ingest_cron.py                 # one shot: us-gov + rss
  python scripts/run_ingest_cron.py --all           # rss + us-gov + web search
  python scripts/run_ingest_cron.py --interval 3600 # repeat every hour (Ctrl+C to stop)
  python scripts/run_ingest_cron.py --dry-run       # log planned actions only

Windows Task Scheduler: run scripts/schedule_ingest.ps1 (hourly recommended).
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mas.db import init_db
from mas.ingest import ingest_status, run_fetch_all, run_rss_fetch, run_us_gov_fetch

LOG_DIR = Path(__file__).parent.parent / "logs"


def _log_path() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return LOG_DIR / f"ingest_{stamp}.log"


def _write_log(line: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    msg = f"[{ts}] {line}\n"
    _log_path().open("a", encoding="utf-8").write(msg)
    print(msg, end="")


def _run_once(*, fetch_all: bool, num_results: int, no_analyze: bool, dry_run: bool) -> int:
    mode = "fetch-all" if fetch_all else "us-gov+rss"
    if dry_run:
        _write_log(f"DRY-RUN would run {mode} num_results={num_results} analyze={not no_analyze}")
        return 0

    init_db()
    auto = not no_analyze
    total = 0

    if fetch_all:
        result = run_fetch_all(num_results=num_results, auto_analyze=auto)
        total = result.get("ingested", 0)
        for name, part in result.get("parts", {}).items():
            if part.get("ok"):
                _write_log(f"  {name}: ingested={part.get('ingested', 0)}")
        if result.get("errors"):
            _write_log(f"  errors: {len(result['errors'])}")
    else:
        us = run_us_gov_fetch(limit_per_source=num_results, auto_analyze=auto)
        rss = run_rss_fetch(max_items_per_feed=num_results, auto_analyze=auto)
        total = us.get("ingested", 0) + rss.get("ingested", 0)
        _write_log(
            f"  us-gov: ingested={us.get('ingested', 0)} sources={us.get('sources_run', 0)} "
            f"ok={us.get('ok')}"
        )
        _write_log(f"  rss: ingested={rss.get('ingested', 0)} ok={rss.get('ok')}")

    status = ingest_status()
    _write_log(
        f"Done {mode}: batch_ingested={total} docs_total={status['documents_total']} "
        f"signals={status['signals_total']}"
    )
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Scheduled Errorlogy ingest")
    parser.add_argument("--all", action="store_true", help="Run fetch-all (includes web search)")
    parser.add_argument("--interval", type=int, default=0, help="Repeat interval in seconds (0 = once)")
    parser.add_argument("--num-results", type=int, default=2, help="Items per source/feed")
    parser.add_argument("--no-analyze", action="store_true", help="Store documents only")
    parser.add_argument("--dry-run", action="store_true", help="Log plan without fetching")
    args = parser.parse_args()

    if args.interval < 0:
        parser.error("--interval must be >= 0")

    while True:
        _write_log("ingest cron start")
        try:
            _run_once(
                fetch_all=args.all,
                num_results=args.num_results,
                no_analyze=args.no_analyze,
                dry_run=args.dry_run,
            )
        except Exception as exc:
            _write_log(f"ERROR: {exc}")
            if args.interval <= 0:
                sys.exit(1)

        if args.interval <= 0:
            break
        _write_log(f"sleep {args.interval}s")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
