# MAS — метрики оркестратора

> **Статус:** ACTIVE v0.2.2+ · Backend + GUI  
> Связи: [[errorlogy-mas — активный MVP (Claude)]] · [[errorlogy-gui — desktop app v0.2]] · [[Таксономия vs Engine — formalization gap]]

## Зачем

Видеть **как работает 14-агентный пайплайн**: engine vs LLM, время шагов, провайдеры, токены — не только результат анализа кейса.

Разделение ролей (v1-math):

| Тип | Агенты |
|-----|--------|
| **engine** | wms, classifier, alpha, pno, acc, egd, t4d, cat, fpd |
| **LLM** | scout, lbi, red_team, card_compiler, neutrality |

---

## Backend

| Компонент | Путь |
|-----------|------|
| Сбор метрик | `errorlogy-mas/mas/metrics.py` |
| Hook LLM | `mas/agents/base.py` → `record_llm()` |
| Hook engine | `mas/orchestrator.py` → `track_engine()` |
| API | `GET /api/metrics` |
| В ответе analyze | `metadata.pipeline_metrics` |

### Пример `GET /api/metrics`

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

Метрики **in-memory** (сессия uvicorn) — перезапуск API сбрасывает историю. v2: SQLite/OTel.

---

## GUI

| Экран | Маршрут |
|-------|---------|
| **MAS Orchestrator** | `/#/mas` |

Показывает:
- KPI: runs, LLM calls, engine steps, tokens
- Timeline последнего прогона (красный = engine, янтарный = LLM)
- Таблица recent runs
- Agent registry (14 agents)

Обновление каждые 5 с + после Analyze (метрики в `sessionStorage` → `last_analysis.metadata.pipeline_metrics`).

---

## Roadmap метрик

| v | Фича |
|---|------|
| v0.2.2 | In-process metrics + GUI page ✅ |
| v2 | Persist runs в SQLite |
| v2 | OpenTelemetry export (совместимо с OpenClaw diagnostics-otel) |
| v2 | Cost USD per provider |
| v2 | SSE live progress в Analyze (не fake timer) |

---

## OpenClaw (будущее)

OpenClaw — **оркестрация ingestion**, не analytics engine.

- Cron → fetch sources → `POST /api/ingest` (v2)  
- OpenClaw OTel + Errorlogy `/api/metrics` → единый Grafana (опционально)

---

## Теги

#mas #orchestrator #metrics #gui #monitoring

→ [[00 — Главная]] · [[errorlogy-gui — desktop app v0.2]]
