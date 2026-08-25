# Tools landscape eval / harness

**Fit for Errorlogy** assessment (1–5): Python MAS, `engine_only`, pytest CI, desktop GUI, split engine/LLM, neutrality rules.

| Fit | |
|-----|----------|
| 5 | Nearly native: pytest, engine-only friendly, low coupling |
| 4 | Good candidate Spike/Pilot |
| 3 | Useful with adapter pipeline |
| 2 | Strong coupling / SaaS lock-in |
| 1 | Conflicts with engine determinism veto OSS funnel |

*Licenses — at time of research; verify before Adopt.*

---

## Open source (GitHub)

| Tool | Repo | License | Purpose | Fit | Notes for Errorlogy |
|------|------|---------|------------|-----|------------------------|
| **pytest-agent-eval** | [datarootsio/pytest-agent-eval](https://github.com/datarootsio/pytest-agent-eval) | Apache-2.0 | pytest plugin, YAML evals, threshold runs, CI skip by default | **5** | Best match: Python, `EVAL_LIVE=1`, markdown reports |
| **AgentProbe** | [dyrach1o/agentprobe-framework](https://github.com/dyrach1o/agentprobe-framework) | Apache-2.0 | pytest-native traces, cost, safety scan | **4** | Trace 14 steps; rule-based eval |
| **checkagent** | [xydac/checkagent](https://github.com/xydac/checkagent) | MIT | Layered pytest, SARIF, record/replay | **4** | Multi-agent handoffs; GitHub Action |
| **rubric-eval** | [Kareem-Rashed/rubric-eval](https://github.com/Kareem-Rashed/rubric-eval) | MIT | pytest + agent tool-call metrics | **3** | Tool-call focus; domain rubrics |
| **promptfoo** | [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | MIT | YAML evals, red-team, multi-model, GHA | **4** | Neutrality red-team; Node CLI, Python-native |
| **DeepEval** | [confident-ai/deepeval](https://github.com/confident-ai/deepeval) | Apache-2.0 | pytest metrics, G-Eval judge | **3** | RAG/metrics bias; rubrics language rules |
| **Inspect AI** | [UKGovernmentBEIS/inspect_ai](https://github.com/UKGovernmentBEIS/inspect_ai) | MIT | Rigorous eval campaigns, sandboxes | **3** | Safety-critical patterns; 14-agent daily CI |
| **Harbor** | [laude-institute/harbor](https://github.com/laude-institute/harbor) | Apache-2.0 | Containerized agent benchmarks | **2** | Terminal-Bench style; governance domain |
| **Langfuse** | [langfuse/langfuse](https://github.com/langfuse/langfuse) | MIT (server) | Self-hosted tracing + evals | **3** | Infra/observability; `target_area: infra` |
| **OpenAI Evals** | [openai/evals](https://github.com/openai/evals) | MIT | Registry pattern for evals | **2** | OpenAI-centric; multi-LLM router |
| **lm-evaluation-harness** | [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) | MIT | Base model benchmarks | **1** | agent harness; MAS pipeline |
| **RAGAS** | [explodinggradients/ragas](https://github.com/explodinggradients/ragas) | Apache-2.0 | RAG metrics | **2** | MAS RAG-first |

---

## Commercial / hosted (reference)

| Tool | Site | License model | Fit | |
|------|------|---------------|-----|---------|
| **Braintrust** | [braintrust.dev](https://www.braintrust.dev) | SaaS + OSS `autoevals` | **3** | CI gates, experiments; data residency review |
| **LangSmith** | [smith.langchain.com](https://smith.langchain.com) | SaaS | **2** | LangChain coupling; MAS — custom orchestrator |
| **Weights & Biases Weave** | [wandb.ai](https://wandb.ai) | SaaS | **2** | Tracing; optional for metrics research |

---

## Errorlogy ( OSS, harness)

| Component | Role |
|-----------|------|
| `pytest` | L1 eval harness |
| `run_challenger.py --engine-only` | L2 smoke |
| GitHub Actions `ci.yml` | Quality gate |
| `research/score_candidate.py` | OSS tool screening ( eval runtime) |

---

## : gap

| Gap MAS | tools |
|---------|---------------------------|
| Per-agent regression | pytest-agent-eval, AgentProbe YAML |
| Neutrality / red-team | promptfoo redteam, checkagent safety |
| Trace 14 steps | Langfuse (pilot), OpenTelemetry (OSS funnel example) |
| Engine numeric regression | pytest only ( tool) |
| Multi-model router compare | promptfoo providers |
| trn-sim experiments | : `validate_outputs.py`, Braintrust |

---

## Veto ( Spike override)

- Tool LLM μ/MSI/PNO
- AGPL dependency desktop distribution path
- `mas/orchestrator.py` (LangGraph « »)
