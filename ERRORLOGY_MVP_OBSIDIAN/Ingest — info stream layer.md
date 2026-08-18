# Ingest — info stream layer

> Слой мониторинга инфопотоков (gov management + media) → MAS pipeline → signal time series

## Зачем

Batch-only seed corpus не отражает живые сигналы. Ingest layer принимает документы извне, прогоняет LightweightScout + engine и пишет точки в `signal_timeseries` для Globe и дашборда.

## Архитектура

```
RSS / US gov APIs / URL / OpenRouter / Gemini / Exa / manual / MCP batch
        ↓
  raw_documents (SQLite)
        ↓
  LightweightScout + engine (structure_only)
        ↓
  cases + signal_timeseries
        ↓
  Globe (last_signal_at, signal_points) + GUI Info Stream
```

## Backend

| Компонент | Путь |
|-----------|------|
| Сервис | `mas/ingest/service.py` |
| URL fetcher | `mas/ingest/fetchers/url.py` — без ключа |
| RSS fetcher | `mas/ingest/fetchers/rss.py` — без ключа; follow URL если summary короткий |
| OpenRouter search | `mas/ingest/fetchers/openrouter_search.py` — `OPENROUTER_API_KEY` |
| Gemini grounding | `mas/ingest/fetchers/gemini_search.py` — `GOOGLE_API_KEY` |
| Exa fetcher | `mas/ingest/fetchers/exa.py` — `EXA_API_KEY` (configured в dev `.env`) |
| Source discovery | `mas/ingest/source_discovery.py` — `discover_sources`, `enrich_source_bundle` |
| US gov fetchers | `federal_register`, `courtlistener`, `govinfo`, `oig`, `legiscan` — см. [[Data Sources — обзор]] |
| US sources config | `data/ingest_sources_us.json` |
| Таблицы | `raw_documents`, `signal_timeseries` в `mas/db.py` |
| Запросы / фиды | `data/ingest_queries.json`, `data/ingest_feeds.json` |
| API | `api/routers/ingest.py` |
| CLI | `scripts/fetch_gov_media.py` |

### API

- `POST /api/ingest` — ручной документ + auto-analyze
- `POST /api/ingest/url` — скачать публичный URL
- `POST /api/ingest/batch` — пакет из MCP / внешних источников
- `POST /api/ingest/fetch-all` — RSS + US gov + web search (лучший провайдер)
- `POST /api/ingest/fetch-us-gov` — Federal Register, CourtListener, OIG (+ keyed sources)
- `POST /api/ingest/fetch-rss` — только RSS
- `POST /api/ingest/fetch-web` — OpenRouter → Gemini → Exa
- `POST /api/ingest/fetch-exa` — только Exa
- `POST /api/ingest/discover-sources` — поиск hits без ingest
- `POST /api/ingest/enrich-bundle` — merged source bundle для analyze
- `POST /api/analyze?enrich_sources=true` — discovery до Scout в полном пайплайне
- `GET /api/ingest/status` — дашборд + `fetchers` ON/OFF
- `GET /api/ingest/documents`, `/documents/{id}`
- `GET /api/ingest/signals`
- `POST /api/ingest/process-pending`

### Ключи (приоритет web search)

1. `OPENROUTER_API_KEY` — уже есть → `perplexity/sonar` / `:online`
2. `GOOGLE_API_KEY` — уже есть → Gemini + Google Search grounding
3. `EXA_API_KEY` — опционально
4. RSS + URL + Federal Register + CourtListener + OIG — **без ключей**
5. `GOVINFO_API_KEY`, `COURTLISTENER_API_TOKEN`, `LEGISCAN_API_KEY` — опционально

## GUI v0.2.3+

- Sidebar → **Info Stream** (`/#/ingest`)
- Статус: docs, signals, Exa configured
- Кнопки: Fetch all, Fetch US gov, Fetch RSS, Web search, Exa
- Авто-refresh каждые 8 с

## Запуск мониторинга

**Fetch all (RSS + US gov + web):**
```bash
python scripts/fetch_gov_media.py
# или POST /api/ingest/fetch-all
```

**Только US gov:**
```bash
python scripts/fetch_gov_media.py --us-gov-only
# или POST /api/ingest/fetch-us-gov
```

**Только RSS:**
```bash
python scripts/fetch_gov_media.py --rss-only
```

**По URL:**
```bash
curl -X POST http://127.0.0.1:8000/api/ingest/url \
  -H "Content-Type: application/json" \
  -d '{"url":"https://..."}'
```

**MCP batch (Cursor Exa → API):**
```bash
curl -X POST http://127.0.0.1:8000/api/ingest/batch \
  -H "Content-Type: application/json" \
  -d '{"documents":[{"source":"exa_mcp","title":"...","url":"...","text":"..."}]}'
```

**E2E Exa flow (Horizon, не Challenger):**
```bash
python errorlogy-mas/examples/run_exa_flow.py
python errorlogy-mas/scripts/exa_smoke.py
```

**Периодический мониторинг (v2):** cron / OpenClaw → `fetch_gov_media.py` каждые N часов.

## Smoke (2026-06-12 / 2026-06-24)

- pytest `test_ingest.py`, `test_source_discovery.py`: green (mock Exa)
- Manual UK Horizon → `INGEST-doc-*`, CEP ~0.30, 1 signal stream GBR
- `run_exa_flow.py` — Exa enrich → engine-only MAS; Challenger остаётся в `run_challenger.py`

→ [[Сессия — GLM Exa zvec KB 2026-06-24]]

## Backlog

- [ ] Scheduler (cron / OpenClaw hook)
- [ ] Slack MCP alerts на новые signals
- [ ] GUI package reinstall 0.2.4

→ [[Roadmap — implementation log]] · [[Таксономия vs Engine — formalization gap]]
