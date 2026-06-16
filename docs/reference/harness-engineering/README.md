# Harness Engineering — справочник для Errorlogy

> **Статус:** reference handbook (без реализации кода).  
> **Ветка при создании:** `research/oss-integration-funnel`  
> **Связанные документы:** [`docs/oss-integration-funnel.md`](../../oss-integration-funnel.md), [`errorlogy-mas/AGENTS.md`](../../../errorlogy-mas/AGENTS.md)

---

## Что это

**Harness engineering** (в контексте AI-агентов) — проектирование и эволюция **обвязки** вокруг LLM: оркестрация, промпты, инструменты, состояние, детерминированные проверки, трассировка и eval-инфраструктура. Это **не** «упряжь для лошади» и не замена `mas/engine/`.

**Agent harness** — система, которая превращает модель в агента: принимает вход, вызывает tools, ведёт state, возвращает структурированный результат. В Errorlogy это в первую очередь `mas/orchestrator.py` + 14 агентов + engine-слой.

**Eval harness** — инфраструктура для прогона задач end-to-end: фикстуры кейсов, параллельный запуск, запись шагов, graders (детерминированные и LLM-as-judge), агрегация метрик, quality gates в CI. Примеры в индустрии: Anthropic evals guidance, OpenAI evals, `promptfoo`, `pytest-agent-eval`, Braintrust, LangSmith.

Исследования 2025–2026 показывают: при фиксированной модели смена harness (промпты, middleware, environment bootstrap, feedback loops) часто даёт больший прирост, чем смена модели. Для Errorlogy это означает: **инвестировать в тестируемую обвязку пайплайна**, не в «ещё один LLM для μ».

---

## Зачем Errorlogy

| Проблема MVP | Роль harness engineering |
|--------------|--------------------------|
| 14-агентный пайплайн, нелинейные регрессии | Слоистые evals: pytest → `engine_only` smoke → опциональные live LLM evals |
| Split engine vs LLM (`μ` детерминирован) | Детерминированные graders на engine; LLM-judge только на narrative/neutrality |
| Neutrality / language rules | Harness-компонент: guards + red-team + eval rubrics |
| OSS-интеграции | Воронка Discover→Adopt; eval-tools оцениваются по `test_safety` и `engine_llm_fit` |
| Desktop GUI + API | Contract tests на `schemas/analysis.py`; smoke без API keys |

**Границы:** `errorlogy-trn-sim/` — **RESEARCH**, отдельный harness; не смешивать с MAS без `bridge/`. OLD SKETCH — только reference.

---

## Содержание

| Файл | Назначение |
|------|------------|
| [01-principles.md](01-principles.md) | 10 принципов из исследования, применимых к Errorlogy |
| [02-errorlogy-mapping.md](02-errorlogy-mapping.md) | Маппинг на MAS, GUI, CI, OSS funnel |
| [03-checklist.md](03-checklist.md) | Чеклист при добавлении агента или фичи |
| [04-tools-landscape.md](04-tools-landscape.md) | Таблица OSS/SaaS инструментов с fit score |
| [05-next-steps.md](05-next-steps.md) | Pilot vs defer, стадии воронки |
| [templates/harness-spec.yaml](templates/harness-spec.yaml) | Минимальный шаблон spec для eval одного MAS-агента |

---

## Быстрые ссылки (текущий MVP)

```bash
# Детерминированные тесты (каждый PR)
cd errorlogy-mas && pytest tests/ -q

# Smoke без LLM-ключей
python errorlogy-mas/examples/run_challenger.py --engine-only
```

CI: [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml) — pytest + challenger engine-only + GUI build.

---

## Источники (внешние)

- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Anthropic — Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [OpenAI — Harness engineering (Codex)](https://openai.com/index/harness-engineering/) *(архитектурный framing)*
- [LangChain deep-agent harness rebuild](https://blog.langchain.com/) *(Terminal-Bench case study, 2026)*
- [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) — UK AISI open-source eval framework
