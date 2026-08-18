"""In-process MAS pipeline metrics — agent steps, LLM tokens, engine timing."""

from __future__ import annotations

import time
import uuid
from collections import deque
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Callable, Iterator

from .engine import ENGINE_VERSION
from .providers.base import LLMResponse

ENGINE_AGENTS = frozenset({
    "wms", "classifier", "alpha", "pno", "acc", "egd", "t4d", "cat", "fpd",
})
LLM_AGENTS = frozenset({
    "scout", "lbi", "red_team", "card_compiler", "neutrality",
})

AGENT_LABELS: dict[str, str] = {
    "scout": "Scout",
    "wms": "WMS",
    "classifier": "Classifier",
    "alpha": "Alpha",
    "pno": "PNO",
    "acc": "ACC",
    "egd": "EGD",
    "t4d": "T4D",
    "cat": "CAT",
    "fpd": "FPD",
    "lbi": "LBI",
    "red_team": "Red Team",
    "card_compiler": "Card Compiler",
    "neutrality": "Neutrality",
}

_history: deque["PipelineRunMetric"] = deque(maxlen=30)
_current_run: ContextVar["PipelineRunMetric | None"] = ContextVar("pipeline_run", default=None)
_step_listener: ContextVar[Callable[[AgentStepMetric], None] | None] = ContextVar(
    "step_listener", default=None
)
_step_listener_stack: ContextVar[list[Callable[[AgentStepMetric], None]]] = ContextVar(
    "step_listener_stack", default=[]
)


@dataclass
class AgentStepMetric:
    agent_id: str
    kind: str  # engine | llm
    duration_ms: float
    status: str  # ok | error | skipped
    provider: str | None = None
    model: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    detail: str = ""


@dataclass
class PipelineRunMetric:
    run_id: str
    case_id: str
    engine_only: bool
    started_at: str
    finished_at: str | None = None
    status: str = "running"
    steps: list[AgentStepMetric] = field(default_factory=list)

    def totals(self) -> dict[str, Any]:
        llm_steps = [s for s in self.steps if s.kind == "llm"]
        eng_steps = [s for s in self.steps if s.kind == "engine"]
        return {
            "total_duration_ms": round(sum(s.duration_ms for s in self.steps), 1),
            "engine_steps": len(eng_steps),
            "llm_steps": len(llm_steps),
            "engine_duration_ms": round(sum(s.duration_ms for s in eng_steps), 1),
            "llm_duration_ms": round(sum(s.duration_ms for s in llm_steps), 1),
            "input_tokens": sum(s.input_tokens for s in llm_steps),
            "output_tokens": sum(s.output_tokens for s in llm_steps),
        }


def start_run(case_id: str, *, engine_only: bool = False) -> PipelineRunMetric:
    run = PipelineRunMetric(
        run_id=str(uuid.uuid4())[:8],
        case_id=case_id,
        engine_only=engine_only,
        started_at=_now_iso(),
    )
    _current_run.set(run)
    _history.append(run)
    return run


def finish_run(*, status: str = "ok") -> None:
    run = _current_run.get()
    if run:
        run.finished_at = _now_iso()
        run.status = status
        _persist_run(run)
    _current_run.set(None)


def _persist_run(run: PipelineRunMetric) -> None:
    try:
        from . import db as case_db
        case_db.save_pipeline_run(run_to_dict(run))
    except Exception:
        pass


def set_step_listener(callback: Callable[[AgentStepMetric], None] | None) -> None:
    if callback is None:
        stack = list(_step_listener_stack.get())
        if stack:
            stack.pop()
        _step_listener_stack.set(stack)
        _step_listener.set(stack[-1] if stack else None)
    else:
        stack = list(_step_listener_stack.get())
        stack.append(callback)
        _step_listener_stack.set(stack)
        _step_listener.set(callback)


def _emit_step(step: AgentStepMetric) -> None:
    cb = _step_listener.get()
    if cb:
        cb(step)


def record_llm(agent_id: str, resp: LLMResponse, duration_ms: float) -> None:
    run = _current_run.get()
    step = AgentStepMetric(
        agent_id=agent_id,
        kind="llm",
        duration_ms=round(duration_ms, 1),
        status="ok",
        provider=resp.provider,
        model=resp.model,
        input_tokens=resp.input_tokens,
        output_tokens=resp.output_tokens,
    )
    if run:
        run.steps.append(step)
    _emit_step(step)


def record_engine(agent_id: str, duration_ms: float, *, detail: str = "", status: str = "ok") -> None:
    run = _current_run.get()
    step = AgentStepMetric(
        agent_id=agent_id,
        kind="engine",
        duration_ms=round(duration_ms, 1),
        status=status,
        detail=detail,
    )
    if run:
        run.steps.append(step)
    _emit_step(step)


@contextmanager
def track_engine(agent_id: str, *, detail: str = "") -> Iterator[None]:
    _emit_step(AgentStepMetric(agent_id=agent_id, kind="engine", duration_ms=0, status="running"))
    t0 = time.perf_counter()
    err = False
    try:
        yield
    except Exception:
        err = True
        raise
    finally:
        ms = (time.perf_counter() - t0) * 1000
        record_engine(agent_id, ms, detail=detail, status="error" if err else "ok")


def last_run() -> PipelineRunMetric | None:
    return _history[-1] if _history else None


def run_to_dict(run: PipelineRunMetric) -> dict[str, Any]:
    return {
        "run_id": run.run_id,
        "case_id": run.case_id,
        "engine_only": run.engine_only,
        "engine_version": ENGINE_VERSION,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
        "status": run.status,
        "steps": [asdict(s) for s in run.steps],
        "totals": run.totals(),
    }


def summary() -> dict[str, Any]:
    runs = list(_history)
    db_runs: list[dict[str, Any]] = []
    try:
        from . import db as case_db
        db_runs = case_db.list_pipeline_runs(limit=30)
    except Exception:
        pass

    llm_calls = sum(1 for r in runs for s in r.steps if s.kind == "llm")
    engine_calls = sum(1 for r in runs for s in r.steps if s.kind == "engine")
    tokens_in = sum(s.input_tokens for r in runs for s in r.steps)
    tokens_out = sum(s.output_tokens for r in runs for s in r.steps)
    last = last_run()

    seen_ids = {r.run_id for r in runs}
    merged_recent: list[dict[str, Any]] = [
        {
            "run_id": r.run_id,
            "case_id": r.case_id,
            "status": r.status,
            "engine_only": r.engine_only,
            "started_at": r.started_at,
            "totals": r.totals(),
        }
        for r in reversed(runs[-10:])
    ]
    for dr in db_runs:
        if dr["run_id"] not in seen_ids and len(merged_recent) < 15:
            merged_recent.append({
                "run_id": dr["run_id"],
                "case_id": dr["case_id"],
                "status": dr["status"],
                "engine_only": dr["engine_only"],
                "started_at": dr["started_at"],
                "totals": dr["totals"],
            })
    merged_recent.sort(key=lambda x: x.get("started_at") or "", reverse=True)

    return {
        "engine_version": ENGINE_VERSION,
        "runs_in_session": len(runs),
        "runs_in_db": len(db_runs),
        "total_llm_calls": llm_calls,
        "total_engine_calls": engine_calls,
        "total_input_tokens": tokens_in,
        "total_output_tokens": tokens_out,
        "last_run": (
            run_to_dict(last) if last
            else (_enrich_db_run(db_runs[0]) if db_runs else None)
        ),
        "recent_runs": merged_recent[:15],
        "agent_registry": [
            {
                "id": aid,
                "label": AGENT_LABELS.get(aid, aid),
                "kind": "engine" if aid in ENGINE_AGENTS else "llm",
            }
            for aid in [
                "scout", "wms", "classifier", "alpha", "pno", "acc", "egd",
                "t4d", "cat", "fpd", "lbi", "red_team", "card_compiler", "neutrality",
            ]
        ],
    }


def _enrich_db_run(dr: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": dr.get("run_id"),
        "case_id": dr.get("case_id"),
        "engine_only": dr.get("engine_only", False),
        "engine_version": ENGINE_VERSION,
        "started_at": dr.get("started_at"),
        "finished_at": dr.get("finished_at"),
        "status": dr.get("status", "ok"),
        "steps": dr.get("steps", []),
        "totals": dr.get("totals", {}),
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
