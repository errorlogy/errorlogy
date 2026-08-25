# Harness engineering — Errorlogy reference

> **Status:** reference handbook (no code implementation).  
> **Related docs:** [`docs/oss-integration-funnel.md`](../../oss-integration-funnel.md), [`errorlogy-mas/AGENTS.md`](../../../errorlogy-mas/AGENTS.md)

---

## What this is

**Harness engineering** (in the AI-agent context) — designing and evolving the **wrapper** around LLMs: orchestration, prompts, tools, state, deterministic checks, tracing, and eval infrastructure. This is **not** a replacement for `mas/engine/`.

**Agent harness** — system that turns a model into an agent: accepts input, calls tools, maintains state, returns structured output. In Errorlogy this is primarily `mas/orchestrator.py` + 14 agents + engine layer.

**Eval harness** — infrastructure for end-to-end task runs: case fixtures, parallel execution, step recording, graders (deterministic and LLM-as-judge), metric aggregation, CI quality gates. Industry examples: Anthropic evals guidance, OpenAI evals, `promptfoo`, `pytest-agent-eval`, Braintrust, LangSmith.

Research 2025–2026 shows: with a fixed model, changing harness (prompts, middleware, environment bootstrap, feedback loops) often yields more gain than changing the model. For Errorlogy: **invest in a testable pipeline wrapper**, not "another LLM for μ".

---

## Why Errorlogy

| MVP problem | Harness engineering role |
|--------------|--------------------------|
| 14-agent pipeline, nonlinear regressions | Layered evals: pytest → `engine_only` smoke → optional live LLM evals |
| Split engine vs LLM (μ deterministic) | Deterministic graders on engine; LLM-judge only on narrative/neutrality |
| Neutrality / language rules | Harness component: guards + red-team + eval rubrics |
| OSS integrations | Discover→Adopt funnel; eval-tools scored on `test_safety` and `engine_llm_fit` |
| Desktop GUI + API | Contract tests on `schemas/analysis.py`; smoke without API keys |

**Boundaries:** `errorlogy-trn-sim/` — **RESEARCH**, separate harness; do not mix with MAS without `bridge/`. OLD SKETCH — reference only.

---

## Contents

| File | Purpose |
|------|------------|
| [01-principles.md](01-principles.md) | 10 research principles applicable to Errorlogy |
| [02-errorlogy-mapping.md](02-errorlogy-mapping.md) | Mapping to MAS, GUI, CI, OSS funnel |
| [03-checklist.md](03-checklist.md) | Checklist when adding agent or feature |
| [04-tools-landscape.md](04-tools-landscape.md) | OSS/SaaS tools table with fit score |
| [05-next-steps.md](05-next-steps.md) | Pilot vs defer, funnel stages |
| [templates/harness-spec.yaml](templates/harness-spec.yaml) | Minimal eval spec template for one MAS agent |

---

## Quick links (current MVP)

```bash
cd errorlogy-mas && pytest tests/ -q
python errorlogy-mas/examples/run_challenger.py --engine-only
```

CI: [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml) — pytest + challenger engine-only + GUI build.
