# Чеклист: новый агент или фича в MAS

Использовать при PR, затрагивающем `mas/agents/`, `orchestrator.py`, `mas/engine/`, или API analyze.

---

## Перед кодом

- [ ] Фича в **ACTIVE** (`errorlogy-mas/`), не OLD SKETCH?
- [ ] Числа остаются в `mas/engine/`, не в промпте?
- [ ] Output types обновлены в `schemas/analysis.py` (если меняется contract)?
- [ ] Заполнен или обновлён `templates/harness-spec.yaml` для затронутого агента?

---

## Детерминированный слой (обязательно)

- [ ] Unit-тесты на новую engine-логику (`pytest tests/`)
- [ ] `engine_only=True` путь не сломан
- [ ] `python examples/run_challenger.py --engine-only` — green локально
- [ ] μ не описан как probability в коде, тестах, docstrings
- [ ] Weak-evidence cap (0.65) учтён, если затронут fuzzy/guards

---

## Agent harness

- [ ] `LANGUAGE_RULES` в `agents/base.py` не ослаблены
- [ ] Новый промпт — versioned (комментарий или константа), не «магический» inline без следа
- [ ] Orchestrator step зарегистрирован; порядок пайплайна документирован
- [ ] Red Team получает engine warnings, если агент их производит

---

## Eval harness (по мере зрелости)

- [ ] Seed case или fixture для минимального regression (хотя бы 1)
- [ ] Детерминированные assertions: schema, required fields, numeric bounds
- [ ] LLM-judge evals — отдельный marker (`llm_eval` / `EVAL_LIVE=1`), не default CI
- [ ] Dual-run: если меняется stochastic path — проверить `test_dual_run.py`

---

## Neutrality & public output

- [ ] Card Compiler / Neutrality path затронут? → rubric на запрещённые формулировки
- [ ] Нет legal accusations без evidence layer
- [ ] Public card diff reviewable (не только «выглядит ок»)

---

## GUI / API

- [ ] `errorlogy-gui` build green (`npm run build`)
- [ ] Breaking change в API? → обновить `api.ts` / OpenAPI
- [ ] SSE steps отражают новый агент (если visible)

---

## OSS / dependencies

- [ ] Новая зависимость прошла Screen по [`oss-integration-funnel.md`](../../oss-integration-funnel.md)
- [ ] Нет AGPL без legal review (desktop GUI)
- [ ] `.env` / keys не в коммите

---

## Перед merge

- [ ] CI green: pytest + engine-only challenger + GUI build
- [ ] Blast radius оценён (1 агент vs весь pipeline)
- [ ] RESEARCH code (`trn-sim`) не смешан в PR без bridge task

---

## Быстрая классификация изменения

| Тип изменения | Минимальный eval |
|---------------|------------------|
| Только `mas/engine/` | pytest + engine_only |
| Один agent prompt | + harness-spec update + optional live spot-check |
| Orchestrator order | full regression + dual-run review |
| Schema break | pytest + API contract + GUI build |
| New OSS eval tool | Spike branch, не прямой merge |
