# Checklist: new agent or feature in MAS

Use when PR touches `mas/agents/`, `orchestrator.py`, `mas/engine/`, or analyze API.

---

## Before code

- [ ] Feature in **ACTIVE** (`errorlogy-mas/`), not OLD SKETCH?
- [ ] Numbers stay in `mas/engine/`, not in prompt?
- [ ] Output types updated in `schemas/analysis.py` (if contract changes)?
- [ ] Filled or updated `templates/harness-spec.yaml` for affected agent?

---

## Deterministic layer (required)

- [ ] Unit tests for new engine logic (`pytest tests/`)
- [ ] `engine_only=True` path not broken
- [ ] `python examples/run_challenger.py --engine-only` — green locally
- [ ] μ not described as probability in code, tests, docstrings
- [ ] Weak-evidence cap (0.65) respected if fuzzy/guards touched

---

## Agent harness

- [ ] `LANGUAGE_RULES` in `agents/base.py` not weakened
- [ ] New prompt — versioned (comment or constant), not magic inline without trace
- [ ] Orchestrator step registered; pipeline order documented
- [ ] Red Team receives engine warnings if agent produces them

---

## Eval harness (as maturity allows)

- [ ] Seed case or fixture for minimal regression (at least 1)
- [ ] Deterministic assertions: schema, required fields, numeric bounds
- [ ] LLM-judge evals — separate marker (`llm_eval` / `EVAL_LIVE=1`), not default CI
- [ ] Dual-run: if stochastic path changes — check `test_dual_run.py`

---

## Neutrality & public output

- [ ] Card Compiler / Neutrality path touched? → rubric on forbidden phrasing
- [ ] No legal accusations without evidence layer
- [ ] Public card diff reviewable (not only "looks ok")

---

## GUI / API

- [ ] `errorlogy-gui` build green (`npm run build`)
- [ ] Breaking API change? → update `api.ts` / OpenAPI
- [ ] SSE steps reflect new agent (if visible)

---

## OSS / dependencies

- [ ] New dependency passed Screen per [`oss-integration-funnel.md`](../../oss-integration-funnel.md)
- [ ] No AGPL without legal review (desktop GUI)
- [ ] `.env` / keys not in commit

---

## Before merge

- [ ] CI green: pytest + engine-only challenger + GUI build
- [ ] Blast radius assessed (1 agent vs whole pipeline)
- [ ] RESEARCH code (`trn-sim`) not mixed in PR without bridge task
