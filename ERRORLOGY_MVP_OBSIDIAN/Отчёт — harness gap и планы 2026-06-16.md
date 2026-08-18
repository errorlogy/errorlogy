# Отчёт — harness gap и планы (2026-06-16)

> **Ветка:** `research/oss-integration-funnel`  
> **Контекст:** повторный аудит после Phase A + Phase B harness engineering  
> **Связанные документы:** [[errorlogy-mas — активный MVP (Claude)]], `docs/reference/harness-engineering/06-gap-audit-2026.md`

---

## Executive summary

После Phase A/B/C (Scout pilot) зрелость eval-harness выросла с **~40–45%** до **~63%**. L1 (~68%): golden snapshot, API smoke, **88 keyless pytest**, CI с `-m "not llm_eval"`. L2: два live pilot — Neutrality **20/20**, Scout extraction **12/12** при `EVAL_LIVE=1`. Главные оставшиеся разрывы: generic spec→pytest driver, Card Compiler eval, cassettes, Red Team live.

**Прогон тестов (2026-06-16, обновлено):**

| Команда | Результат |
|---------|-----------|
| `py -3.12 -m pytest tests/ -q -m "not llm_eval"` | **88 passed**, 32 deselected |
| `EVAL_LIVE=1 pytest tests/evals/test_neutrality_live.py -m llm_eval` | **20 passed**, 10 deselected |
| `EVAL_LIVE=1 pytest tests/evals/test_scout_extraction_live.py -m llm_eval` | **12 passed**, 14 deselected (~79s) |

---

## Оценки зрелости harness

| Слой | Было (2026-06-15) | Стало (2026-06-16) | Δ | Комментарий |
|------|-------------------|---------------------|---|-------------|
| **L1 — Engine + CI** | ~55% | **~68%** | +13 | Golden baseline, API smoke, 74 keyless теста, CI pytest + engine-only |
| **L2 — LLM-агенты** | ~42% | **~62%** | +20 | Neutrality + Scout live pilots; Red Team — только spec |
| **L3 — Процесс + tooling** | ~38% | **~50%** | +12 | Handbook, vault→.env, eval-live.yml; promptfoo/nightly — нет |
| **Общая зрелость** | ~40–45% | **~63%** | +18–23 | L1 силён; L2 — два агента с live eval |

### Пирамида eval (факт)

```text
L4 Live LLM eval     [██] Neutrality ✅ Scout ✅; Card/Red Team — нет
L3 Golden/cassettes  [~]  engine baseline ✅; full pipeline cassettes — нет
L2 Integration       [██] engine_only smoke + API contract
L1 Unit pytest       [███] engine modules + ingest + guards
```

---

## Phase A — выполнено ✅

| Артефакт | Путь |
|----------|------|
| Golden engine snapshot | `errorlogy-mas/tests/test_challenger_engine_snapshot.py` + `fixtures/challenger_engine_baseline.json` |
| API smoke | `errorlogy-mas/tests/test_api_analyze.py` |
| Harness-spec (3 агента) | `errorlogy-mas/tests/evals/specs/{scout,neutrality,red_team}.yaml` |

**Коммит:** `dbd2ba2`

---

## Phase B — выполнено ✅

| Артефакт | Путь |
|----------|------|
| Seed packs | `tests/evals/seeds/neutrality_violations.yaml` (15), `neutrality_clean.yaml` (5), `scout_extraction.yaml` (stub) |
| Live Neutrality eval | `tests/evals/test_neutrality_live.py` (`llm_eval`, `EVAL_LIVE=1`) |
| Vault → .env | `scripts/load_keys_from_vault.ps1` |
| CI live eval (manual) | `.github/workflows/eval-live.yml` (`workflow_dispatch`) |

**Коммит:** `05a6c69`

---

## Оставшиеся gap

### P0 (критично для следующего спринта)

| Gap | Статус |
|-----|--------|
| Scout extraction live eval | ✅ `0c4c91a` — 12 seeds, 12/12 live |
| Generic spec→pytest driver (Neutrality + Scout hand-wired) | Отсутствует |

### P1 (важно)

| Gap | Статус |
|-----|--------|
| Card Compiler + Neutrality joint eval | Deferred |
| Recorded outputs / cassettes full pipeline | Deferred |
| Red Team live eval harness | Spec only |
| CI: явный `-m "not llm_eval"` в ci.yml | ✅ Done (`0c4c91a`) |

### P2 (улучшения)

| Gap | Статус |
|-----|--------|
| OpenTelemetry per-agent spans | P3 в roadmap |
| Nightly live workflow (`run_challenger.py` full) | Deferred |
| Eval tool funnel → Adopt (promptfoo и др.) | Partial discover |

---

## Phase C roadmap (следующий harness)

1. ~~Scout extraction live eval~~ ✅ (`test_scout_extraction_live.py`, commit `0c4c91a`)
2. **P1 — Card Compiler eval** — joint с Neutrality
3. **P3 — OpenTelemetry** — FastAPI span per agent step
4. **Nightly live workflow** — full challenger с keys
5. **Generic eval runner** — spec YAML → pytest (не только Neutrality)

См. `docs/reference/harness-engineering/05-next-steps.md`

---

## Прочие планы проекта (чеклист)

| План | Статус | Заметки |
|------|--------|---------|
| **errorlogy-gui v1** (Electron **0.2.5**) | ✅ ~90% MAS API | API autostart из ярлыка, `py -3.12` + `api-startup.log` |
| **errorlogy-gui-v2** (прогноз, **:5174**) | ✅ v0.1 browser | `/`, `/case`, `/stream`, `/data` — без Electron |
| **GUI integration Phase 1–2** | ✅ Done | Result из API, deep links, ingest/history, taxonomy |
| **GUI integration Phase 3** | ⏳ Pending | OAuth UI, export, lazy Globe code-split |
| **OSS integration funnel** + `discover_github_oss.py` | ✅ Branch + docs | `research/oss-integration-funnel`, `docs/oss-integration-funnel.md` |
| **Harness engineering handbook** | ✅ Done | `docs/reference/harness-engineering/` (8 файлов) |
| **Minimal CI** | ✅ Done | `.github/workflows/ci.yml` — pytest + engine-only + GUI build |
| **Refactoring audit** | ✅ Рекомендации | Точечный refactor: OpenAPI types GUI↔API, split ingest, lazy Globe; orchestrator не трогать |
| **GITHUB_TOKEN 401** (`discover_github_oss.py`) | ⚠️ Blocked | Токен в `.env` отвечает 401 — проверить Active + scope `public_repo`; dry-run без токена работает с лимитом |

---

## Следующие 3 действия

1. **Generic spec→pytest driver** — обобщить Neutrality + Scout runners.
2. **Card Compiler live eval** — joint с Neutrality на публичном output.
3. **GUI v2 E2E smoke** — Challenger `engine_only` на `:5174`.

---

## Следующие шаги (приоритизация, 2026-06-16)

| Горизонт | Действие | Почему |
|----------|----------|--------|
| ~~Неделя~~ | ~~Scout live eval~~ | ✅ `0c4c91a` |
| ~~Неделя~~ | ~~`-m "not llm_eval"` в ci.yml~~ | ✅ `0c4c91a` |
| **Неделя** | GUI v2 smoke `engine_only` на `:5174` | Параллельно harness; фиксирует product loop |
| **2–4 нед** | Generic spec→pytest driver | После Scout (2-й агент), не раньше |
| **2–4 нед** | Card Compiler + Neutrality joint eval | Замыкает публичный output chain |
| **Отложить** | OTel, nightly full challenger, promptfoo adopt | Observability/cost без роста eval coverage |
| **Отложить** | Agent-Reach в MAS | `discover`, verdict maybe; cherry-pick CLIs при ingest-spike |
| **Отложить** | GITHUB_TOKEN 401 | Dry-run работает; unblock когда нужен OSS discover |

---

## Ссылки

- Handbook: `docs/reference/harness-engineering/README.md`
- Gap audit (обновлён): `docs/reference/harness-engineering/06-gap-audit-2026.md`
- OSS funnel: `docs/oss-integration-funnel.md`
- GUI v1: [[errorlogy-gui — desktop app v0.2]]
- MAS: [[errorlogy-mas — активный MVP (Claude)]]

---

*Сгенерировано агентом Cursor, 2026-06-16. Секреты и API keys не включены.*
