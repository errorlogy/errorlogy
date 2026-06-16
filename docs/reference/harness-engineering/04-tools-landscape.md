# Ландшафт инструментов eval / harness

Оценка **fit для Errorlogy** (1–5): учёт Python MAS, `engine_only`, pytest CI, desktop GUI, split engine/LLM, neutrality rules.

| Fit | Значение |
|-----|----------|
| 5 | Почти native: pytest, engine-only friendly, low coupling |
| 4 | Хороший кандидат для Spike/Pilot |
| 3 | Полезно с адаптером или только для части pipeline |
| 2 | Сильная привязка к другому стеку / SaaS lock-in |
| 1 | Конфликт с engine determinism или veto OSS funnel |

*Лицензии — на момент исследования; проверять перед Adopt.*

---

## Open source (GitHub)

| Tool | Repo | License | Назначение | Fit | Заметки для Errorlogy |
|------|------|---------|------------|-----|------------------------|
| **pytest-agent-eval** | [datarootsio/pytest-agent-eval](https://github.com/datarootsio/pytest-agent-eval) | Apache-2.0 | pytest plugin, YAML evals, threshold runs, CI skip by default | **5** | Лучший match: Python, `EVAL_LIVE=1`, markdown reports |
| **AgentProbe** | [dyrach1o/agentprobe-framework](https://github.com/dyrach1o/agentprobe-framework) | Apache-2.0 | pytest-native traces, cost, safety scan | **4** | Trace 14 steps; rule-based eval |
| **checkagent** | [xydac/checkagent](https://github.com/xydac/checkagent) | MIT | Layered pytest, SARIF, record/replay | **4** | Multi-agent handoffs; GitHub Action |
| **rubric-eval** | [Kareem-Rashed/rubric-eval](https://github.com/Kareem-Rashed/rubric-eval) | MIT | pytest + agent tool-call metrics | **3** | Tool-call focus; меньше domain rubrics |
| **promptfoo** | [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | MIT | YAML evals, red-team, multi-model, GHA | **4** | Neutrality red-team; Node CLI, не Python-native |
| **DeepEval** | [confident-ai/deepeval](https://github.com/confident-ai/deepeval) | Apache-2.0 | pytest metrics, G-Eval judge | **3** | RAG/metrics bias; настроить rubrics под language rules |
| **Inspect AI** | [UKGovernmentBEIS/inspect_ai](https://github.com/UKGovernmentBEIS/inspect_ai) | MIT | Rigorous eval campaigns, sandboxes | **3** | Safety-critical patterns; тяжёлый для 14-agent daily CI |
| **Harbor** | [laude-institute/harbor](https://github.com/laude-institute/harbor) | Apache-2.0 | Containerized agent benchmarks | **2** | Terminal-Bench style; не governance domain |
| **Langfuse** | [langfuse/langfuse](https://github.com/langfuse/langfuse) | MIT (server) | Self-hosted tracing + evals | **3** | Infra/observability; `target_area: infra` |
| **OpenAI Evals** | [openai/evals](https://github.com/openai/evals) | MIT | Registry pattern for evals | **2** | OpenAI-centric; адаптация под multi-LLM router |
| **lm-evaluation-harness** | [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) | MIT | Base model benchmarks | **1** | Не agent harness; не для MAS pipeline |
| **RAGAS** | [explodinggradients/ragas](https://github.com/explodinggradients/ragas) | Apache-2.0 | RAG metrics | **2** | MAS не RAG-first |

---

## Commercial / hosted (reference)

| Tool | Site | License model | Fit | Заметки |
|------|------|---------------|-----|---------|
| **Braintrust** | [braintrust.dev](https://www.braintrust.dev) | SaaS + OSS `autoevals` | **3** | CI gates, experiments; data residency review |
| **LangSmith** | [smith.langchain.com](https://smith.langchain.com) | SaaS | **2** | LangChain coupling; MAS — custom orchestrator |
| **Weights & Biases Weave** | [wandb.ai](https://wandb.ai) | SaaS | **2** | Tracing; optional for metrics research |

---

## Уже в Errorlogy (не OSS, но harness)

| Компонент | Роль |
|-----------|------|
| `pytest` | L1 eval harness |
| `run_challenger.py --engine-only` | L2 smoke |
| GitHub Actions `ci.yml` | Quality gate |
| `research/score_candidate.py` | OSS tool screening (не eval runtime) |

---

## Матрица: что закрывает какой gap

| Gap MAS | Рекомендуемый класс tools |
|---------|---------------------------|
| Per-agent regression | pytest-agent-eval, AgentProbe YAML |
| Neutrality / red-team | promptfoo redteam, checkagent safety |
| Trace 14 steps | Langfuse (pilot), OpenTelemetry (OSS funnel example) |
| Engine numeric regression | pytest only (не внешний tool) |
| Multi-model router compare | promptfoo providers |
| trn-sim experiments | Отдельно: `validate_outputs.py`, не Braintrust |

---

## Veto (не Spike без override)

- Tool требует LLM для вычисления μ/MSI/PNO
- AGPL dependency в desktop distribution path
- Замена `mas/orchestrator.py` целиком (LangGraph «ради паттерна»)
