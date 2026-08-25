# Harness engineering principles (for Errorlogy)

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
