"""Ingestion layer — raw documents, auto-analyze, signal time series."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .. import db as case_db
from ..config import EXA_AGENT_MODE, EXA_PREFERRED, EXA_SEARCH_TYPE
from ..orchestrator import Orchestrator
from .fetchers import (
    courtlistener as courtlistener_fetcher,
    exa as exa_fetcher,
    federal_register as federal_register_fetcher,
    gemini_search,
    govinfo as govinfo_fetcher,
    legiscan as legiscan_fetcher,
    oig as oig_fetcher,
    openrouter_search,
    rss as rss_fetcher,
    url as url_fetcher,
)

_QUERIES_PATH = Path(__file__).parent.parent.parent / "data" / "ingest_queries.json"
_FEEDS_PATH = Path(__file__).parent.parent.parent / "data" / "ingest_feeds.json"
_US_SOURCES_PATH = Path(__file__).parent.parent.parent / "data" / "ingest_sources_us.json"
_orchestrator: Orchestrator | None = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_orch(*, init_llm: bool = True) -> Orchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator(init_llm=init_llm)
    return _orchestrator


def _guess_country(text: str, title: str) -> str:
    combined = f"{title} {text}".lower()
    hints = [
        ("united states", "USA"), ("u.s.", "USA"), ("nasa", "USA"), ("congress", "USA"),
        ("united kingdom", "UK"), ("post office", "UK"), ("parliament", "UK"),
        ("european union", "EU"), ("france", "France"), ("germany", "Germany"),
        ("japan", "Japan"), ("china", "China"), ("russia", "Russia"), ("ukraine", "Ukraine"),
    ]
    for needle, country in hints:
        if needle in combined:
            return country
    return ""


def _guess_year(text: str) -> int:
    years = [int(y) for y in re.findall(r"\b(20\d{2}|19\d{2})\b", text)]
    return max(years) if years else 0


def _load_queries() -> list[str]:
    if _QUERIES_PATH.exists():
        qdata = json.loads(_QUERIES_PATH.read_text(encoding="utf-8"))
        return qdata.get("gov_management", []) + qdata.get("media_signals", [])
    return ["government investigation regulatory failure report"]


def _load_feeds() -> list[dict[str, str]]:
    if _FEEDS_PATH.exists():
        data = json.loads(_FEEDS_PATH.read_text(encoding="utf-8"))
        return data.get("feeds", [])
    return []


def _load_us_sources() -> list[dict[str, Any]]:
    if _US_SOURCES_PATH.exists():
        data = json.loads(_US_SOURCES_PATH.read_text(encoding="utf-8"))
        return data.get("sources", [])
    return []


_US_FETCHERS: dict[str, Any] = {
    "federal_register": federal_register_fetcher,
    "courtlistener": courtlistener_fetcher,
    "govinfo": govinfo_fetcher,
    "oig": oig_fetcher,
    "legiscan": legiscan_fetcher,
}


def fetcher_status() -> dict[str, bool]:
    us_gov = us_gov_fetcher_status()
    return {
        "url": url_fetcher.is_configured(),
        "rss": rss_fetcher.is_configured(),
        "openrouter": openrouter_search.is_configured(),
        "gemini": gemini_search.is_configured(),
        "exa": exa_fetcher.is_configured(),
        "federal_register": us_gov.get("federal_register", False),
        "courtlistener": us_gov.get("courtlistener_recap", False),
        "govinfo": us_gov.get("govinfo_gao", False) or us_gov.get("govinfo_crpt", False),
        "oig": us_gov.get("oig_doj", False),
        "legiscan": us_gov.get("legiscan_us", False),
    }


def us_gov_fetcher_status() -> dict[str, bool]:
    """Per-source ON/OFF from ingest_sources_us.json."""
    status: dict[str, bool] = {}
    for src in _load_us_sources():
        fetcher_name = src.get("fetcher", "")
        module = _US_FETCHERS.get(fetcher_name)
        if not module:
            status[src.get("id", fetcher_name)] = False
            continue
        configured = module.is_configured()
        if src.get("requires_key") and not configured:
            status[src.get("id", fetcher_name)] = False
        else:
            status[src.get("id", fetcher_name)] = True
    return status


def _pick_web_search_provider() -> str:
    if EXA_PREFERRED and exa_fetcher.is_configured():
        return "exa"
    if openrouter_search.is_configured():
        return "openrouter"
    if gemini_search.is_configured():
        return "gemini"
    if exa_fetcher.is_configured():
        return "exa"
    return ""


def _search_hits(provider: str, query: str, *, num_results: int) -> list[dict[str, Any]]:
    if provider == "openrouter":
        return openrouter_search.search(query, num_results=num_results)
    if provider == "gemini":
        return gemini_search.search(query, num_results=num_results)
    if provider == "exa":
        return exa_fetcher.search(query, num_results=num_results)
    raise RuntimeError("No web search provider configured")


def _ingest_hits(
    hits: list[dict[str, Any]],
    *,
    auto_analyze: bool = True,
    seen_urls: set[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ingested: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    seen = seen_urls if seen_urls is not None else set()

    for hit in hits:
        url = hit.get("url", "")
        if url and url in seen:
            continue
        if url:
            seen.add(url)
        try:
            r = ingest_document(
                source=hit.get("source", "unknown"),
                source_type=hit.get("source_type", "web"),
                url=url,
                title=hit.get("title", ""),
                text=hit["text"],
                country=hit.get("country", ""),
                doc_id=hit.get("doc_id"),
                auto_analyze=auto_analyze,
                structure_only=True,
                source_environment=hit.get("source_environment", ""),
                agency=hit.get("agency", ""),
            )
            ingested.append(r)
        except Exception as exc:
            errors.append({"url": url or hit.get("title"), "error": str(exc)})

    return ingested, errors


def ingest_document(
    *,
    source: str,
    text: str,
    title: str = "",
    url: str = "",
    country: str = "",
    source_type: str = "manual",
    doc_id: str | None = None,
    auto_analyze: bool = True,
    structure_only: bool = True,
    source_environment: str = "",
    agency: str = "",
) -> dict[str, Any]:
    """Store raw document; optionally run MAS pipeline."""
    if not text.strip():
        raise ValueError("text is required")

    doc_id = doc_id or f"doc-{uuid.uuid4().hex[:12]}"
    title = title or doc_id
    country = country or _guess_country(text, title)
    year = _guess_year(text)

    case_db.save_raw_document(
        doc_id=doc_id,
        source=source,
        source_type=source_type,
        url=url,
        title=title,
        country=country,
        text=text,
        status="pending" if auto_analyze else "stored",
    )

    result: dict[str, Any] = {
        "doc_id": doc_id,
        "status": "stored",
        "country": country,
        "auto_analyze": auto_analyze,
    }

    if auto_analyze:
        analysis = _analyze_document(
            doc_id=doc_id,
            text=text,
            title=title,
            country=country,
            year=year,
            structure_only=structure_only,
            source_environment=source_environment,
            agency=agency,
        )
        result["status"] = "analyzed"
        result["case_id"] = analysis["case_id"]
        result["cep"] = analysis.get("cep")
        result["cat"] = analysis.get("cat")

    return result


def ingest_batch(
    documents: list[dict[str, Any]],
    *,
    auto_analyze: bool = True,
    structure_only: bool = True,
) -> dict[str, Any]:
    """Ingest pre-fetched documents (e.g. from Cursor Exa MCP)."""
    ingested = []
    errors = []
    for doc in documents:
        text = (doc.get("text") or "").strip()
        if not text:
            errors.append({"title": doc.get("title"), "error": "text is required"})
            continue
        try:
            r = ingest_document(
                source=doc.get("source", "mcp"),
                source_type=doc.get("source_type", "mcp_bridge"),
                url=doc.get("url", ""),
                title=doc.get("title", ""),
                country=doc.get("country", ""),
                text=text,
                doc_id=doc.get("doc_id"),
                auto_analyze=auto_analyze,
                structure_only=structure_only,
                source_environment=doc.get("source_environment", ""),
                agency=doc.get("agency", ""),
            )
            ingested.append(r)
        except Exception as exc:
            errors.append({"title": doc.get("title"), "error": str(exc)})

    return {
        "ok": True,
        "ingested": len(ingested),
        "documents": ingested,
        "errors": errors,
    }


def ingest_url(
    url: str,
    *,
    auto_analyze: bool = True,
) -> dict[str, Any]:
    """Fetch a public URL and ingest."""
    hit = url_fetcher.fetch_url(url)
    if not hit:
        raise ValueError(f"Could not extract enough text from {url}")
    ingested, errors = _ingest_hits([hit], auto_analyze=auto_analyze)
    if not ingested:
        raise ValueError(errors[0]["error"] if errors else "ingest failed")
    return {"ok": True, "url": url, **ingested[0]}


def _analyze_document(
    *,
    doc_id: str,
    text: str,
    title: str,
    country: str,
    year: int,
    structure_only: bool,
    source_environment: str = "",
    agency: str = "",
) -> dict[str, Any]:
    case_id = f"INGEST-{doc_id}"
    orch = _get_orch(init_llm=structure_only)
    ingest_metadata = {
        "title": title,
        "source_environment": source_environment,
        "agency": agency,
    }

    if structure_only:
        result = orch.run_from_text(
            case_id=case_id,
            raw_text=text,
            title=title,
            country=country,
            year=year,
            engine_only=True,
            structure_only=True,
            verbose=False,
            ingest_metadata=ingest_metadata,
        )
    else:
        result = orch.run_from_text(
            case_id=case_id,
            raw_text=text,
            title=title,
            country=country,
            year=year,
            engine_only=True,
            verbose=False,
            ingest_metadata=ingest_metadata,
        )

    dumped = result.model_dump()
    iso3 = case_db.country_to_iso3(country)
    case_db.save_signal_point(
        country=country,
        iso3=iso3,
        case_id=case_id,
        doc_id=doc_id,
        msi=result.wms.msi,
        cep=result.wms.cep,
        echo_pressure=result.egd.echo_room_pressure,
        dominant_pno=result.pno.dominant_pno,
        cat=result.cat.catastrophe_hypothesis,
    )
    case_db.mark_document_analyzed(doc_id, case_id=case_id)

    return {
        "case_id": case_id,
        "cep": result.wms.cep,
        "msi": result.wms.msi,
        "cat": result.cat.catastrophe_hypothesis,
        "dominant_pno": result.pno.dominant_pno,
        "result": dumped,
    }


def process_pending(*, limit: int = 10, structure_only: bool = True) -> list[dict]:
    """Analyze documents with status=pending."""
    docs = case_db.list_raw_documents(status="pending", limit=limit)
    out = []
    for d in docs:
        full = case_db.get_raw_document(d["doc_id"])
        if not full:
            continue
        try:
            r = _analyze_document(
                doc_id=d["doc_id"],
                text=full["text"],
                title=full["title"],
                country=full["country"],
                year=_guess_year(full["text"]),
                structure_only=structure_only,
                source_environment=full.get("source_environment", ""),
                agency=full.get("agency", ""),
            )
            out.append({"doc_id": d["doc_id"], "status": "analyzed", **r})
        except Exception as exc:
            case_db.update_document_status(d["doc_id"], "error", str(exc))
            out.append({"doc_id": d["doc_id"], "status": "error", "error": str(exc)})
    return out


def run_rss_fetch(
    *,
    feeds: list[dict[str, str]] | None = None,
    max_items_per_feed: int = 3,
    auto_analyze: bool = True,
) -> dict[str, Any]:
    """Pull configured RSS/Atom feeds."""
    feed_list = feeds or _load_feeds()
    if not feed_list:
        return {"ok": False, "error": "No feeds configured in data/ingest_feeds.json", "ingested": 0}

    ingested: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for feed in feed_list:
        feed_url = feed.get("url", "")
        if not feed_url:
            continue
        try:
            hits = rss_fetcher.fetch_feed(feed_url, max_items=max_items_per_feed)
            for hit in hits:
                if feed.get("country") and not hit.get("country"):
                    hit["country"] = feed["country"]
            batch, batch_errs = _ingest_hits(hits, auto_analyze=auto_analyze, seen_urls=seen_urls)
            ingested.extend(batch)
            errors.extend(batch_errs)
        except Exception as exc:
            errors.append({"feed": feed_url, "error": str(exc)})

    return {
        "ok": True,
        "feeds_run": len(feed_list),
        "ingested": len(ingested),
        "documents": ingested,
        "errors": errors,
    }


def run_web_search(
    *,
    queries: list[str] | None = None,
    num_results: int = 3,
    provider: str | None = None,
    auto_analyze: bool = True,
) -> dict[str, Any]:
    """Web search via best available provider (OpenRouter > Gemini > Exa)."""
    chosen = provider or _pick_web_search_provider()
    if not chosen:
        return {
            "ok": False,
            "error": "No web search provider — set OPENROUTER_API_KEY, GOOGLE_API_KEY, or EXA_API_KEY",
            "ingested": 0,
        }

    queries = queries or _load_queries()
    ingested: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for query in queries:
        try:
            hits = _search_hits(chosen, query, num_results=num_results)
            batch, batch_errs = _ingest_hits(hits, auto_analyze=auto_analyze, seen_urls=seen_urls)
            ingested.extend(batch)
            errors.extend(batch_errs)
        except Exception as exc:
            errors.append({"query": query, "error": str(exc)})

    return {
        "ok": True,
        "provider": chosen,
        "queries_run": len(queries),
        "ingested": len(ingested),
        "documents": ingested,
        "errors": errors,
    }


def run_exa_fetch(
    *,
    queries: list[str] | None = None,
    num_results: int = 3,
    auto_analyze: bool = True,
) -> dict[str, Any]:
    """Run Exa searches and ingest results."""
    if not exa_fetcher.is_configured():
        return {
            "ok": False,
            "error": "EXA_API_KEY not configured",
            "ingested": 0,
        }

    queries = queries or _load_queries()
    ingested: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for query in queries:
        try:
            hits = exa_fetcher.search(query, num_results=num_results)
            batch, batch_errs = _ingest_hits(hits, auto_analyze=auto_analyze, seen_urls=seen_urls)
            ingested.extend(batch)
            errors.extend(batch_errs)
        except Exception as exc:
            errors.append({"query": query, "error": str(exc)})

    return {
        "ok": True,
        "provider": "exa",
        "queries_run": len(queries),
        "ingested": len(ingested),
        "documents": ingested,
        "errors": errors,
    }


def _fetch_us_source_hits(
    src: dict[str, Any],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    fetcher_name = src.get("fetcher", "")
    module = _US_FETCHERS.get(fetcher_name)
    if not module:
        return []
    if src.get("requires_key") and not module.is_configured():
        return []

    params = dict(src.get("params") or {})
    wms_env = src.get("wms_environment", "")
    country = src.get("country", "USA")
    kwargs: dict[str, Any] = {"limit": limit}
    if wms_env:
        kwargs["source_environment"] = wms_env
    kwargs.update({k: v for k, v in params.items() if k not in kwargs})

    hits = module.fetch_recent(**kwargs)
    for hit in hits:
        if country and not hit.get("country"):
            hit["country"] = country
        if wms_env and not hit.get("source_environment"):
            hit["source_environment"] = wms_env
    return hits


def run_us_gov_fetch(
    *,
    sources: list[str] | None = None,
    limit_per_source: int = 3,
    auto_analyze: bool = True,
) -> dict[str, Any]:
    """Pull configured US government API/scrape sources."""
    all_sources = _load_us_sources()
    if not all_sources:
        return {"ok": False, "error": "No sources in data/ingest_sources_us.json", "ingested": 0}

    if sources:
        allowed = set(sources)
        all_sources = [s for s in all_sources if s.get("id") in allowed]

    ingested: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    sources_run = 0

    for src in all_sources:
        src_id = src.get("id", "")
        fetcher_name = src.get("fetcher", "")
        module = _US_FETCHERS.get(fetcher_name)
        if not module:
            errors.append({"source": src_id, "error": f"Unknown fetcher: {fetcher_name}"})
            continue
        if src.get("requires_key") and not module.is_configured():
            continue

        sources_run += 1
        try:
            hits = _fetch_us_source_hits(src, limit=limit_per_source)
            batch, batch_errs = _ingest_hits(hits, auto_analyze=auto_analyze, seen_urls=seen_urls)
            ingested.extend(batch)
            errors.extend(batch_errs)
        except Exception as exc:
            errors.append({"source": src_id, "error": str(exc)})

    return {
        "ok": True,
        "sources_run": sources_run,
        "ingested": len(ingested),
        "documents": ingested,
        "errors": errors,
        "fetchers": us_gov_fetcher_status(),
    }


def run_fetch_all(
    *,
    num_results: int = 2,
    max_items_per_feed: int = 2,
    auto_analyze: bool = True,
) -> dict[str, Any]:
    """Run RSS + web search + US gov sources (best provider)."""
    parts: dict[str, Any] = {}
    total_ingested = 0
    all_errors: list[dict[str, Any]] = []

    rss_result = run_rss_fetch(max_items_per_feed=max_items_per_feed, auto_analyze=auto_analyze)
    parts["rss"] = rss_result
    if rss_result.get("ok"):
        total_ingested += rss_result.get("ingested", 0)
        all_errors.extend(rss_result.get("errors", []))

    us_gov_result = run_us_gov_fetch(limit_per_source=max_items_per_feed, auto_analyze=auto_analyze)
    parts["us_gov"] = us_gov_result
    if us_gov_result.get("ok"):
        total_ingested += us_gov_result.get("ingested", 0)
        all_errors.extend(us_gov_result.get("errors", []))

    web_result = run_web_search(num_results=num_results, auto_analyze=auto_analyze)
    parts["web_search"] = web_result
    if web_result.get("ok"):
        total_ingested += web_result.get("ingested", 0)
        all_errors.extend(web_result.get("errors", []))

    return {
        "ok": True,
        "ingested": total_ingested,
        "parts": parts,
        "errors": all_errors,
        "fetchers": fetcher_status(),
    }


def ingest_status() -> dict[str, Any]:
    """Monitoring summary for GUI / ops."""
    from ..engine.cep_alerts import count_active_alerts

    stats = case_db.ingest_stats()
    recent = case_db.list_raw_documents(limit=15)
    streams = case_db.signal_stream_summary()
    fetchers = fetcher_status()
    us_gov = us_gov_fetcher_status()
    return {
        "engine": "v1-ingest",
        "exa_configured": fetchers["exa"],
        "exa_search_type": EXA_SEARCH_TYPE,
        "exa_agent_mode": EXA_AGENT_MODE,
        "exa_preferred": EXA_PREFERRED,
        "fetchers": fetchers,
        "us_gov_configured": us_gov,
        "web_search_provider": _pick_web_search_provider() or None,
        "active_alerts_count": count_active_alerts(),
        **stats,
        "recent_documents": recent,
        "signal_streams": streams,
    }
