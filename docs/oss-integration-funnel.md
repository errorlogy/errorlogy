# Воронка оценки OSS-интеграций для Errorlogy

> **Статус:** процесс + шаблон трекера (без фактических интеграций).  
> **Связанные документы:** [`AGENTS.md`](../AGENTS.md), [`errorlogy-mas/AGENTS.md`](../errorlogy-mas/AGENTS.md), [`research/oss-candidates.yaml`](../research/oss-candidates.yaml).

Опционально: симлинк в Obsidian → `ERRORLOGY_MVP_OBSIDIAN/OSS — воронка интеграции.md` → `../docs/oss-integration-funnel.md`.

---

## Зачем

Errorlogy MVP состоит из нескольких зон с разными правилами внедрения. Новые open-source проекты на GitHub (оркестраторы, observability, codegen, workflow engines и т.д.) нужно **отфильтровать до кода**, чтобы:

- не нарушить split **engine (μ, детерминизм) vs LLM (интерпретация)**;
- не тащить паттерны из **OLD SKETCH** в ACTIVE без migration task;
- не смешивать **RESEARCH** (`errorlogy-trn-sim`) с 14-агентным пайплайном без явного bridge;
- сохранить воспроизводимость аналитики и прохождение **CI** ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)).

---

## Границы репозитория

| Метка | Путь | Правило для OSS |
|-------|------|-----------------|
| **ACTIVE** | `errorlogy-mas/`, `errorlogy-gui/` | Только после Pilot; обязателен CI green |
| **RESEARCH** | `errorlogy-trn-sim/` | Допустимы эксперименты; в MAS — только через `bridge/` + отдельное решение |
| **OLD SKETCH** | `ERRORLOGY/errorlogy_old_version/` | Справочник и seed-кейсы; **не** источник кода для копипаста |

---

## Стадии воронки

```text
Discover → Screen → Spike → Pilot → Adopt | Reject | Defer
```

| Стадия | Цель | Артефакты | Выход |
|--------|------|-----------|-------|
| **Discover** | Зафиксировать кандидата | Запись в `research/oss-candidates.yaml` | `stage: discover` |
| **Screen** | Быстрый отсев по рубрике | Заполненный `score`, заметки | Переход в Spike **или** Reject/Defer |
| **Spike** | 0.5–2 дня: POC в ветке / sandbox | Ветка `spike/<name>`, заметки в `notes_ru` | Go/no-go для Pilot |
| **Pilot** | Ограниченный scope в целевой зоне | PR в `research/oss-integration-funnel` или feature-ветку | Метрики, diff blast radius |
| **Adopt** | Merge в ACTIVE | Документация, тесты, CI | `decision: adopt` |
| **Reject** | Не подходит | Причина в трекере | `decision: reject` |
| **Defer** | Потенциально позже | Условие пересмотра | `decision: defer` |
| **Research-only** | Только trn-sim / bridge | Не трогать `mas/agents/` | `decision: research_only` |

**Порог Screen → Spike:** суммарный взвешенный балл ≥ **3.0** из 5.0 (см. рубрику) **и** нет автоматического veto (см. ниже).

**Порог Pilot → Adopt:** CI green (`pytest`, `run_challenger.py --engine-only`, `npm run build` для GUI); для engine-изменений — без LLM в числовых путях; Neutrality/language rules не ослаблены.

---

## Рубрика оценки (1–5)

Каждая ось: **1** = плохо для Errorlogy, **5** = отлично. Веса можно менять; дефолт — равные.

| Ось | Вес | 1 (риск) | 5 (хорошо) | Контекст Errorlogy |
|-----|-----|----------|------------|-------------------|
| **coupling** | 1.0 | Жёсткая привязка к фреймворку, сложно вырезать | Тонкий адаптер, optional dependency | MAS orchestrator, GUI `api.ts` |
| **duplication** | 1.0 | Дублирует `mas/engine/*`, taxonomy, orchestrator | Закрывает явный gap (ingest, metrics UI) | Не второй fuzzy/PNO |
| **test_safety** | 1.2 | Ломает `engine_only` / детерминизм μ | Хорошо мокается, покрывается pytest | `pytest tests/`, challenger smoke |
| **blast_radius** | 1.2 | Трогает все 14 агентов + схемы | Локальный модуль (1 пакет) | `schemas/analysis.py` — высокий радиус |
| **license** | 1.0 | AGPL/неясная лицензия для desktop | MIT/Apache-2.0, совместима с Electron | GUI distribution |
| **maintenance** | 0.8 | Заброшен >12 мес, мало contributors | Активные релизы, used in prod | |
| **engine_llm_fit** | 1.5 | Толкает LLM считать μ/MSI/PNO | Усиливает engine **или** чисто infra/UX | См. `errorlogy-mas/AGENTS.md` |
| **old_sketch_risk** | 1.0 | Копипаст из politic.bar v0.6 / AGIU | Независим от OLD SKETCH | Migration task если overlap |

**Формула:** `score_total = Σ(weight × value) / Σ(weight)` → число 1..5 в YAML.

### Автоматические veto (Reject без Spike)

- Предлагает заменить `mas/engine/` вычислениями LLM.
- Требует merge кода из `errorlogy_old_version/` без migration task.
- Лицензия несовместима с распространением GUI (проверить юристом при сомнении).
- Втягивает «concern scoring / AI assessment» чужого продукта в core engine (см. Roadmap Phase H — только ingest-плагины).

### Типичные целевые зоны (`target_area`)

| Значение | Примеры OSS-категорий |
|----------|------------------------|
| `mas` | ingest, workflow patterns, eval harness, OpenAPI server middleware |
| `gui` | Electron tooling, chart libs, API client codegen |
| `trn` | simulation, coupling libs, phase diagrams |
| `infra` | CI, observability, logging, temporal/cron (не путать с product logic) |

---

## Исходы решения

| `decision` | Когда | Действие |
|------------|-------|----------|
| `adopt` | Pilot успешен, CI green | Merge в `main`, обновить README/AGENTS при необходимости |
| `defer` | Потенциал есть, нет capacity / зависимость от roadmap | `review_after: YYYY-QN` в YAML |
| `reject` | Veto или низкий score | Архивировать заметки, не удалять запись (история) |
| `research_only` | Полезно только для trn-sim или `bridge/egd_stub.py` | Код только под `errorlogy-trn-sim/` |

---

## Кто и когда

| Событие | Частота | Участники | Результат |
|---------|---------|-----------|-----------|
| **Триаж Discover** | По мере находок | Любой контрибьютор | Новая строка в YAML |
| **Screen batch** | Ежемесячно (лёгкий) | Tech lead + 1 reviewer | Spike-лист на квартал |
| **Quarterly OSS review** | Раз в квартал | Владелец MAS + GUI | Обновление `decision`, defer → spike |
| **CI gate** | Каждый PR в `main`/`master` | GitHub Actions | Блок merge при красном CI |

Связь с CI: любой **Adopt** из Pilot обязан проходить workflow `CI` (MAS tests + challenger engine-only + GUI build). Документационные PR (только `docs/`, `research/`) CI не ломают, но при изменении зависимостей — полный прогон локально перед merge.

---

## Автообход GitHub

Скрипт [`research/discover_github_oss.py`](../research/discover_github_oss.py) ищет репозитории через [GitHub Search API](https://docs.github.com/en/rest/search/search) по профилям запросов, заточенным под Errorlogy (forecasting, Hawkes/CEP, FastAPI agents, OpenAPI codegen, ingest/RSS, observability и т.д.).

### Как это работает

1. Для каждого встроенного запроса вызывается `GET /search/repositories` (сортировка по звёздам).
2. Результаты **дедуплицируются** по `repo_url` относительно уже существующих записей в YAML.
3. Новые строки получают `stage: discover`, `source: github-search`, `discovered_at: YYYY-MM-DD`, пустой `score` (рубрику заполняют на Screen).
4. По умолчанию — **dry-run** (только вывод в консоль). Флаг `--apply` дописывает новые кандидаты в конец списка `candidates` без перезаписи комментариев в начале файла.

### Команды

```bash
# Просмотр встроенных запросов
python research/discover_github_oss.py --list-queries

# Dry-run (без записи)
python research/discover_github_oss.py

# Записать новых кандидатов в трекер
python research/discover_github_oss.py --apply

# Один запрос, до 3 репозиториев
python research/discover_github_oss.py --query "hawkes process python" --max-per-query 3 --apply
```

### Лимиты и токен

| Режим | Лимит search API (ориентир) |
|-------|-----------------------------|
| Без токена | ~10 запросов/мин |
| `GITHUB_TOKEN` или `GH_TOKEN` в окружении | ~30 запросов/мин |

Для локального запуска: `export GITHUB_TOKEN=ghp_...` (PAT без лишних scope достаточно для search). **Не коммитить** токены и `.env`.

Скрипт читает заголовки `X-RateLimit-*` и при исчерпании лимита ждёт до `X-RateLimit-Reset`.

### CI (опционально)

Workflow [`.github/workflows/oss-discover.yml`](../.github/workflows/oss-discover.yml): еженедельный cron (понедельник 06:00 UTC) и ручной `workflow_dispatch`. Использует встроенный `secrets.GITHUB_TOKEN`, запускает `--apply`, выкладывает артефакт `oss-candidates-yaml` — **merge в main вручную** после триажа (авто-push не настроен).

### Поля автообнаружения

| Поле | Значение |
|------|----------|
| `source` | `github-search` |
| `search_query` | запрос, которым найден репозиторий |
| `discovered_at` | дата ISO |
| `github_stars` | звёзды на момент обхода |
| `decision` | `pending` |

После обхода: `python research/score_candidate.py` для Screen и решение spike / reject / defer.

---

## Рабочий процесс (чеклист)

1. Добавить кандидата в [`research/oss-candidates.yaml`](../research/oss-candidates.yaml) (`stage: discover`) — вручную или через `discover_github_oss.py --apply`.
2. Заполнить рубрику → `python research/score_candidate.py` (или `--name <id>`).
3. При score ≥ 3.0 и без veto → `stage: spike`, ветка `spike/<short-name>`.
4. Spike: POC **вне** `main`; для MAS — предпочтительно `errorlogy-sandbox/` или отдельная ветка.
5. Pilot: узкий PR; для `mas/engine` — только с тестами и без LLM в числах.
6. Зафиксировать `decision` и дату в YAML.

---

## Пример: OpenTelemetry (illustrative)

См. запись `opentelemetry-python` в трекере — **пример, решение не принято**.

- **Discover:** нужна трассировка latency 14 шагов pipeline.
- **Screen:** высокий `test_safety`, низкий `engine_llm_fit` risk (infra), `target_area: infra`.
- **Spike:** middleware в FastAPI + export в console, без изменения agent prompts.
- **Pilot:** opt-in flag в API, default off.
- **Adopt/Reject:** по итогам overhead и пользе для `/#/mas` metrics.

---

## Анти-паттерны (из аудита MVP)

- LangGraph / полная замена orchestrator «ради паттерна» (3+ месяца detour).
- democracy-monitor **AI assessment** в core — только ingest fetchers.
- Портирование politic.bar v0.6 pipeline без migration task.
- Расширение OLD SKETCH по умолчанию.
- Commit `.env` или API keys.

---

## См. также

- Harness engineering (eval/agent harness, принципы, чеклист): [`docs/reference/harness-engineering/README.md`](reference/harness-engineering/README.md)
- Engine audit: `ERRORLOGY_MVP_OBSIDIAN/Анализ Claude — состояние engine v1.md`
- TRN scope: `errorlogy-trn-sim/docs/SAFETY_AND_SCOPE.md`
- Roadmap OSS mentions: `ERRORLOGY_MVP_OBSIDIAN/Roadmap — MAS math development TZ.md`
