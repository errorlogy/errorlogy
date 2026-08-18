"""
POST /api/analyze  — run full MAS pipeline on a governance case
POST /api/analyze/stream — SSE live step progress + final result
GET  /api/taxonomy — return ontology summary
GET  /api/taxonomy/mode/{id} — single mode
"""
import asyncio
import json
from dataclasses import asdict
from queue import Empty, Queue
from threading import Thread

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from mas.engine import ENGINE_VERSION
from mas.orchestrator import Orchestrator
from mas import taxonomy
from mas.metrics import AgentStepMetric
from api.auth.jwt import current_user

router = APIRouter(prefix="/api", tags=["analysis"])

# Shared orchestrator (initialized once)
_orchestrator: Orchestrator | None = None

def get_orchestrator() -> Orchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator


class AnalyzeRequest(BaseModel):
    case_id: str
    raw_text: str
    title: str = ""
    country: str = ""
    year: int = 0


def _run_analyze(
    orch: Orchestrator,
    req: AnalyzeRequest,
    *,
    engine_only: bool,
    structure_only: bool,
    dual_run: bool,
    enrich_sources: bool = False,
    discover_num_results: int = 3,
    on_step=None,
):
    if dual_run:
        return orch.run_dual(
            case_id=req.case_id,
            raw_text=req.raw_text,
            title=req.title,
            country=req.country,
            year=req.year,
            verbose=False,
            on_step=on_step,
        )
    return orch.run_from_text(
        case_id=req.case_id,
        raw_text=req.raw_text,
        title=req.title,
        country=req.country,
        year=req.year,
        verbose=False,
        engine_only=engine_only,
        structure_only=structure_only,
        enrich_sources=enrich_sources,
        discover_num_results=discover_num_results,
        on_step=on_step,
    )


@router.post("/analyze")
async def analyze(
    req: AnalyzeRequest,
    engine_only: bool = False,
    structure_only: bool = False,
    dual_run: bool = False,
    enrich_sources: bool = False,
    discover_num_results: int = 3,
    user=Depends(current_user),
):
    try:
        orch = get_orchestrator()
        result = _run_analyze(
            orch, req,
            engine_only=engine_only,
            structure_only=structure_only,
            dual_run=dual_run,
            enrich_sources=enrich_sources,
            discover_num_results=discover_num_results,
        )
        return result.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/analyze/stream")
async def analyze_stream(
    req: AnalyzeRequest,
    engine_only: bool = False,
    structure_only: bool = False,
    dual_run: bool = False,
    enrich_sources: bool = False,
    discover_num_results: int = 3,
    user=Depends(current_user),
):
    orch = get_orchestrator()
    queue: Queue = Queue()

    def on_step(step: AgentStepMetric) -> None:
        queue.put({"event": "step", "data": asdict(step)})

    def run_pipeline() -> None:
        try:
            result = _run_analyze(
                orch, req,
                engine_only=engine_only,
                structure_only=structure_only,
                dual_run=dual_run,
                enrich_sources=enrich_sources,
                discover_num_results=discover_num_results,
                on_step=on_step,
            )
            queue.put({"event": "done", "data": result.model_dump()})
        except Exception as exc:
            queue.put({"event": "error", "data": {"detail": str(exc)}})
        finally:
            queue.put(None)

    async def event_generator():
        loop = asyncio.get_running_loop()
        Thread(target=run_pipeline, daemon=True).start()
        while True:
            try:
                item = await loop.run_in_executor(None, queue.get, True, 0.5)
            except Empty:
                yield ": keepalive\n\n"
                continue
            if item is None:
                break
            payload = json.dumps(item["data"], ensure_ascii=False)
            yield f"event: {item['event']}\ndata: {payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/cases/{case_id}")
async def get_case(case_id: str, user=Depends(current_user)):
    from mas.db import get_case
    result = get_case(case_id)
    if not result:
        raise HTTPException(status_code=404, detail="Case not found")
    return result


@router.get("/taxonomy")
async def get_taxonomy():
    data = taxonomy.load()
    return {
        "version": data.get("version"),
        "counts": data.get("counts"),
        "layers": data.get("layers"),
        "meta_dimensions": data.get("meta_dimensions"),
    }


@router.get("/taxonomy/mode/{mode_id}")
async def get_mode(mode_id: str):
    mode = taxonomy.get_mode(mode_id)
    if not mode:
        raise HTTPException(404, f"Mode {mode_id} not found")
    return mode


@router.get("/taxonomy/modes")
async def get_modes():
    data = taxonomy.load()
    return data.get("atomic_modes", [])


@router.get("/taxonomy/edges")
async def get_edges():
    return taxonomy.get_alpha_edges()


@router.get("/health")
async def health():
    from mas.config import Config, EXA_AGENT_MODE, EXA_PREFERRED, EXA_SEARCH_TYPE
    from mas.ingest.fetchers import exa as exa_fetcher
    cfg = Config()
    return {
        "status": "ok",
        "engine": ENGINE_VERSION,
        "providers": cfg.available_providers(),
        "taxonomy_modes": taxonomy.summary().get("atomic_total"),
        "alpha_edges": len(taxonomy.get_alpha_edges()),
        "exa_configured": exa_fetcher.is_configured(),
        "exa_preferred": EXA_PREFERRED,
        "exa_search_type": EXA_SEARCH_TYPE,
        "exa_agent_mode": EXA_AGENT_MODE,
    }
