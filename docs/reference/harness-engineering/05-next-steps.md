# Следующие шаги (defer vs pilot)

Согласовано со стадиями [`docs/oss-integration-funnel.md`](../../oss-integration-funnel.md).

---

## Сейчас (уже есть — усилить документацией)

| Действие | Стадия | Усилие |
|----------|--------|--------|
| Держать CI: pytest + engine-only + GUI build | Adopt (gate) | 0 — поддержка |
| Документировать harness-spec per agent при изменениях | Process | низкий |
| Seed cases: Challenger + calibration seeds в version control | Adopt | низкий |

---

## Pilot (0.5–2 недели, узкий scope)

### P1 — Neutrality + Card Compiler eval (рекомендуемый первый pilot)

**Почему первым:** языковые guards — чистый LLM-eval слой; не трогает μ engine.

| Шаг | Деталь |
|-----|--------|
| Tool | `promptfoo` (red-team + custom assertions) **или** `pytest-agent-eval` YAML |
| Scope | 10–20 фраз-нарушений + 5 clean outputs из seed cases |
| Gate | `EVAL_LIVE=1` только на PR label / weekly workflow |
| Success | 0 regressions на neutrality violations; CI default остаётся keyless |

**Funnel:** Discover → Screen (fit ≥4) → Spike в `spike/neutrality-eval` → Pilot PR.

### P2 — pytest-agent-eval для Scout extraction

| Шаг | Деталь |
|-----|--------|
| Scope | 3 seed cases → `GovernanceCase` schema assertions |
| Gate | Deterministic fields only in CI; LLM fields optional live |
| Risk | Flaky extraction — use threshold 0.8, 3 runs |

### P3 — Trace middleware (OpenTelemetry)

Уже illustrative в OSS funnel (`opentelemetry-python`). Pilot: FastAPI span per agent step, export console, default off.

---

## Spike (explore, не merge)

| Кандидат | Цель | Выход |
|----------|------|-------|
| AgentProbe | Trace + cost per 14-step run | Отчёт: overhead vs value |
| checkagent record/replay | Cassette для full pipeline | Сравнение с dual-run |
| Langfuse self-hosted | Dashboard для latency | Infra decision |

Записать в `research/oss-candidates.yaml` с `target_area: mas` или `infra`.

---

## Defer

| Идея | Причина defer | Пересмотр |
|------|---------------|-----------|
| Auto harness evolution (AHE / Meta-Harness) | Нет stable observability baseline | После P1+P3 |
| Harbor / Terminal-Bench adapters | Wrong domain benchmark | Если generic agent CI template нужен |
| Full live E2E в каждом PR | Cost + keys in CI | Nightly workflow only |
| lm-evaluation-harness | Base model eval, not MAS | Never for pipeline |
| Merge trn-sim evals into MAS CI | RESEARCH boundary | Explicit bridge task |

---

## Предлагаемая очередь (Q2–Q3 2026)

```text
1. P1 Neutrality eval pilot     ← первое практическое применение
2. harness-spec.yaml для Scout, Neutrality, Red Team
3. P2 Scout schema evals (pytest-agent-eval)
4. P3 OpenTelemetry spike (infra)
5. Nightly live workflow (optional full challenger)
```

---

## Критерии Adopt для eval tool

Из OSS funnel Pilot → Adopt:

- CI green с новым tool **opt-in**
- `engine_only` не затронут
- Neutrality/language rules не ослаблены
- Документация в `docs/reference/harness-engineering/`
- Запись в `oss-candidates.yaml` → `decision: adopt`

---

## Не делать в этом этапе

- Полная реализация eval harness в `errorlogy-mas/tests/evals/` (только после P1 spike sign-off)
- Замена orchestrator
- Commit secrets в promptfoo/prompt configs
