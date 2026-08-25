---
id: TZ-003
title: Seed corpus — 5 governance cases, engine_only pipeline, SQLite
status: done
priority: 3
estimated: 30min
author: Claude
created: 2026-06-12
depends_on: [TZ-002]
---

## Context

After TZ-002 SQLite exists. Seed it with first cases so:
- Globe shows real data instead of static seed JSON
- Baseline exists for future engine calibration
- MasPage shows recent_runs from real pipeline runs

All 5 cases — from OLD SKETCH (full sources in `ERRORLOGY/errorlogy_old_version/`).
Run with `engine_only=True` — no LLM calls.

---

## Script

**File:** `errorlogy-mas/scripts/seed_corpus.py`

Loads Challenger, Chernobyl, Iraq WMD, Post Office Horizon, Deepwater Horizon — runs engine-only pipeline, saves to DB.

---

## Run

```bash
cd errorlogy-mas
python scripts/seed_corpus.py
```

Expected: 5 cases saved with top mode, μ, CAT, CEP printed per case.

---

## Verification

```bash
python -c "from mas.db import list_cases, country_stats; import json; print(json.dumps(list_cases(), indent=2))"
# GET /api/stats/countries → real country counts
```

---

## Out of scope

- Do not run full MAS pipeline on seeds (no LLM keys in this task)
- Do not edit case texts to "improve" engine output
- Do not add more than 5 cases in this script
- Keep `country_stats_seed.json` as fallback
