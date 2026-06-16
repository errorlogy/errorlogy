# Harness gap audit — 2026-06-15

Brief audit of eval harness coverage vs production MAS pipeline. Phase A closes keyless CI gaps; Phase B is live LLM eval pilot.

---

## Findings (before Phase A)

| Gap | Severity | Status after Phase A |
|-----|----------|----------------------|
| No golden engine snapshot on Challenger fixture | High | Fixed — `test_challenger_engine_snapshot.py` + baseline JSON |
| No API-level `POST /api/analyze` smoke test | Medium | Fixed — `test_api_analyze.py` |
| No per-agent harness specs in repo | Medium | Fixed — `tests/evals/specs/{scout,neutrality,red_team}.yaml` |
| Per-agent LLM evals (Scout, Neutrality, Red Team) | High | Deferred — Phase B (P1/P2) |
| Recorded outputs / cassettes for full pipeline | Medium | Deferred |
| L4 live E2E in CI | Low (cost) | Deferred — nightly only |
| Agent-step latency metrics for eval | Low | Deferred — OpenTelemetry spike (P3) |
| Eval tool funnel entries | Low | Partial — `promptfoo`, `pytest-agent-eval` in discover |

---

## Phase A (this change)

- Golden snapshot: MSI, CEP, dominant PNO, top-5 mode IDs and μ vs committed baseline
- API smoke: `engine_only=true`, `CaseAnalysis` validation, no keys
- Harness specs: Scout (step 1), Red Team (12), Neutrality (14) with real module paths
- OSS funnel: eval tools registered at **discover** stage

---

## Phase B (this change — Neutrality live eval pilot)

1. **Seed packs** — `errorlogy-mas/tests/evals/seeds/`:
   - `neutrality_violations.yaml` (15 cases)
   - `neutrality_clean.yaml` (5 cases)
   - `scout_extraction.yaml` (3-case P2 stub)
2. **Live eval runner** — `tests/evals/test_neutrality_live.py` (`pytest -m llm_eval`, gate `EVAL_LIVE=1`)
3. **Vault → .env script** — `scripts/load_keys_from_vault.ps1` (local keys only, gitignored)
4. **CI** — `.github/workflows/eval-live.yml` (`workflow_dispatch` only; secrets documented, not committed)
5. **Spec wired** — `tests/evals/specs/neutrality.yaml` references seed paths + runner

| Gap | Severity | Status after Phase B |
|-----|----------|----------------------|
| Per-agent LLM evals (Neutrality) | High | **Pilot** — live eval + seeds |
| Seed packs in repo | Medium | **Done** |
| P2 Scout extraction evals | High | Stub seeds only |
| L4 live E2E in CI | Low (cost) | **Opt-in** workflow_dispatch |
| Card Compiler live eval | Medium | Deferred — Neutrality-only pilot |

---

## Phase B (remaining after pilot)

1. **P2 — Scout extraction schema evals** (wire `scout_extraction.yaml` to pytest)
2. **Card Compiler + Neutrality joint eval**
3. **Recorded outputs / cassettes** for full pipeline
4. **P3 — OpenTelemetry** per-agent spans (opt-in middleware)
5. **Nightly live workflow** — full `run_challenger.py` with keys
6. **Eval runner** — generic spec→pytest driver (not just Neutrality)

See [05-next-steps.md](05-next-steps.md) for queue and adopt criteria.

---

## Re-audit scores (post Phase A+B — 2026-06-16)

| Layer | Before | After | Notes |
|-------|--------|-------|-------|
| L1 Engine + CI | ~55% | **~68%** | Golden snapshot, API smoke, 74 keyless pytest |
| L2 LLM agents | ~42% | **~54%** | Neutrality live pilot (20 seeds); Scout/Card deferred |
| L3 Process + tooling | ~38% | **~50%** | Handbook, vault script, eval-live.yml |
| **Overall harness maturity** | ~40–45% | **~57%** | |

**Test runs (local, 2026-06-16):**

- `pytest tests/ -q -m "not llm_eval"` → **74 passed**, 20 deselected
- `EVAL_LIVE=1 pytest tests/evals/test_neutrality_live.py -m llm_eval` → **20 passed**, 10 deselected

### Remaining gaps (priority)

| Priority | Gap |
|----------|-----|
| **P0** | Scout extraction eval runner (seeds stub only) |
| **P0** | Generic spec→pytest driver (Neutrality-only today) |
| **P1** | Card Compiler eval; pipeline cassettes; Red Team live eval |
| **P2** | OpenTelemetry spans; nightly full challenger; promptfoo adopt |

Obsidian copy: `ERRORLOGY_MVP_OBSIDIAN/Отчёт — harness gap и планы 2026-06-16.md`
