# Data Sources - overview

> Hub document: where does Errorlogy get external signals and how they relate to ingest.

## Layers

| Layer | Purpose | Document |
|------|-----------|-----|
| Ingest | Collection + auto-analyze → `raw_documents`, `signal_timeseries` | [[Ingest - info stream layer]] |
| Environments | WMS `source_environments` (12 types) | [[Data Sources - environments]] |
| Corpus | Seed cases, batch JSON | Roadmap / corpus docs |
| MCP | Cursor Exa bridge, batch ingest | Ingest layer |

## Sources by region

###UK/EU (RSS)

Config: `errorlogy-mas/data/ingest_feeds.json` - BBC, gov.uk, parliamentary feeds.

### US government (API / scrape)

Config: `errorlogy-mas/data/ingest_sources_us.json`

Ported from [democracy-monitor](https://github.com/agile-explorations/democracy-monitor) (MIT) - **collection layer only**, without DM assessment pipeline.

| Fetcher | Module | Key | WMS environment |
|---------|--------|------|-----------------|
| Federal Register | `federal_register.py` | no | `legal_judicial` |
| CourtListener | `courtlistener.py` | `COURTLISTENER_API_TOKEN` (optional) | `legal_judicial` |
| GovInfo GAO/CRPT | `govinfo.py` | `GOVINFO_API_KEY` | `audit_oversight` |
| DOJ OIG | `oig.py` | no | `audit_oversight` |
| LegiScan US | `legiscan.py` | `LEGISCAN_API_KEY` | `parliamentary_inquiry` |

### Web search (queries)

Config: `errorlogy-mas/data/ingest_queries.json` - OpenRouter / Gemini / Exa.

## API / CLI

- `POST /api/ingest/fetch-us-gov` - US gov sources only
- `POST /api/ingest/fetch-all` - RSS + US gov + web search
- `python scripts/fetch_gov_media.py --us-gov-only`

## Attribution

Fetchers `federal_register`, `courtlistener`, `govinfo`, `oig`, `legiscan` - adapted from democracy-monitor (MIT).