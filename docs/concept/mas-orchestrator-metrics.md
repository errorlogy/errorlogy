# MAS — orchestrator metrics

> **Status:** ACTIVE v0.2.2 · Backend + GUI

## Why

14-agent pipeline: engine vs LLM, timing, tokens, providers.

| Type | Agents |
|------|--------|
| engine | wms, classifier, alpha, pno, acc, egd, t4d, cat, fpd |
| LLM | scout, lbi, red_team, card_compiler, neutrality |

## Backend

- `errorlogy-mas/mas/metrics.py`
- `GET /api/metrics`
- `metadata.pipeline_metrics` in analyze response
- In-memory (uvicorn session); v2 → SQLite/OTel

## GUI

- Route: `/#/mas`
- KPI, step timeline, recent runs, agent registry
- Auto-refresh 5s

## Roadmap

v0.2.2 ✅ in-process + GUI | v2 persist | v2 OTel | v2 cost USD | v2 SSE live progress
