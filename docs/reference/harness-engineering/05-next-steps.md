# Next steps (defer vs pilot)

Aligned with stages [`docs/oss-integration-funnel.md`](../../oss-integration-funnel.md).

---

## Now (already present — strengthen with documentation)

| | | |
|----------|--------|--------|
| CI: pytest + engine-only + GUI build | Adopt (gate) | 0 — |
| harness-spec per agent | Process | low |
| Seed cases: Challenger + calibration seeds version control | Adopt | low |

---

## Pilot (0.5–2 weeks, scope)

### P1 — Neutrality eval pilot ✅ (Phase B, 2026-06-15)

**Why first:** language guards — pure LLM-eval layer; does not touch μ engine.

| | |
|-----|--------|
| Tool | `pytest` + `tests/evals/test_neutrality_live.py` |
| Seeds | `tests/evals/seeds/neutrality_{violations,clean}.yaml` |
| Keys | `scripts/load_keys_from_vault.ps1` → local `.env` (gitignored) |
| Gate | `EVAL_LIVE=1`; CI `.github/workflows/eval-live.yml` (`workflow_dispatch`) |
| Success | Violation seeds raise flags; clean seeds pass; default CI keyless |

```powershell
cd errorlogy-mas
.\scripts\load_keys_from_vault.ps1
$env:EVAL_LIVE = "1"
pytest tests/evals/test_neutrality_live.py -v
```

OAuth (`api/auth`) batch eval — API keys env.

### P1b — Card Compiler eval ( )

### P2 — pytest-agent-eval Scout extraction

| | |
|-----|--------|
| Scope | 3 seed cases → `GovernanceCase` schema assertions |
| Gate | Deterministic fields only in CI; LLM fields optional live |
| Risk | Flaky extraction — use threshold 0.8, 3 runs |

### P3 — Trace middleware (OpenTelemetry)

illustrative OSS funnel (`opentelemetry-python`). Pilot: FastAPI span per agent step, export console, default off.

---

## Spike (explore, merge)

| | | |
|----------|------|-------|
| AgentProbe | Trace + cost per 14-step run | : overhead vs value |
| checkagent record/replay | Cassette full pipeline | dual-run |
| Langfuse self-hosted | Dashboard latency | Infra decision |

`research/oss-candidates.yaml` `target_area: mas` `infra`.

---

## Defer

| | defer | |
|------|---------------|-----------|
| Auto harness evolution (AHE / Meta-Harness) | stable observability baseline | P1+P3 |
| Harbor / Terminal-Bench adapters | Wrong domain benchmark | generic agent CI template |
| Full live E2E PR | Cost + keys in CI | Nightly workflow only |
| lm-evaluation-harness | Base model eval, not MAS | Never for pipeline |
| Merge trn-sim evals into MAS CI | RESEARCH boundary | Explicit bridge task |

---

## (Q2–Q3 2026)

```text
1. P1 Neutrality eval pilot     ← DONE (Phase B)
2. harness-spec.yaml Scout, Neutrality, Red Team ← DONE (Phase A)
3. P2 Scout schema evals (pytest-agent-eval)
4. P3 OpenTelemetry spike (infra)
5. Nightly live workflow (optional full challenger)
```

---

## Adopt eval tool

OSS funnel Pilot → Adopt:

- CI green tool **opt-in**
- `engine_only`
- Neutrality/language rules weakened
- `docs/reference/harness-engineering/`
- Entry in `oss-candidates.yaml` → `decision: adopt`

---

##

- eval harness `errorlogy-mas/tests/evals/` ( P1 spike sign-off)
- orchestrator
- Commit secrets promptfoo/prompt configs
