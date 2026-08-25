# Report - harness gap and plans (2026-06-16)

> **Thread:** `research/oss-integration-funnel`  
> **Context:** re-audit after Phase A + Phase B harness engineering  
> **Related docs:** [[errorlogy-mas - active MVP (Claude)]], `docs/reference/harness-engineering/06-gap-audit-2026.md`

---

## Executive summary

After Phase A/B/C (Scout pilot), eval-harness maturity increased from **~40–45%** to **~63%**. L1 (~68%): golden snapshot, smoke API, **88 keyless pytest**, CI with `-m "not llm_eval"`. L2: two live pilots - Neutrality **20/20**, Scout extraction **12/12** with `EVAL_LIVE=1`. The main remaining gaps are: generic spec→pytest driver, Card Compiler eval, cassettes, Red Team live.

**Test run (2026-06-16, updated):**

| Team | Result |
|---------|-----------|
| `py -3.12 -m pytest tests/ -q -m "not llm_eval"` | **88 passed**, 32 deselected |
| `EVAL_LIVE=1 pytest tests/evals/test_neutrality_live.py -m llm_eval` | **20 passed**, 10 deselected |
| `EVAL_LIVE=1 pytest tests/evals/test_scout_extraction_live.py -m llm_eval` | **12 passed**, 14 deselected (~79s) |

---

## Harness maturity ratings

| Layer | Was (2026-06-15) | Became (2026-06-16) | Δ | Comment |
|------|-------------------|---------------------|---|-------------|
| **L1 - Engine + CI** | ~55% | **~68%** | +13 | Golden baseline, API smoke, 74 keyless tests, CI pytest + engine-only |
| **L2 - LLM agents** | ~42% | **~62%** | +20 | Neutrality + Scout live pilots; Red Team - spec only |
| **L3 - Process + tooling** | ~38% | **~50%** | +12 | Handbook, vault→.env, eval-live.yml; promptfoo/nightly - no |
| **General Maturity** | ~40–45% | **~63%** | +18–23 | L1 is strong; L2 - two agents with live eval |

### Pyramid eval (fact)

```text
L4 Live LLM eval [██] Neutrality ✅ Scout ✅; Card/Red Team - no
L3 Golden/cassettes [~] engine baseline ✅; full pipeline cassettes - no
L2 Integration [██] engine_only smoke + API contract
L1 Unit pytest [███] engine modules + ingest + guards
```

---

## Phase A - completed ✅

| Artifact | Path |
|----------|------|
| Golden engine snapshot | `errorlogy-mas/tests/test_challenger_engine_snapshot.py` + `fixtures/challenger_engine_baseline.json` |
| API smoke | `errorlogy-mas/tests/test_api_analyze.py` |
| Harness-spec (3 agents) | `errorlogy-mas/tests/evals/specs/{scout,neutrality,red_team}.yaml` |

**Commit:** `dbd2ba2`

---

## Phase B - completed ✅

| Artifact | Path |
|----------|------|
| Seed packs | `tests/evals/seeds/neutrality_violations.yaml` (15), `neutrality_clean.yaml` (5), `scout_extraction.yaml` (stub) |
| Live Neutrality eval | `tests/evals/test_neutrality_live.py` (`llm_eval`, `EVAL_LIVE=1`) |
| Vault → .env | `scripts/load_keys_from_vault.ps1` |
| CI live eval (manual) | `.github/workflows/eval-live.yml` (`workflow_dispatch`) |

**Commit:** `05a6c69`

---

## Remaining gap

### P0 (critical for next sprint)

| Gap | Status |
|----------|--------|
| Scout extraction live eval | ✅ `0c4c91a` — 12 seeds, 12/12 live |
| Generic spec→pytest driver (Neutrality + Scout hand-wired) | Missing |

### P1 (important)

| Gap | Status |
|----------|--------|
| Card Compiler + Neutrality joint eval | Deferred |
| Recorded outputs / cassettes full pipeline | Deferred |
| Red Team live eval harness | Spec only |
| CI: explicit `-m "not llm_eval"` in ci.yml | ✅ Done (`0c4c91a`) |

### P2 (improvements)

| Gap | Status |
|----------|--------|
| OpenTelemetry per-agent spans | P3 in roadmap |
| Nightly live workflow (`run_challenger.py` full) | Deferred |
| Eval tool funnel → Adopt (promptfoo, etc.) | Partial discover |

---

## Phase C roadmap (next harness)

1. ~~Scout extraction live eval~~ ✅ (`test_scout_extraction_live.py`, commit `0c4c91a`)
2. **P1 — Card Compiler eval** — joint with Neutrality
3. **P3 - OpenTelemetry** - FastAPI span per agent step
4. **Nightly live workflow** - full challenger with keys
5. **Generic eval runner** - spec YAML → pytest (not only Neutrality)

See `docs/reference/harness-engineering/05-next-steps.md`

---

## Other project plans (checklist)| Plan | Status | Notes |
|-----------|--------|---------|
| **errorlogy-gui v1** (Electron **0.2.5**) | ✅ ~90% MAS API | API autostart from shortcut, `py -3.12` + `api-startup.log` |
| **errorlogy-gui-v2** (forecast, **:5174**) | ✅ v0.1 browser | `/`, `/case`, `/stream`, `/data` - without Electron |
| **GUI integration Phase 1–2** | ✅ Done | Result from API, deep links, ingest/history, taxonomy |
| **GUI integration Phase 3** | ⏳Pending | OAuth UI, export, lazy Globe code-split |
| **OSS integration funnel** + `discover_github_oss.py` | ✅ Branch + docs | `research/oss-integration-funnel`, `docs/oss-integration-funnel.md` |
| **Harness engineering handbook** | ✅ Done | `docs/reference/harness-engineering/` (8 files) |
| **Minimal CI** | ✅ Done | `.github/workflows/ci.yml` - pytest + engine-only + GUI build |
| **Refactoring audit** | ✅ Recommendations | Point refactor: OpenAPI types GUI↔API, split ingest, lazy Globe; orchestrator do not touch |
| **GITHUB_TOKEN 401** (`discover_github_oss.py`) | ⚠️Blocked | The token in `.env` responds 401 - check Active + scope `public_repo`; dry-run without a token works with a limit |

---

## Next 3 actions

1. **Generic spec→pytest driver** - generalize Neutrality + Scout runners.
2. **Card Compiler live eval** — joint with Neutrality on public output.
3. **GUI v2 E2E smoke** - Challenger `engine_only` on `:5174`.

---

## Next steps (prioritization, 2026-06-16)

| Horizon | Action | Why |
|----------|----------|--------|
| ~~Week~~ | ~~Scout live eval~~ | ✅ `0c4c91a` |
| ~~Week~~ | ~~`-m "not llm_eval"` in ci.yml~~ | ✅ `0c4c91a` |
| **Week** | GUI v2 smoke `engine_only` on `:5174` | Parallel harness; fixes product loop |
| **2-4 weeks** | Generic spec→pytest driver | After Scout (2nd agent), not before |
| **2-4 weeks** | Card Compiler + Neutrality joint eval | Closes the public output chain |
| **Stop** | OTel, nightly full challenger, promptfoo adopt | Observability/cost without growth eval coverage |
| **Stop** | Agent-Reach in MAS | `discover`, verdict maybe; cherry-pick CLIs on ingest-spike |
| **Stop** | GITHUB_TOKEN 401 | Dry-run works; unblock when you need OSS discover |

---

## Links

- Handbook: `docs/reference/harness-engineering/README.md`
- Gap audit (updated): `docs/reference/harness-engineering/06-gap-audit-2026.md`
- OSS funnel: `docs/oss-integration-funnel.md`
- GUI v1: [[errorlogy-gui - desktop app v0.2]]
- MAS: [[errorlogy-mas - active MVP (Claude)]]

---

*Generated by Cursor Agent, 2026-06-16. Secrets and API keys are not included.*