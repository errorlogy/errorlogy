"""Fetch governance + media signals and ingest into Errorlogy DB."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mas.db import init_db
from mas.ingest import ingest_status, run_exa_fetch, run_fetch_all, run_rss_fetch, run_us_gov_fetch, run_web_search


def main() -> None:
    parser = argparse.ArgumentParser(description="Gov/media ingest (RSS + web search)")
    parser.add_argument("--no-analyze", action="store_true", help="Store only, skip MAS")
    parser.add_argument("--num-results", type=int, default=2)
    parser.add_argument("--rss-only", action="store_true")
    parser.add_argument("--web-only", action="store_true")
    parser.add_argument("--exa-only", action="store_true")
    parser.add_argument("--us-gov-only", action="store_true")
    parser.add_argument("-q", "--query", action="append", help="Extra search query")
    args = parser.parse_args()

    init_db()
    auto = not args.no_analyze

    if args.exa_only:
        result = run_exa_fetch(queries=args.query, num_results=args.num_results, auto_analyze=auto)
        if not result.get("ok"):
            print(f"ERROR: {result.get('error')}")
            sys.exit(1)
        print(f"[exa] Ingested: {result['ingested']}")
    elif args.us_gov_only:
        result = run_us_gov_fetch(limit_per_source=args.num_results, auto_analyze=auto)
        if not result.get("ok"):
            print(f"ERROR: {result.get('error')}")
            sys.exit(1)
        print(f"[us-gov] Ingested: {result['ingested']} from {result.get('sources_run', 0)} sources")
    elif args.rss_only:
        result = run_rss_fetch(auto_analyze=auto)
        print(f"[rss] Ingested: {result.get('ingested', 0)}")
    elif args.web_only:
        result = run_web_search(queries=args.query, num_results=args.num_results, auto_analyze=auto)
        if not result.get("ok"):
            print(f"ERROR: {result.get('error')}")
            sys.exit(1)
        print(f"[{result.get('provider')}] Ingested: {result['ingested']}")
    else:
        result = run_fetch_all(num_results=args.num_results, auto_analyze=auto)
        print(f"[all] Ingested: {result['ingested']}")
        for name, part in result.get("parts", {}).items():
            if part.get("ok"):
                extra = f" via {part['provider']}" if part.get("provider") else ""
                print(f"  - {name}: {part.get('ingested', 0)}{extra}")

    status = ingest_status()
    print(f"Total docs: {status['documents_total']} | signals: {status['signals_total']}")
    print(f"Fetchers: {status.get('fetchers')}")
    print(f"Sources: {status['sources']}")


if __name__ == "__main__":
    main()
