# Specs from Claude — index

Technical specifications written by Claude for Cursor implementation.

Convention:
- One file = one atomic work block
- `status: pending` → not started
- `status: in_progress` → Cursor picked up
- `status: done` → accepted, verified
- `status: rejected` → rejected, see comment

| File | Description | Priority | Status |
|------|-------------|----------|--------|
| [TZ-001_engine-cleanup.md](TZ-001_engine-cleanup.md) | PNO dead code, T4D keywords, EGD fallback, CAT-002 rule | 1 | done |
| [TZ-002_sqlite-persistence.md](TZ-002_sqlite-persistence.md) | SQLite for case history + /api/cases + Globe from DB | 2 | done |
| [TZ-003_seed-corpus.md](TZ-003_seed-corpus.md) | 5 seed cases: Challenger, Chernobyl, Iraq WMD, Horizon, Deepwater | 3 | done |
