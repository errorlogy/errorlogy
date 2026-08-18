# Data Sources — обзор

> Hub-документ: откуда Errorlogy берёт внешние сигналы и как они связаны с ingest.

## Слои

| Слой | Назначение | Документ |
|------|------------|----------|
| Ingest | Сбор + auto-analyze → `raw_documents`, `signal_timeseries` | [[Ingest — info stream layer]] |
| Environments | WMS `source_environments` (12 типов) | [[Data Sources — environments]] |
| Corpus | Seed cases, batch JSON | Roadmap / corpus docs |
| MCP | Cursor Exa bridge, batch ingest | Ingest layer |

## Источники по регионам

### UK / EU (RSS)

Конфиг: `errorlogy-mas/data/ingest_feeds.json` — BBC, gov.uk, parliamentary feeds.

### US government (API / scrape)

Конфиг: `errorlogy-mas/data/ingest_sources_us.json`

Портировано из [democracy-monitor](https://github.com/agile-explorations/democracy-monitor) (MIT) — **только слой сбора**, без DM assessment pipeline.

| Fetcher | Модуль | Ключ | WMS environment |
|---------|--------|------|-----------------|
| Federal Register | `federal_register.py` | нет | `legal_judicial` |
| CourtListener | `courtlistener.py` | `COURTLISTENER_API_TOKEN` (optional) | `legal_judicial` |
| GovInfo GAO / CRPT | `govinfo.py` | `GOVINFO_API_KEY` | `audit_oversight` |
| DOJ OIG | `oig.py` | нет | `audit_oversight` |
| LegiScan US | `legiscan.py` | `LEGISCAN_API_KEY` | `parliamentary_inquiry` |

### Web search (queries)

Конфиг: `errorlogy-mas/data/ingest_queries.json` — OpenRouter / Gemini / Exa.

## API / CLI

- `POST /api/ingest/fetch-us-gov` — US gov sources only
- `POST /api/ingest/fetch-all` — RSS + US gov + web search
- `python scripts/fetch_gov_media.py --us-gov-only`

## Attribution

Fetchers `federal_register`, `courtlistener`, `govinfo`, `oig`, `legiscan` — adapted from democracy-monitor (MIT).
