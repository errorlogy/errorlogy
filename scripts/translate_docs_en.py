#!/usr/bin/env python3
"""Write English translations for remaining docs (no full-tree scan)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TRANSLATIONS = {
"docs/oss-integration-funnel.md": r'''# OSS integration evaluation funnel for Errorlogy

> **Status:** process + tracker template (no actual integrations yet).  
> **Related docs:** [`AGENTS.md`](../AGENTS.md), [`errorlogy-mas/AGENTS.md`](../errorlogy-mas/AGENTS.md), [`research/oss-candidates.yaml`](../research/oss-candidates.yaml).

Optional: Obsidian symlink → `ERRORLOGY_MVP_OBSIDIAN/OSS — integration funnel.md` → `../docs/oss-integration-funnel.md`.

---

## Why

The Errorlogy MVP has several zones with different integration rules. New open-source GitHub projects (orchestrators, observability, codegen, workflow engines, etc.) must be **filtered before code**, so that:

- the split **engine (μ, determinism) vs LLM (interpretation)** is preserved;
- patterns from **OLD SKETCH** are not pulled into ACTIVE without a migration task;
- **RESEARCH** (`errorlogy-trn-sim`) is not mixed with the 14-agent pipeline without an explicit bridge;
- analytical reproducibility and **CI** pass ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)).

---

## Repository boundaries

| Label | Path | OSS rule |
|-------|------|----------|
| **ACTIVE** | `errorlogy-mas/`, `errorlogy-gui/` | Only after Pilot; CI must be green |
| **RESEARCH** | `errorlogy-trn-sim/` | Experiments allowed; MAS only via `bridge/` + separate decision |
| **OLD SKETCH** | `ERRORLOGY/errorlogy_old_version/` | Reference and seed cases; **not** a copy-paste code source |

---

## Funnel stages

```text
Discover → Screen → Spike → Pilot → Adopt | Reject | Defer
```

| Stage | Goal | Artifacts | Exit |
|-------|------|-----------|------|
| **Discover** | Record candidate | Entry in `research/oss-candidates.yaml` | `stage: discover` |
| **Screen** | Quick rubric filter | Filled `score`, notes | Spike **or** Reject/Defer |
| **Spike** | 0.5–2 days: POC in branch / sandbox | Branch `spike/<name>`, notes in `notes_en` | Go/no-go for Pilot |
| **Pilot** | Limited scope in target zone | PR in `research/oss-integration-funnel` or feature branch | Metrics, diff blast radius |
| **Adopt** | Merge into ACTIVE | Docs, tests, CI | `decision: adopt` |
| **Reject** | Not suitable | Reason in tracker | `decision: reject` |
| **Defer** | Potentially later | Review condition | `decision: defer` |
| **Research-only** | trn-sim / bridge only | Do not touch `mas/agents/` | `decision: research_only` |

**Screen → Spike threshold:** weighted total score ≥ **3.0** out of 5.0 (see rubric) **and** no automatic veto (below).

**Pilot → Adopt threshold:** CI green (`pytest`, `run_challenger.py --engine-only`, `npm run build` for GUI); for engine changes — no LLM in numeric paths; Neutrality/language rules not weakened.

---

## Scoring rubric (1–5)

Each axis: **1** = bad for Errorlogy, **5** = excellent. Weights adjustable; default — equal.

| Axis | Weight | 1 (risk) | 5 (good) | Errorlogy context |
|-----|-----|----------|------------|-------------------|
| **coupling** | 1.0 | Hard framework lock-in, hard to remove | Thin adapter, optional dependency | MAS orchestrator, GUI `api.ts` |
| **duplication** | 1.0 | Duplicates `mas/engine/*`, taxonomy, orchestrator | Closes explicit gap (ingest, metrics UI) | Not a second fuzzy/PNO |
| **test_safety** | 1.2 | Breaks `engine_only` / μ determinism | Mocks well, covered by pytest | `pytest tests/`, challenger smoke |
| **blast_radius** | 1.2 | Touches all 14 agents + schemas | Local module (1 package) | `schemas/analysis.py` — high radius |
| **license** | 1.0 | AGPL/unclear license for desktop | MIT/Apache-2.0, Electron-compatible | GUI distribution |
| **maintenance** | 0.8 | Abandoned >12 mo, few contributors | Active releases, used in prod | |
| **engine_llm_fit** | 1.5 | Pushes LLM to compute μ/MSI/PNO | Strengthens engine **or** pure infra/UX | See `errorlogy-mas/AGENTS.md` |
| **old_sketch_risk** | 1.0 | Copy-paste from politic.bar v0.6 / AGIU | Independent of OLD SKETCH | Migration task if overlap |

**Formula:** `score_total = Σ(weight × value) / Σ(weight)` → number 1..5 in YAML.

### Automatic veto (Reject without Spike)

- Proposes replacing `mas/engine/` computations with LLM.
- Requires merging code from `errorlogy_old_version/` without migration task.
- License incompatible with GUI distribution (legal review if uncertain).
- Pulls foreign product "concern scoring / AI assessment" into core engine (Roadmap Phase H — ingest plugins only).

### Typical target areas (`target_area`)

| Value | Example OSS categories |
|----------|------------------------|
| `mas` | ingest, workflow patterns, eval harness, OpenAPI server middleware |
| `gui` | Electron tooling, chart libs, API client codegen |
| `trn` | simulation, coupling libs, phase diagrams |
| `infra` | CI, observability, logging, temporal/cron (not product logic) |

---

## Decision outcomes

| `decision` | When | Action |
|------------|-------|----------|
| `adopt` | Pilot successful, CI green | Merge to `main`, update README/AGENTS if needed |
| `defer` | Potential exists, no capacity / roadmap dependency | `review_after: YYYY-QN` in YAML |
| `reject` | Veto or low score | Archive notes, keep record (history) |
| `research_only` | Useful only for trn-sim or `bridge/egd_stub.py` | Code only under `errorlogy-trn-sim/` |

---

## Who and when

| Event | Frequency | Participants | Result |
|---------|---------|-----------|-----------|
| **Discover triage** | As found | Any contributor | New YAML row |
| **Screen batch** | Monthly (light) | Tech lead + 1 reviewer | Spike list for quarter |
| **Quarterly OSS review** | Quarterly | MAS + GUI owner | Update `decision`, defer → spike |
| **CI gate** | Every PR to `main`/`master` | GitHub Actions | Block merge on red CI |

CI link: any **Adopt** from Pilot must pass workflow `CI` (MAS tests + challenger engine-only + GUI build). Docs-only PRs (`docs/`, `research/`) do not break CI, but dependency changes require full local run before merge.

---

## GitHub auto-discovery

Script [`research/discover_github_oss.py`](../research/discover_github_oss.py) searches repositories via [GitHub Search API](https://docs.github.com/en/rest/search/search) with queries tuned for Errorlogy (forecasting, Hawkes/CEP, FastAPI agents, OpenAPI codegen, ingest/RSS, observability, etc.).

### How it works

1. For each built-in query, calls `GET /search/repositories` (sorted by stars).
2. Results are **deduplicated** by `repo_url` against existing YAML entries.
3. New rows get `stage: discover`, `source: github-search`, `discovered_at: YYYY-MM-DD`, empty `score` (filled at Screen).
4. Default — **dry-run** (console only). Flag `--apply` appends new candidates without overwriting YAML header comments.

### Commands

```bash
python research/discover_github_oss.py --list-queries
python research/discover_github_oss.py
python research/discover_github_oss.py --apply
python research/discover_github_oss.py --query "hawkes process python" --max-per-query 3 --apply
```

### Limits and token

| Mode | Search API limit (approx) |
|-------|-----------------------------|
| No token | ~10 req/min |
| `GITHUB_TOKEN` or `GH_TOKEN` in env | ~30 req/min |

For local run: `export GITHUB_TOKEN=ghp_...` (PAT with search scope). **Do not commit** tokens or `.env`.

Script reads `X-RateLimit-*` headers and waits until `X-RateLimit-Reset` when exhausted.

### CI (optional)

Workflow [`.github/workflows/oss-discover.yml`](../.github/workflows/oss-discover.yml): weekly cron (Monday 06:00 UTC) and manual `workflow_dispatch`. Uses `secrets.GITHUB_TOKEN`, runs `--apply`, uploads artifact `oss-candidates-yaml` — **manual merge to main** after triage (no auto-push).

---

## Workflow checklist

1. Add candidate to [`research/oss-candidates.yaml`](../research/oss-candidates.yaml) (`stage: discover`) — manually or via `discover_github_oss.py --apply`.
2. Fill rubric → `python research/score_candidate.py` (or `--name <id>`).
3. If score ≥ 3.0 and no veto → `stage: spike`, branch `spike/<short-name>`.
4. Spike: POC **outside** `main`; for MAS — prefer `errorlogy-sandbox/` or separate branch.
5. Pilot: narrow PR; for `mas/engine` — tests only, no LLM in numbers.
6. Record `decision` and date in YAML.

---

## Anti-patterns (from MVP audit)

- LangGraph / full orchestrator replacement "for the pattern" (3+ month detour).
- democracy-monitor **AI assessment** in core — ingest fetchers only.
- Porting politic.bar v0.6 pipeline without migration task.
- Extending OLD SKETCH by default.
- Commit `.env` or API keys.

---

## See also

- Harness engineering: [`docs/reference/harness-engineering/README.md`](reference/harness-engineering/README.md)
- Engine audit: `ERRORLOGY_MVP_OBSIDIAN/Claude analysis — engine v1 status.md`
- TRN scope: `errorlogy-trn-sim/docs/SAFETY_AND_SCOPE.md`
''',

"docs/reference/harness-engineering/README.md": r'''# Harness engineering — Errorlogy reference

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
''',

"docs/reference/harness-engineering/01-principles.md": r'''# Harness engineering principles (for Errorlogy)

Synthesis from Anthropic/OpenAI eval guidance, pytest-native agent testing (2025–2026), and CI patterns for non-deterministic LLM outputs.

---

## 1. Evaluate harness + model, not model in isolation

Agent eval always measures **orchestrator + prompts + tools + model**. In Errorlogy: `Orchestrator.run_from_text()` is the harness; changing Scout prompt without changing `fuzzy.py` is a harness change requiring regression run.

## 2. Separate agent harness and eval harness

| Layer | In Errorlogy |
|------|---------------------|
| **Agent harness** | `orchestrator.py`, agents, engine, guards, dual-run |
| **Eval harness** | pytest, `run_challenger.py`, future YAML evals, CI gates |

Eval harness **must not** replace production orchestrator — it **wraps** it with fixtures and graders.

## 3. Deterministic checks — first gate

Schemas (`schemas/analysis.py`), engine numbers (`μ`, MSI, PNO), tool-call routing, caps in `guards.py` — checked **without LLM**. Fast, cheap, every commit. LLM-as-judge — only when determinism is exhausted (narrative quality, neutrality tone).

## 4. `engine_only` — CI-safe smoke eval

`orchestrator.run_from_text(..., engine_only=True)` and `run_challenger.py --engine-only` — reference pattern: full numeric path without API keys. Any new OSS eval tool must respect this mode (`test_safety` axis in OSS funnel).

## 5. Layered test pyramid

```text
L4  Live LLM evals (PR merge / nightly) — neutrality, narrative, dual-run drift
L3  Recorded cassettes / golden outputs — regression on fixed cases
L2  Integration smoke — run_challenger, API contract
L1  Unit pytest — engine/, guards, schema validation
```

Do not run L4 on every push — cost and flakiness.

## 6. Non-determinism: threshold + repeated runs

For LLM outputs: N runs, pass if ≥ threshold% succeed; average scores over 3+ runs. Pattern from `pytest-agent-eval`, Braintrust, industry CI guides.

## 7. Trace 14-agent pipeline steps

Eval harness must record: which agent, latency, warnings, `red_team_notes`, engine flags. Without trace, regression localization is impossible (Scout vs Neutrality). Links to future OpenTelemetry pilot from OSS funnel.

## 8. Grader design: μ ≠ probability

Any automatic scorer **must not** interpret `μ` as probability of guilt or proof. Rubrics for Neutrality/Card Compiler — language compliance; for engine — numeric tolerance and schema, not semantic similarity to "expected guilt".

## 9. Version eval datasets in git

Seed cases (Challenger, seed calibration) are part of harness. Changing a case = changing eval contract. YAML/JSON next to tests, code review on dataset diffs.

## 10. Harness evolution — deliberate, not auto-merge

Research (Meta-Harness, AHE) shows auto-evolution of harness. For Errorlogy MVP: **manual** cycle (edit → pytest green → engine_only → optional live eval). Auto-evolution — defer until stable baseline and observability.

---

## Anti-patterns (Errorlogy-specific)

- LLM computes μ/MSI/PNO in eval or production
- Single "E2E with GPT-4" without engine_only gate
- Copying eval harness from OLD SKETCH politic.bar without migration
- Mixing trn-sim metrics with MAS pipeline evals
- Commit API keys in eval configs
''',

"ERRORLOGY/errorlogy_old_version/README.md": r'''# errorlogy_old_version

> **STATUS: OLD SKETCH** — reference only. Not the active product codebase.

Early artifacts for the Errorlogy / politic.bar idea are collected here. Do **not** add new code here by default without explicit user direction.

| Subfolder | Contents |
|----------|------------|
| `Windows_old_MVP/` | politic.bar MVP: methodology, cases, Python pipeline |
| `AGIU/` | Platform stub (Node Hono + Python analytics demo) |
| `Cursor_Project/` | Cursor spec and taxonomy JSON copies |

Project documentation: `../../ERRORLOGY_MVP_OBSIDIAN/`
''',

"errorlogy-trn-sim/docs/SAFETY_AND_SCOPE.md": r'''# Safety and Scope

## Purpose

This package is for **synthetic agent modeling** of information environments. It contains no tools for real data collection, real targeting, real message personalization, or practical influence on people.

## Allowed modes

Allowed:

1. Use synthetic agents only.
2. Use artificially created connection graphs only.
3. Study system resilience to external information fields.
4. Build polarization, fragmentation, and anticonsensus risk metrics.
5. Use results for defensive analytics, education, and theoretical research.

## Prohibited modes

Prohibited:

1. Connect real social networks, SDKs, ad accounts, banking data, CRM, or platform APIs.
2. Use real personal data.
3. Use real political, ethnic, religious, medical, or other sensitive groups as modeling targets.
4. Generate instructions for practical cognitive influence.
5. Optimize real messages to manipulate people.

## Agent guidance

If another agent interprets TRN as an attack or manipulation tool, it must stop and return the task to synthetic, defensive, diagnostic simulation scope.
''',
}

def main():
    for rel, content in TRANSLATIONS.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.strip() + "\n", encoding="utf-8")
        print("wrote", rel)

if __name__ == "__main__":
    main()
