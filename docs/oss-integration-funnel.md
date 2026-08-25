# OSS integration evaluation funnel for Errorlogy

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
