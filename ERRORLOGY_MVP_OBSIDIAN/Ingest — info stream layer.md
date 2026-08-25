# Ingest - info stream layer

> Information flow monitoring layer (gov management + media) → MAS pipeline → signal time series

## Why

Batch-only seed corpus does not reflect live signals. The Ingest layer accepts documents from the outside, runs LightweightScout + engine and writes points in `signal_timeseries` for Globe and dashboard.

## Architecture

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

##Backend

| Component | Path |
|-----------|------|
| Service | `mas/ingest/service.py` |
| URL fetcher | `mas/ingest/fetchers/url.py` - no key |
| RSS fetcher | `mas/ingest/fetchers/rss.py` - without a key; follow URL if summary is short |
| OpenRouter search | `mas/ingest/fetchers/openrouter_search.py` - `OPENROUTER_API_KEY` |
| Gemini grounding | `mas/ingest/fetchers/gemini_search.py` - `GOOGLE_API_KEY` |
| Exa fetcher | `mas/ingest/fetchers/exa.py` - `EXA_API_KEY` (configured in dev `.env`) |
| Source discovery | `mas/ingest/source_discovery.py` - `discover_sources`, `enrich_source_bundle` |
| US gov fetchers | `federal_register`, `courtlistener`, `govinfo`, `oig`, `legiscan` - see [[Data Sources - overview]] |
| US sources config | `data/ingest_sources_us.json` |
| Tables | `raw_documents`, `signal_timeseries` in `mas/db.py` |
| Requests/feeds | `data/ingest_queries.json`, `data/ingest_feeds.json` |
| API | `api/routers/ingest.py` |
| CLI | `scripts/fetch_gov_media.py` |

###API

- `POST /api/ingest` - manual document + auto-analyze
- `POST /api/ingest/url` — download public URL
- `POST /api/ingest/batch` - package from MCP / external sources
- `POST /api/ingest/fetch-all` - RSS + US gov + web search (best provider)
- `POST /api/ingest/fetch-us-gov` - Federal Register, CourtListener, OIG (+ keyed sources)
- `POST /api/ingest/fetch-rss` - RSS only
- `POST /api/ingest/fetch-web` - OpenRouter → Gemini → Exa
- `POST /api/ingest/fetch-exa` - Exa only
- `POST /api/ingest/discover-sources` - search for hits without ingest
- `POST /api/ingest/enrich-bundle` — merged source bundle for analyze
- `POST /api/analyze?enrich_sources=true` - discovery to Scout in the full pipeline
- `GET /api/ingest/status` - dashboard + `fetchers` ON/OFF
- `GET /api/ingest/documents`, `/documents/{id}`
- `GET /api/ingest/signals`
- `POST /api/ingest/process-pending`

### Keys (web search priority)

1. `OPENROUTER_API_KEY` - already exists → `perplexity/sonar` / `:online`
2. `GOOGLE_API_KEY` - already exists → Gemini + Google Search grounding
3. `EXA_API_KEY` - optional
4. RSS + URL + Federal Register + CourtListener + OIG - **no keys**
5. `GOVINFO_API_KEY`, `COURTLISTENER_API_TOKEN`, `LEGISCAN_API_KEY` - optional

## GUI v0.2.3+

- Sidebar → **Info Stream** (`/#/ingest`)
- Status: docs, signals, Exa configured
- Buttons: Fetch all, Fetch US gov, Fetch RSS, Web search, Exa
- Auto-refresh every 8 s

## Start monitoring

**Fetch all (RSS + US gov + web):**
```bash
python scripts/fetch_gov_media.py
# or POST /api/ingest/fetch-all
```

**US gov only:**
```bash
python scripts/fetch_gov_media.py --us-gov-only
# or POST /api/ingest/fetch-us-gov
```

**RSS only:**
```bash
python scripts/fetch_gov_media.py --rss-only
```

**By URL:**
```bash
curl -X POST http://127.0.0.1:8000/api/ingest/url\
  -H "Content-Type: application/json" \
  -d '{"url":"https://..."}'
```

**MCP batch (Cursor Exa → API):**
```bash
curl -X POST http://127.0.0.1:8000/api/ingest/batch\
  -H "Content-Type: application/json" \
  -d '{"documents":[{"source":"exa_mcp","title":"...","url":"...","text":"..."}]}'
```

**E2E Exa flow (Horizon, not Challenger):**
```bash
python errorlogy-mas/examples/run_exa_flow.py
python errorlogy-mas/scripts/exa_smoke.py
```

**Periodic monitoring (v2):** cron/OpenClaw → `fetch_gov_media.py` every N hours.

## Smoke (2026-06-12 / 2026-06-24)

- pytest `test_ingest.py`, `test_source_discovery.py`: green (mock Exa)
- Manual UK Horizon → `INGEST-doc-*`, CEP ~0.30, 1 signal stream GBR
- `run_exa_flow.py` — Exa enrich → engine-only MAS; Challenger remains in `run_challenger.py`

→ [[Session – GLM Exa zvec KB 2026-06-24]]

##Backlog

- [ ] Scheduler (cron / OpenClaw hook)
- [ ] Slack MCP alerts for new signals
- [ ] GUI package reinstall 0.2.4

→ [[Roadmap - implementation log]] · [[Taxonomy vs Engine - formalization gap]]