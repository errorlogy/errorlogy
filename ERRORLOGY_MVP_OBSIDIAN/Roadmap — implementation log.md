# Roadmap — implementation log

> Живой лог по плану Errorlogy Improvement Roadmap (Cursor, 2026-06-01)

## Фаза A — TZ-001 ✅

- `pno.py`: `_family_weights` удалён, `_pno_num()` для lookup
- `t4d.py`: убраны Challenger keywords, расширен latency_risk
- `egd.py`: удалён synthetic fallback CB-019/CB-028
- `cat.py`: CAT-002 по cluster_id, sympy forms CAT-003/010/015
- pytest: 16/16

## Фаза B — SQLite ✅

- `mas/db.py`: cases + pipeline_runs + `country_stats_globe()`
- `api/main.py`: init_db on startup
- orchestrator: `_persist_result()` после каждого run
- metrics: persist runs в DB, merge в `/api/metrics`
- stats: DB-first, seed fallback
- `GET /api/cases/{case_id}`, `GET /api/stats/cases`

## Фаза C — Seed corpus ✅

- `scripts/seed_corpus.py` — 5 кейсов engine_only
- DB: USA×3, UK×1, RUS×1

## Фаза D ✅

- `mas/dual_run.py` + `POST /api/analyze?dual_run=true`
- `structure_only=true` — LightweightScout (Scout + engine)
- pipeline_runs persist → MasPage survives restart

## Фаза E ✅

- `mas/engine/embeddings.py` — multilingual MiniLM, TF-IDF fallback
- `ERRORLOGY_USE_EMBEDDINGS=0|1`

## Фаза E+ (2026-06-01) ✅

- `scripts/calibrate_fuzzy.py` — Scout reference targets + scipy L-BFGS-B
- `data/calibration_targets.json` — top5 + weak_signals per seed
- `data/fuzzy_weights.json` — loadable weights in `fuzzy.py`
- `alpha.py` — edge weight × confidence from taxonomy
- `embeddings.precompute_modes()` at taxonomy load
- GUI: LightweightScout, dual-run, pipeline_metrics в Analyze/Result
- Dual-run smoke Challenger: jaccard=1.0, CAT-003

## Фаза F — Ingest / info streams ✅ (2026-06-12)

- `mas/ingest/service.py` — raw docs → analyze → signal_timeseries
- Fetchers: **url**, **rss**, **openrouter**, **gemini**, exa (optional)
- `data/ingest_queries.json`, `data/ingest_feeds.json` (BBC, NAO, NASA, GAO)
- API: `/ingest/url`, `/batch`, `/fetch-all`, `/fetch-rss`, `/fetch-web`, `/fetch-exa`
- Web search priority: OpenRouter → Gemini → Exa (без новых ключей)
- GUI v0.2.4: Fetch all, RSS, Web, URL, MCP paste
- pytest: 26/26

## Фаза G — Roadmap TZ (2026-06-13) 📋

- Новый документ: **[[Roadmap — MAS math development TZ]]**
- Три горизонта: H1 engineering (corpus 20, WMS typing, cron, SSE), H2 Weak Signal Layer (fusion, CEP series), H3 Homo-MAS (FJ, PNO-007, GT)
- Таблица math-модулей + 10 эпиков с DoD; arxiv/github референсы
- Backlog ниже — детализирован в TZ

## Фаза H1 (2026-06-13) — WMS binding + ingest wiring ✅ (partial)

- `mas/engine/wms_vocabulary.py` — legacy Scout/heuristic → WMS-001..020; `normalize_signal_type`, catalog for Scout
- `mas/agents/scout.py` — prompt uses taxonomy WMS IDs + `source_environment` enum
- `mas/orchestrator.py` — heuristic outputs WMS IDs; `ingest_metadata` merge with Scout
- `mas/engine/egd.py`, `wms.py`, `fuzzy.py`, `t4d.py` — WMS-aware weights / normalization
- `mas/ingest/service.py` — `source_environment` + `agency` from hits → analyze pipeline
- `tests/test_wms_vocabulary.py` — vocabulary + environment diversity MSI
- **Остаётся H1:** optional OTLP

## Фаза H1 (2026-06-13) — corpus 20 + ingest cron + PNO ✅

- `scripts/seed_corpus.py` — **20** seed cases (USA×9, UK×5, EU×2, Germany, Japan, International, USSR)
- `data/calibration_targets.json` — top5 engine targets for all 20; weak_signals retained on original 5
- `scripts/run_ingest_cron.py` — us-gov+rss or `--all`, interval loop, `--dry-run`, logs → `logs/ingest_YYYYMMDD.log`
- `scripts/schedule_ingest.ps1` — Task Scheduler wrapper
- `mas/engine/pno.py` — `display_pno_id` / `taxonomy_pno_id` (PNO-001 ↔ PNO-1)
- pytest: **47/47** green

## Фаза H1 (2026-06-13) — SSE + dual-run Red Team ✅

- `POST /api/analyze/stream` — SSE step events (`agent_id`, `status`, `duration_ms`) + final `done` payload
- `mas/metrics.py` — optional `set_step_listener` callback; engine steps emit `running` then `ok`
- `mas/orchestrator.py` — `on_step` on all run paths; backward-compat sync `POST /api/analyze`
- `mas/dual_run.py` — `apply_dual_run_flags()` injects `[dual-run review]` hints into `red_team_notes`
- GUI Analyze: live step progress via stream; Result: dual-run Red Team badge
- `tests/test_dual_run.py` — divergence flag + no-flag match cases
- pytest: **49/49** green

## Phase H — democracy-monitor concern scoring (optional plugin, NOT core)

- Ingest layer ports **US gov fetchers only** from [democracy-monitor](https://github.com/agile-explorations/democracy-monitor); no DM AI assessment in engine.
- Optional future plugin: `mas/plugins/dm_concern.py` — concern scores as **supplementary ingest metadata**, never replacing WMS/MSI/CEP.
- GUI may show plugin badge; core pipeline remains Scout → engine deterministic path.
- Do not merge DM assessment pipeline into `mas/engine/` without explicit migration TZ.

## Фаза H2 (2026-06-13) — CEP alerts + Bayesian fusion ✅ (partial)

- `mas/engine/cep_alerts.py` — CEP threshold alerts, severity bands, 7d trends per iso3
- `mas/engine/bayesian_fusion.py` — log-odds multisource fusion; wired into `wms.compute_msi` when ≥2 signals
- API: `GET /api/signals/alerts`, `GET /api/signals/trends`
- `ingest_status()` — `active_alerts_count`
- GUI: IngestPage CEP alerts panel; Globe trend badges (Δ7d, cep_max)
- pytest: **59/59** (10 new: `test_cep_alerts`, `test_bayesian_fusion`)
- **Остаётся H2:** Hawkes bursts, EU/UK ingest, corpus 100, METHODS plugins, Scout verifier

## Фаза I — GLM, Z.ai, zvec KB, Exa E2E (2026-06-24) ✅

- `mas/providers/router.py` — GLM-5.2 для `card_compiler` + `t4d` (OpenRouter `z-ai/glm-5.2`, Z.ai `glm-5.2`)
- `ZaiProvider` + `ZAI_API_KEY` — прямой API Z.ai (`mas/providers/openai_compat.py`)
- `mas/kb/` — zvec hybrid FTS+vector; `retrieval.py`, demo `examples/zvec_kb_demo.py`
- Engine T4D читает `case.metadata.kb_context` (`mas/engine/t4d.py`)
- Exa: `source_discovery.py`, `enrich_sources` в orchestrator + `POST /api/analyze?enrich_sources=true`
- API: `POST /api/ingest/discover-sources`, `/enrich-bundle`; CLI `examples/run_exa_flow.py`, `scripts/exa_smoke.py`
- `EXA_API_KEY` configured (см. `.env`, не в vault)
- **Docker не требуется** для desktop MVP (venv + FastAPI + Electron GUI)
- **loop-library** skill + секция в корневом `AGENTS.md`
- Smoke: Challenger = offline engine; Horizon = Exa integration demo

→ детали: [[Сессия — GLM Exa zvec KB 2026-06-24]]

## Следующий шаг (backlog)

- Подключить `attach_kb_context()` в orchestrator перед T4D / Card Compiler
- GUI reinstall 0.2.4 с Info Stream
- optional OTLP metrics export

→ [[Roadmap — MAS math development TZ]] · [[Ingest — info stream layer]] · [[Анализ Claude — состояние engine v1]] · [[MAS — метрики оркестратора]]
