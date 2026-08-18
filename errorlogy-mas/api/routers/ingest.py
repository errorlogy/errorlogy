"""Ingestion API — gov/media info streams."""



from __future__ import annotations



import pathlib

import sys



from fastapi import APIRouter, HTTPException

from pydantic import BaseModel, Field



sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))



from mas.ingest import (

    ingest_batch,

    ingest_document,

    ingest_status,

    ingest_url,

    process_pending,

    run_exa_fetch,

    run_fetch_all,

    run_rss_fetch,

    run_us_gov_fetch,

    run_web_search,

    build_discovery_query,

    discover_sources,

    enrich_source_bundle,

)

from mas import db as case_db



router = APIRouter(prefix="/api/ingest", tags=["ingest"])





class IngestRequest(BaseModel):

    source: str = "manual"

    source_type: str = "manual"

    url: str = ""

    title: str = ""

    country: str = ""

    text: str

    doc_id: str | None = None

    auto_analyze: bool = True

    structure_only: bool = True





class IngestUrlRequest(BaseModel):

    url: str

    auto_analyze: bool = True





class BatchDocument(BaseModel):

    source: str = "mcp"

    source_type: str = "mcp_bridge"

    url: str = ""

    title: str = ""

    country: str = ""

    text: str

    doc_id: str | None = None





class IngestBatchRequest(BaseModel):

    documents: list[BatchDocument]

    auto_analyze: bool = True

    structure_only: bool = True





class ExaFetchRequest(BaseModel):

    queries: list[str] | None = None

    num_results: int = Field(default=3, ge=1, le=10)

    auto_analyze: bool = True





class WebSearchRequest(BaseModel):

    queries: list[str] | None = None

    num_results: int = Field(default=3, ge=1, le=10)

    provider: str | None = None

    auto_analyze: bool = True





class RssFetchRequest(BaseModel):

    max_items_per_feed: int = Field(default=3, ge=1, le=10)

    auto_analyze: bool = True





class FetchAllRequest(BaseModel):

    num_results: int = Field(default=2, ge=1, le=5)

    max_items_per_feed: int = Field(default=2, ge=1, le=5)

    auto_analyze: bool = True





class UsGovFetchRequest(BaseModel):

    sources: list[str] | None = None

    limit_per_source: int = Field(default=3, ge=1, le=10)

    auto_analyze: bool = True




class DiscoverSourcesRequest(BaseModel):

    query: str | None = None

    title: str = ""

    country: str = ""

    year: int = 0

    raw_text: str = ""

    num_results: int = Field(default=3, ge=1, le=10)

    provider: str | None = None




class EnrichBundleRequest(BaseModel):

    raw_text: str

    title: str = ""

    country: str = ""

    year: int = 0

    query: str | None = None

    num_results: int = Field(default=3, ge=1, le=10)

    provider: str | None = None





@router.post("")

async def post_ingest(req: IngestRequest):

    try:

        return ingest_document(

            source=req.source,

            source_type=req.source_type,

            url=req.url,

            title=req.title,

            country=req.country,

            text=req.text,

            doc_id=req.doc_id,

            auto_analyze=req.auto_analyze,

            structure_only=req.structure_only,

        )

    except ValueError as exc:

        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:

        raise HTTPException(status_code=500, detail=str(exc)) from exc





@router.post("/url")

async def post_ingest_url(req: IngestUrlRequest):

    try:

        return ingest_url(url=req.url, auto_analyze=req.auto_analyze)

    except ValueError as exc:

        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:

        raise HTTPException(status_code=500, detail=str(exc)) from exc





@router.post("/batch")

async def post_ingest_batch(req: IngestBatchRequest):

    docs = [d.model_dump() for d in req.documents]

    return ingest_batch(

        docs,

        auto_analyze=req.auto_analyze,

        structure_only=req.structure_only,

    )





@router.get("/status")

async def get_status():

    return ingest_status()





@router.get("/documents")

async def list_documents(status: str | None = None, limit: int = 50):

    return {"documents": case_db.list_raw_documents(status=status, limit=limit)}





@router.get("/documents/{doc_id}")

async def get_document(doc_id: str):

    doc = case_db.get_raw_document(doc_id)

    if not doc:

        raise HTTPException(status_code=404, detail="Document not found")

    return doc





@router.get("/signals")

async def get_signals(country: str | None = None, iso3: str | None = None, limit: int = 100):

    return {

        "signals": case_db.list_signal_timeseries(country=country, iso3=iso3, limit=limit),

    }





@router.post("/process-pending")

async def post_process_pending(limit: int = 10, structure_only: bool = True):

    return {"processed": process_pending(limit=limit, structure_only=structure_only)}





@router.post("/fetch-exa")

async def post_fetch_exa(req: ExaFetchRequest):

    result = run_exa_fetch(

        queries=req.queries,

        num_results=req.num_results,

        auto_analyze=req.auto_analyze,

    )

    if not result.get("ok"):

        raise HTTPException(status_code=503, detail=result.get("error", "Exa fetch failed"))

    return result





@router.post("/fetch-web")

async def post_fetch_web(req: WebSearchRequest):

    result = run_web_search(

        queries=req.queries,

        num_results=req.num_results,

        provider=req.provider,

        auto_analyze=req.auto_analyze,

    )

    if not result.get("ok"):

        raise HTTPException(status_code=503, detail=result.get("error", "Web search failed"))

    return result





@router.post("/fetch-rss")

async def post_fetch_rss(req: RssFetchRequest):

    result = run_rss_fetch(

        max_items_per_feed=req.max_items_per_feed,

        auto_analyze=req.auto_analyze,

    )

    if not result.get("ok"):

        raise HTTPException(status_code=503, detail=result.get("error", "RSS fetch failed"))

    return result





@router.post("/fetch-us-gov")

async def post_fetch_us_gov(req: UsGovFetchRequest):

    result = run_us_gov_fetch(

        sources=req.sources,

        limit_per_source=req.limit_per_source,

        auto_analyze=req.auto_analyze,

    )

    if not result.get("ok"):

        raise HTTPException(status_code=503, detail=result.get("error", "US gov fetch failed"))

    return result





@router.post("/fetch-all")

async def post_fetch_all(req: FetchAllRequest):

    return run_fetch_all(

        num_results=req.num_results,

        max_items_per_feed=req.max_items_per_feed,

        auto_analyze=req.auto_analyze,

    )





@router.post("/discover-sources")

async def post_discover_sources(req: DiscoverSourcesRequest):

    query = req.query or build_discovery_query(

        title=req.title,

        country=req.country,

        year=req.year,

        raw_text=req.raw_text,

    )

    hits, provider = discover_sources(

        query,

        num_results=req.num_results,

        provider=req.provider,

    )

    if not provider:

        raise HTTPException(

            status_code=503,

            detail="No web search provider — set EXA_API_KEY, OPENROUTER_API_KEY, or GOOGLE_API_KEY",

        )

    return {

        "ok": True,

        "query": query,

        "provider": provider,

        "hits": len(hits),

        "sources": hits,

    }





@router.post("/enrich-bundle")

async def post_enrich_bundle(req: EnrichBundleRequest):

    enriched, hits, provider = enrich_source_bundle(

        req.raw_text,

        title=req.title,

        country=req.country,

        year=req.year,

        num_results=req.num_results,

        provider=req.provider,

        query=req.query,

    )

    if not provider:

        raise HTTPException(

            status_code=503,

            detail="No web search provider — set EXA_API_KEY, OPENROUTER_API_KEY, or GOOGLE_API_KEY",

        )

    return {

        "ok": True,

        "provider": provider,

        "hits": len(hits),

        "sources": hits,

        "enriched_text": enriched,

    }

