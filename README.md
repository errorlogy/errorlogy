# Errorlogy

**https://errorlogy.com** — analytical platform for governance error patterns (non-accusatory framing).

## English quick start

| Component | Path | Role |
|-----------|------|------|
| **errorlogy-mas** | `errorlogy-mas/` | FastAPI backend — 14-agent pipeline, taxonomy v16 |
| **errorlogy-gui-v2** | `errorlogy-gui-v2/` | Browser UI (forecast, streams) |
| **Umbrella contracts** | [ai-native-gov](https://github.com/errorlogy/ai-native-gov) | Institutional topology & cross-layer schemas |

```bash
cd errorlogy-mas
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env                             # add LLM keys locally — never commit
python api/main.py                               # → http://127.0.0.1:8000/docs
```

**Cross-layer API (MVP iter 1)** — institutional activation stub (`INSTITUTIONAL_MODEL`, no μ/analyze):

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/events/cross-layer` | Frame & persist cross-layer event |
| `GET` | `/api/events/cross-layer` | List events (`?story_id=`, `?event_type=`, `?limit=`) |
| `GET` | `/api/events/cross-layer/layers` | Valid `institution:*` layer enum |
| `GET` | `/api/events/cross-layer/{event_id}` | Single event |

Schemas vendored from umbrella: `errorlogy-mas/schemas/`. OpenAPI: `/docs`.

---

**https://errorlogy.com** — аналитическая платформа об ошибках государственного управления.

> *Errors in governance as observable objects: the gap between what was declared, what was known, and what was decided.*

**Errorlogy** моделирует ошибки госуправления как наблюдаемые объекты (разрыв: заявлено / известно / решено).  
**politic.bar** — первый продукт: аналитический каталог публичных карточек без обвинительного языка.

## Слои анализа

```text
DATA → WMS → CB/SF/MP/GT/HM/... → α → ACC → PNO → FPD
```

Подробнее: [`docs/concept/`](docs/concept/) · Obsidian: [`ERRORLOGY_MVP_OBSIDIAN/`](ERRORLOGY_MVP_OBSIDIAN/)

---

# ERRORLOGY_MVP — репозиторий разработки

## Статус репозитория

Workspace объединяет **активную разработку** (новый MVP) и **архив скетчей** (ранние итерации идеи).

| Путь | Статус | Назначение |
|------|--------|------------|
| `errorlogy-mas/` | **ACTIVE** | Multi-agent backend politic.bar: 14-агентный пайплайн, taxonomy v16, FastAPI, multi-LLM router *(собрано Claude)* |
| `errorlogy-gui/` | **ACTIVE** | Electron + Vite + React desktop UI v0.2.4 (~90% API integration) |
| `errorlogy-gui-v2/` | **ACTIVE** | Browser UI v0.1 — прогноз, потоки, методология (порт 5174) |
| `ERRORLOGY/errorlogy_old_version/` | **OLD / SKETCH** | Ранние артефакты: politic.bar v0.6, AGIU, ТЗ, копии taxonomy |
| `ERRORLOGY_MVP_OBSIDIAN/` | **Документация** | Obsidian: концепция, таксономия, карта, журнал работ |

Подробнее о том, что сделал Claude: [Obsidian — errorlogy-mas](ERRORLOGY_MVP_OBSIDIAN/errorlogy-mas%20%E2%80%94%20%D0%B0%D0%BA%D1%82%D0%B8%D0%B2%D0%BD%D1%8B%D0%B9%20MVP%20(Claude).md).

## Активный MVP: errorlogy-mas

```bash
cd errorlogy-mas
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
# .env — ключи LLM (см. mas/config.py)
python examples/run_challenger.py
```

API: `python api/main.py` → http://127.0.0.1:8000/docs

## GUI: errorlogy-gui

**Terminal 1 — API:** `cd errorlogy-mas && python api/main.py`  
**Terminal 2 — UI:** `cd errorlogy-gui && npm install && npm run dev:vite` (Vite проксирует `/api` → `:8000`)

Без LLM-ключей: режим **Engine only** на странице Analyze. Подробнее: [`errorlogy-gui/README.md`](errorlogy-gui/README.md).

**Упрощённый UI прогноза:** [`errorlogy-gui-v2/README.md`](errorlogy-gui-v2/README.md) — `npm run dev` на порту 5174.

Пайплайн:

```text
Scout → WMS → Classifier → Alpha → PNO → ACC → EGD → T4D → CAT → FPD → LBI
      → Red Team → Card Compiler → Neutrality Audit
```

Источник истины по коду: `errorlogy-mas/AGENTS.md`, онтология: `errorlogy-mas/data/errorlogy_unified_taxonomy_v16.json`.

## OLD SKETCH (не расширять без явной просьбы)

| Путь | Содержимое |
|------|------------|
| `…/Windows_old_MVP/Politic Bar (pre errorlogy)/` | Методология v0.6, seed-кейсы, 8-агентный pipeline |
| `…/AGIU/` | Hono health + demo FastAPI analytics |
| `…/Cursor_Project/` | Полное ТЗ на web-MVP |

## Документация

- Obsidian: [`ERRORLOGY_MVP_OBSIDIAN/`](ERRORLOGY_MVP_OBSIDIAN/) — [главная](ERRORLOGY_MVP_OBSIDIAN/00%20%E2%80%94%20%D0%93%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0.md)
- Cursor: [`AGENTS.md`](AGENTS.md), [`.cursor/rules/`](.cursor/rules/)
- **OSS evaluation funnel:** [`docs/oss-integration-funnel.md`](docs/oss-integration-funnel.md) — воронка оценки open-source кандидатов; трекер [`research/oss-candidates.yaml`](research/oss-candidates.yaml); чеклист `python research/score_candidate.py`
- **Harness engineering:** [`docs/reference/harness-engineering/README.md`](docs/reference/harness-engineering/README.md) — eval/agent harness, принципы и чеклист для MAS

## Идея

**Errorlogy** — ошибки госуправления как наблюдаемые объекты (разрыв: заявлено / известно / решено).  
**politic.bar** — первый продукт: аналитический каталог без обвинительного языка.
