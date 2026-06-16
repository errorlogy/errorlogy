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

## Phase B (remaining)

1. **P1 — Neutrality + Card Compiler eval pilot** (`promptfoo` or `pytest-agent-eval`, `EVAL_LIVE=1`)
2. **P2 — Scout extraction schema evals** (3 seed cases, threshold 0.8)
3. **Seed packs** — `tests/evals/seeds/*.yaml` referenced in specs (not yet created)
4. **P3 — OpenTelemetry** per-agent spans (opt-in middleware)
5. **Nightly live workflow** — full `run_challenger.py` with keys
6. **Eval runner** — wire specs to CI (opt-in job), not just documentation YAML

See [05-next-steps.md](05-next-steps.md) for queue and adopt criteria.
