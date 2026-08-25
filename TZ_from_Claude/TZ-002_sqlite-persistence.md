---
id: TZ-002
title: SQLite persistence — case history + /api/cases + Globe from DB
status: done
priority: 2
estimated: 2-3h
author: Claude
created: 2026-06-12
depends_on: []
---

## Context

Analysis results are not persisted after the request completes.
GUI `sessionStorage` holds only the last run of the current browser session.
`country_stats_seed.json` is static and does not update after Analyze.

Goal: persist each `CaseAnalysis` in SQLite. No ORM — stdlib `sqlite3` only.

---

## Step 1 — Create `mas/db.py`

**New file:** `errorlogy-mas/mas/db.py`

(See implemented module in repo — schema: `cases` table with `result_json`.)

---

## Step 2 — Initialize DB on FastAPI startup

**File:** `api/main.py`

Call `init_db()` in lifespan or `@app.on_event("startup")`.

---

## Step 3 — Save result in orchestrator

**File:** `mas/orchestrator.py`

After successful `run_engine_from_case` / `run_from_text`, call `case_db.save_case(...)`.

---

## Step 4 — Refresh stats router

**File:** `api/routers/stats.py`

Use `case_db.country_stats()` with fallback to `country_stats_seed.json` when DB empty.

Add `GET /api/stats/cases` listing recent cases.

---

## Step 5 — Case by ID endpoint

**File:** `api/routers/analysis.py`

Add `GET /api/cases/{case_id}` returning stored `CaseAnalysis` JSON or 404.

---

## Verification

```bash
cd errorlogy-mas
python -c "from mas.db import init_db; init_db(); print('DB created')"
pytest tests/ -x -q
```

---

## Out of scope

- No SQLAlchemy / Alembic / other ORM
- Do not change `CaseAnalysis` schema — store as `model_dump()` JSON
- Do not delete `country_stats_seed.json` — fallback required
- No DELETE/UPDATE endpoints for cases
