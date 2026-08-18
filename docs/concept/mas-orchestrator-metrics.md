# MAS — метрики оркестратора

> **Статус:** ACTIVE v0.2.2 · Backend + GUI

## Зачем

14-агентный пайплайн: engine vs LLM, timing, tokens, providers.

| Тип | Агенты |
|-----|--------|
| engine | wms, classifier, alpha, pno, acc, egd, t4d, cat, fpd |
| LLM | scout, lbi, red_team, card_compiler, neutrality |

## Backend

- `errorlogy-mas/mas/metrics.py`
- `GET /api/metrics`
- `metadata.pipeline_metrics` в analyze response
- In-memory (сессия uvicorn); v2 → SQLite/OTel

## GUI

- Маршрут: `/#/mas`
- KPI, step timeline, recent runs, agent registry
- Auto-refresh 5s

## Roadmap

v0.2.2 ✅ in-process + GUI | v2 persist | v2 OTel | v2 cost USD | v2 SSE live progress
