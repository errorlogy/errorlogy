# Сессия — GLM, Exa, zvec KB (2026-06-24)

> **Контекст:** интеграция LLM-провайдеров, локальной KB, Exa source discovery и уточнение smoke-кейсов для ACTIVE MVP (`errorlogy-mas/`).  
> **Связи:** [[errorlogy-mas — активный MVP (Claude)]], [[Ingest — info stream layer]], [[Roadmap — implementation log]], `AGENTS.md`

---

## Executive summary

1. **GLM-5.2** назначен на длинные нарративы: `card_compiler` и `t4d` — через OpenRouter (`z-ai/glm-5.2`) и/или прямой **Z.ai API** (`ZaiProvider`, `ZAI_API_KEY`).
2. **Локальная KB на zvec** — гибрид FTS + vector (RRF), модуль `mas/kb/`; контекст для engine T4D через `case.metadata.kb_context`.
3. **Exa** — полный контур: ingest, `source_discovery`, API `enrich_sources`, CLI `run_exa_flow.py`; `EXA_API_KEY` настроен (значение не хранить в vault).
4. **Docker не нужен** для desktop MVP: venv + `python api/main.py` + `npm run dev` в `errorlogy-gui/`.
5. **loop-library** — глобальный Cursor skill + секция в корневом `AGENTS.md`.
6. **Challenger vs Horizon (кейс)** — Challenger для офлайн engine smoke; UK Post Office Horizon — для Exa-enriched flow (не путать с Roadmap Horizon H1–H3).

---

## GLM-5.2 — card_compiler и T4D

Два пути к одной модели:

| Путь | Провайдер | Env | Модель |
|------|-----------|-----|--------|
| OpenRouter | `OpenRouterProvider` | `OPENROUTER_API_KEY` | `z-ai/glm-5.2` |
| Прямой Z.ai | `ZaiProvider` | `ZAI_API_KEY` | `glm-5.2` |

**Роутер** (`errorlogy-mas/mas/providers/router.py`):

- `AGENT_PREFERENCES`: для `card_compiler` и `t4d` в цепочке после `openai` идёт `zai`, затем `kimi`, `deepseek`, `openrouter`.
- `OPENROUTER_MODEL_MAP`: явно `z-ai/glm-5.2` для `card_compiler` и `t4d` (длинные структурированные карточки и worldline-нарратив).
- `ZAI_MODEL_MAP`: `glm-5.2` для тех же ролей.

**Зачем GLM на этих агентах:** Card Compiler генерирует 8-секционную публичную карточку; T4D (LLM-обёртка) дополняет engine worldline текстом. Оба требуют длинного связного вывода при соблюдении `LANGUAGE_RULES` (`errorlogy-mas/AGENTS.md`).

**Регистрация:** `mas/providers/__init__.py` → `build_router()` регистрирует `ZaiProvider` при наличии `ZAI_API_KEY`. Base URL: `https://api.z.ai/api/paas/v4`.

```bash
# .env (пример имён переменных — без значений)
OPENROUTER_API_KEY=...
ZAI_API_KEY=...
```

---

## zvec — локальная knowledge base

| Компонент | Путь |
|-----------|------|
| Store (hybrid query) | `errorlogy-mas/mas/kb/zvec_store.py` |
| Pipeline retrieval | `errorlogy-mas/mas/kb/retrieval.py` |
| Demo | `errorlogy-mas/examples/zvec_kb_demo.py` |
| Данные по умолчанию | `errorlogy-mas/.data/zvec_kb/` |

**Режим поиска:** `KB_QUERY_MODE=hybrid` (по умолчанию) — FTS + HNSW vector, merge через `WeightedReRanker` (RRF-style).

**Конфиг** (`mas/config.py`):

| Переменная | Default | Смысл |
|------------|---------|-------|
| `KB_ENABLED` | `true` | Включить KB (graceful off без `zvec`) |
| `KB_ZVEC_PATH` | `.data/zvec_kb` | Путь коллекции |
| `KB_TOPK` | `5` | Число сниппетов |
| `KB_QUERY_MODE` | `hybrid` | `vector` / `fts` / `hybrid` |
| `KB_INGEST_ON_SCOUT` | `false` | Индексировать после Scout |
| `KB_INGEST_ON_COMPLETE` | `false` | Индексировать после полного run |
| `KB_EMBEDDINGS` | `hash` | `sentence-transformers`, `fastembed` |

**Поток в пайплайне:**

1. `build_case_query()` собирает запрос из title, description, weak signals, top modes.
2. `attach_kb_context()` → hybrid search → `case.metadata["kb_context"]`.
3. **Engine T4D** (`mas/engine/t4d.py`, `_case_text`) дополняет `source_text` KB-контекстом при построении worldline.

> **Статус wiring:** инфраструктура и T4D-потребление готовы; вызов `attach_kb_context` в `orchestrator` перед шагами T4D / Card Compiler — следующий шаг интеграции (контекст для LLM Card пока не в prompt).

**Smoke без ключей:**

```bash
cd errorlogy-mas
python examples/zvec_kb_demo.py
```

---

## Exa — полная интеграция

| Слой | Entry | Роль Exa |
|------|-------|----------|
| Fetcher | `mas/ingest/fetchers/exa.py` | `/search` или Agent API |
| Source discovery | `mas/ingest/source_discovery.py` | `discover_sources`, `enrich_source_bundle` |
| Orchestrator | `enrich_sources=True` в `run_from_text` | Доп. источники → `raw_text` до Scout |
| API analyze | `POST /api/analyze?enrich_sources=true` | То же через REST |
| API ingest | `POST /api/ingest/fetch-exa`, `fetch-web`, `fetch-all` | Search + ingest |
| API discovery | `POST /api/ingest/discover-sources`, `/enrich-bundle` | Hits / merged bundle |
| CLI | `scripts/fetch_gov_media.py --exa-only` | Cron-friendly ingest |
| E2E demo | `examples/run_exa_flow.py` | Exa → bundle → engine-only MAS |
| Smoke | `scripts/exa_smoke.py` | Проверка конфига (ключ не печатается) |

**Env** (имена только):

| Переменная | Default | Смысл |
|------------|---------|-------|
| `EXA_API_KEY` | — | Включает Exa (graceful disable) |
| `EXA_SEARCH_TYPE` | `auto` | Режим `/search` |
| `EXA_PREFERRED` | `false` | Приоритет Exa в `fetch-web` |
| `EXA_AGENT_MODE` | `false` | Agent API вместо search |
| `EXA_AGENT_EFFORT` | `minimal` | Усилие агента |

**Приоритет web search** (без Exa): OpenRouter → Gemini → Exa. См. [[Ingest — info stream layer]].

```bash
python scripts/exa_smoke.py
python examples/run_exa_flow.py
python examples/run_exa_flow.py --no-enrich    # seed only
python examples/run_exa_flow.py --ingest       # + persist raw_documents
```

Тесты: `tests/test_source_discovery.py`, `tests/test_ingest_fetchers.py` (mock Exa).

---

## Docker — не требуется для desktop MVP

Для локальной разработки достаточно:

```bash
# Backend
cd errorlogy-mas
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# .env с ключами
python api/main.py

# GUI
cd errorlogy-gui
npm install
npm run dev:vite   # или npm run dev для Electron
```

Контейнеры в репозитории не описаны и не нужны для smoke/E2E на Windows. SQLite + локальный zvec path — file-based.

---

## loop-library (Cursor)

Глобальный skill: `~/.agents/skills/loop-library/`  
Установка: `npx skills add Forward-Future/loop-library --skill loop-library -g`

Документировано в корневом `AGENTS.md` → секция **Cursor agent tooling**:

- **loop-library** — проектирование bounded repeatable workflows (триггер, действие, верификация, stop).
- **/loop** — встроенный session cadence (отдельно от loop-library).

Примеры loop для Errorlogy: pre-merge `pytest`, `run_challenger.py --engine-only`, health `GET /api/health`.

---

## Challenger vs Horizon — выбор smoke-кейса

| | **Challenger (STS-51L, 1986)** | **Horizon (UK Post Office, 1999+)** |
|---|-------------------------------|-------------------------------------|
| Скрипт | `examples/run_challenger.py` | `examples/run_exa_flow.py` |
| Назначение | Офлайн engine smoke, pytest golden, GUI demo JSON | Exa source discovery + enriched bundle |
| Ключи | `--engine-only` без API | `EXA_API_KEY` для enrich |
| В corpus | `scripts/seed_corpus.py` (USA) | `GB-POL-1999-HORIZON-01` |

**Почему Challenger в smoke по умолчанию:**

- Хорошо документирован, public domain, богатый набор weak signals для калибровки engine.
- Не зависит от сети и внешних API — стабильный CI (`pytest`, `--engine-only`).
- Golden snapshot и dual-run benchmarks привязаны к Challenger.

**Horizon** — живой governance-кейс для проверки Exa ingest/discovery и UK media/gov контекста; в `run_exa_flow.py` явно указано: *«not Challenger»*.

> **Не путать:** Roadmap **Horizon 1/2/3** ([[Roadmap — MAS math development TZ]]) — горизонты разработки (engineering / Weak Signal / Homo-MAS), а не кейс Post Office.

---

## Быстрые команды smoke

```bash
# Engine-only, без ключей
python errorlogy-mas/examples/run_challenger.py --engine-only
pytest errorlogy-mas/tests/ -q -m "not llm_eval"

# Exa + engine (Horizon)
python errorlogy-mas/examples/run_exa_flow.py

# zvec KB demo
python errorlogy-mas/examples/zvec_kb_demo.py
```

---

## Теги

#active #errorlogy-mas #session #glm #exa #zvec #ingest #cursor

→ [[00 — Главная]] · [[Для AI-агентов]] · [[Roadmap — implementation log]]
