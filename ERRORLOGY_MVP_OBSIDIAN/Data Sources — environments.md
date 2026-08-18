# Data Sources — environments

> Маппинг внешних источников на WMS `source_environments` (taxonomy v16)

## 12 WMS source environments

Из `errorlogy-mas/data/errorlogy_unified_taxonomy_v16.json` → `source_environments`:

| ID | Label (кратко) |
|----|----------------|
| `parliamentary_inquiry` | Parliamentary / legislative inquiry |
| `legal_judicial` | Courts, legal proceedings |
| `audit_oversight` | Audit, IG, oversight bodies |
| `regulatory_agency` | Regulatory agencies |
| `executive_branch` | Executive / White House |
| `media_investigation` | Investigative journalism |
| `academic_research` | Academic / think tank |
| `whistleblowers` | Whistleblower disclosures |
| `international_body` | UN, EU bodies, etc. |
| `corporate_disclosure` | Corporate filings |
| `civil_society` | NGOs, advocacy |
| `technical_literature` | Technical / engineering docs |

## US gov fetcher mapping

| Source ID | Fetcher | `wms_environment` | Notes |
|-----------|---------|---------------------|-------|
| `federal_register` | Federal Register API | `legal_judicial` | Rules, notices, presidential docs |
| `courtlistener_recap` | CourtListener RECAP | `legal_judicial` | Federal dockets; optional token |
| `govinfo_gao` | GovInfo `GAOREPORTS` | `audit_oversight` | GAO reports |
| `govinfo_crpt` | GovInfo `CRPT` | `audit_oversight` | Congressional reports |
| `oig_doj` | DOJ OIG scrape | `audit_oversight` | IG reports; may extend to `whistleblowers` |
| `legiscan_us` | LegiScan Congress | `parliamentary_inquiry` | Bills, legislative activity |

## UK RSS (ingest_feeds.json)

| Feed | Typical environment |
|------|---------------------|
| BBC Politics | `media_investigation` |
| gov.uk government feed | `executive_branch` / `regulatory_agency` |
| Parliamentary / NAO-style | `parliamentary_inquiry` / `audit_oversight` |

## Hit schema (ingest)

Каждый fetcher возвращает `normalize_hit` dict:

- `source`, `source_type`, `url`, `title`, `text`, `country`, `doc_id`
- опционально: `source_environment`, `agency`

Scout + engine используют текст; `source_environment` зарезервирован для будущего routing в WMS layers.

## См. также

- [[Data Sources — обзор]]
- [[Ingest — info stream layer]]
