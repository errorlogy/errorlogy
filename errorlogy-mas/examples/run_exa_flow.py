#!/usr/bin/env python3
"""
End-to-end Exa → source bundle → MAS pipeline (engine-only by default).

Uses UK Post Office Horizon as the demo case — not Challenger.
Challenger remains the repo's offline engine smoke default in run_challenger.py.

  python examples/run_exa_flow.py
  python examples/run_exa_flow.py --no-enrich   # skip Exa, engine-only on seed text
  python examples/run_exa_flow.py --ingest      # also persist discovered docs via ingest
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if sys.platform == "win32":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from mas.ingest import enrich_source_bundle, ingest_document
from mas.ingest.fetchers import exa as exa_fetcher
from mas.orchestrator import Orchestrator
from rich.console import Console
from rich.panel import Panel

console = Console()

HORIZON_SEED = """
UK Post Office Limited prosecuted hundreds of sub-postmasters for theft and false accounting
based on shortfalls shown by the Horizon IT accounting system. Sub-postmasters reported bugs
and accounting errors for years; Post Office management dismissed complaints and pursued
prosecutions. A public inquiry found systematic denial, cover-up, and failure of oversight
over more than a decade.
""".strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Exa source discovery + MAS engine flow")
    parser.add_argument("--no-enrich", action="store_true", help="Skip Exa discovery")
    parser.add_argument("--ingest", action="store_true", help="Store discovered hits in ingest DB")
    parser.add_argument("--num-results", type=int, default=2)
    args = parser.parse_args()

    case_id = "GB-POL-1999-HORIZON-01"
    title = "UK Post Office Horizon IT Scandal"
    country = "UK"
    year = 1999
    raw_text = HORIZON_SEED
    discovery_meta: dict = {"provider": None, "hits": 0, "urls": []}

    console.print(Panel.fit(
        "[bold]Errorlogy MAS — Exa integration flow[/bold]\n"
        f"Case: [cyan]{case_id}[/cyan]\n"
        f"Exa configured: {'yes' if exa_fetcher.is_configured() else 'no'}",
        border_style="cyan",
    ))

    if not args.no_enrich:
        if not exa_fetcher.is_configured():
            console.print("[yellow]EXA_API_KEY not set — continuing with seed text only.[/yellow]")
        else:
            console.print("\n[bold]Step 1:[/bold] Exa source discovery…")
            raw_text, hits, provider = enrich_source_bundle(
                raw_text,
                title=title,
                country=country,
                year=year,
                num_results=args.num_results,
            )
            discovery_meta = {
                "provider": provider,
                "hits": len(hits),
                "urls": [h.get("url", "") for h in hits if h.get("url")],
            }
            console.print(f"  provider={provider} hits={len(hits)}")
            for h in hits:
                console.print(f"  - {h.get('title', '')[:70]}")

            if args.ingest and hits:
                console.print("\n[bold]Step 1b:[/bold] Ingest discovered documents…")
                for hit in hits:
                    ingest_document(
                        source=hit.get("source", "exa"),
                        source_type=hit.get("source_type", "web_search"),
                        url=hit.get("url", ""),
                        title=hit.get("title", ""),
                        country=hit.get("country", country),
                        text=hit["text"],
                        doc_id=hit.get("doc_id"),
                        auto_analyze=False,
                    )
                console.print(f"  stored {len(hits)} raw document(s)")

    console.print("\n[bold]Step 2:[/bold] Engine-only MAS pipeline (Scout skipped)…")
    orch = Orchestrator(init_llm=False)
    analysis = orch.run_from_text(
        case_id=case_id,
        raw_text=raw_text,
        title=title,
        country=country,
        year=year,
        engine_only=True,
        verbose=True,
    )
    if discovery_meta.get("hits"):
        meta = dict(analysis.metadata or {})
        meta["source_discovery"] = discovery_meta
        analysis.metadata = meta

    console.print("\n[green]Done.[/green]")
    console.print(f"  PNO: {analysis.pno.dominant_pno}")
    console.print(f"  CEP: {analysis.wms.cep:.3f}")
    console.print(f"  CAT: {analysis.cat.catastrophe_hypothesis}")
    if analysis.top_modes:
        top = analysis.top_modes[0]
        console.print(f"  Top mode: {top.mode_id} μ={top.mu:.2f}")

    out = ROOT / "examples" / "exa_flow_output.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(analysis.model_dump(), f, indent=2, ensure_ascii=False)
    console.print(f"\n[dim]Saved → {out}[/dim]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
