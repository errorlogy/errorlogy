# Принципы harness engineering (для Errorlogy)

Синтез из Anthropic/OpenAI eval guidance, pytest-native agent testing (2025–2026) и паттернов CI для non-deterministic LLM outputs.

---

## 1. Оценивайте harness + model, не модель в вакууме

Eval «агента» всегда измеряет связку **orchestrator + prompts + tools + model**. В Errorlogy: `Orchestrator.run_from_text()` — это harness; смена промпта Scout без смены `fuzzy.py` — harness change, требующий регрессионного прогона.

## 2. Разделяйте agent harness и eval harness

| Слой | Что это в Errorlogy |
|------|---------------------|
| **Agent harness** | `orchestrator.py`, agents, engine, guards, dual-run |
| **Eval harness** | pytest, `run_challenger.py`, будущие YAML evals, CI gates |

Eval harness **не должен** подменять production orchestrator — он его **оборачивает** фикстурами и graders.

## 3. Детерминированные проверки — первый рубеж

Схемы (`schemas/analysis.py`), числа engine (`μ`, MSI, PNO), routing tool calls, caps в `guards.py` — проверяются **без LLM**. Быстро, дёшево, на каждый commit. LLM-as-judge — только когда детерминизм исчерпан (narrative quality, neutrality tone).

## 4. `engine_only` — CI-safe smoke eval

`orchestrator.run_from_text(..., engine_only=True)` и `run_challenger.py --engine-only` — эталонный паттерн: полный числовой путь без API keys. Любой новый OSS eval-tool обязан уважать этот режим (ось `test_safety` в OSS funnel).

## 5. Слоистая пирамида тестов

```text
L4  Live LLM evals (PR merge / nightly) — neutrality, narrative, dual-run drift
L3  Recorded cassettes / golden outputs — regression на фиксированных кейсах
L2  Integration smoke — run_challenger, API contract
L1  Unit pytest — engine/, guards, schema validation
```

Не поднимать L4 на каждый push — cost и flakiness.

## 6. Non-determinism: threshold + repeated runs

Для LLM-выходов: N прогонов, pass если ≥ threshold% успешны; усреднение scores по 3+ runs. Паттерн из `pytest-agent-eval`, Braintrust, industry CI guides.

## 7. Трассировка шагов 14-агентного пайплайна

Eval harness должен записывать: какой агент, latency, warnings, `red_team_notes`, engine flags. Без trace невозможно локализовать регрессию (Scout vs Neutrality). Связь с будущим OpenTelemetry pilot из OSS funnel.

## 8. Grader design: μ ≠ probability

Любой автоматический scorer **не должен** интерпретировать `μ` как вероятность вины или доказанность. Rubrics для Neutrality/Card Compiler — language compliance; для engine — numeric tolerance и schema, не semantic similarity к «ожидаемой вине».

## 9. Версионируйте eval datasets в git

Seed-кейсы (Challenger, seed calibration) — часть harness. Изменение кейса = изменение eval contract. YAML/JSON рядом с тестами, code review на dataset diffs.

## 10. Harness evolution — осознанно, не auto-merge

Исследования (Meta-Harness, AHE) показывают auto-evolution harness. Для MVP Errorlogy: **ручной** цикл (edit → pytest green → engine_only → optional live eval). Auto-evolution — defer до стабильного baseline и observability.

---

## Анти-паттерны (специфичные для Errorlogy)

- LLM считает μ/MSI/PNO в eval или production
- Один «E2E с GPT-4» без engine_only gate
- Копирование eval harness из OLD SKETCH politic.bar без migration
- Смешение trn-sim метрик с MAS pipeline evals
- Commit API keys в eval configs
