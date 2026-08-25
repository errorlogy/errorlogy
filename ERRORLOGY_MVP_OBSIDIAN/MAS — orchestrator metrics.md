# MAS - orchestrator metrics

> **Status:** ACTIVE v0.2.2+ · Backend + GUI  
> Connections: [[errorlogy-mas - active MVP (Claude)]] · [[errorlogy-gui - desktop app v0.2]] · [[Taxonomy vs Engine - formalization gap]]

## Why

Seeing **how a 14-agent pipeline works**: engine vs LLM, step times, providers, tokens is not only the result of a case analysis.

Role separation (v1-math):

| Type | Agents |
|----------|--------|
| **engine** | wms, classifier, alpha, pno, acc, egd, t4d, cat, fpd |
| **LLM** | scout, lbi, red_team, card_compiler, neutrality |

---

##Backend

| Component | Path |
|-----------|------|
| Metrics collection | `errorlogy-mas/mas/metrics.py` |
| Hook LLM | `mas/agents/base.py` → `record_llm()` |
| Hook engine | `mas/orchestrator.py` → `track_engine()` |
| API | `GET /api/metrics` |
| In the response analyze | `metadata.pipeline_metrics` |

### Example `GET /api/metrics`

```json
{
  "engine_version": "v1-math",
  "runs_in_session": 3,
  "total_llm_calls": 15,
  "total_engine_calls": 27,
  "last_run": {
    "case_id": "US-NASA-1986-CHALLENGER-01",
    "steps": [
      {"agent_id": "scout", "kind": "llm", "duration_ms": 4200, "provider": "openai", "input_tokens": 1200},
      {"agent_id": "wms", "kind": "engine", "duration_ms": 12}
    ],
    "totals": { "engine_duration_ms": 180, "llm_duration_ms": 45000 }
  },
  "agent_registry": [...]
}
```

Metrics **in-memory** (uvicorn session) - restarting the API resets the history. v2: SQLite/OTel.

---

##GUI

| Screen | Route |
|-------|---------|
| **MAS Orchestrator** | `/#/mas` |

Shows:
- KPI: runs, LLM calls, engine steps, tokens
- Timeline of last run (red = engine, amber = LLM)
- Recent runs table
- Agent registry (14 agents)

Update every 5 s + after Analyze (metrics in `sessionStorage` → `last_analysis.metadata.pipeline_metrics`).

---

## Roadmap of metrics

| v | Feature |
|---|------|
| v0.2.2 | In-process metrics + GUI page ✅ |
| v2 | Persist runs in SQLite |
| v2 | OpenTelemetry export (compatible with OpenClaw diagnostics-otel) |
| v2 | Cost USD per provider |
| v2 | SSE live progress in Analyze (not fake timer) |

---

## OpenClaw (future)

OpenClaw is an **ingestion orchestration**, not an analytics engine.

- Cron → fetch sources → `POST /api/ingest` (v2)  
- OpenClaw OTel + Errorlogy `/api/metrics` → single Grafana (optional)

---

## Tags

#mas #orchestrator #metrics #gui #monitoring

→ [[00 - Home]] · [[errorlogy-gui - desktop app v0.2]]