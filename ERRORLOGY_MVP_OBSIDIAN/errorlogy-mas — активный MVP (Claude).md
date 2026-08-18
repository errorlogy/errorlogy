# errorlogy-mas — активный MVP (Claude)

> **Статус:** ACTIVE · **Автор сборки:** Claude (Claude Code) · **Продукт:** politic.bar backend

Зафиксировано, чтобы Cursor и другие агенты не путали этот код с **OLD SKETCH** в `errorlogy_old_version/`.

## Что сделано

### Backend MAS (`errorlogy-mas/`)

1. **14-агентный пайплайн** по ТЗ (`Cursor_Project/TZ_Cursor_Errorlogy_politicbar_FULL.md`):

```text
Scout → WMS → Classifier → Alpha → PNO → ACC → EGD → T4D → CAT → FPD → LBI
      → Red Team → Card Compiler → Neutrality Audit
```

2. **Онтология v16** — `data/errorlogy_unified_taxonomy_v16.json` (381 mode universe, alpha edges).

3. **Analytics Engine v1** (`mas/engine/`, `ENGINE_VERSION = v1-math`) — детерминированная математика:
   - `fuzzy`, `alpha`, `wms`, `pno`, `acc`, `egd`, `t4d`, `cat`, `fpd`, `guards`
   - numpy / scipy / networkx / sklearn / sympy / ruptures
   - LLM **не** считает числа — только Scout, LBI, Red Team, Card, Neutrality
   - `engine_only=True` в orchestrator и `POST /api/analyze?engine_only=true`
   - `pytest tests/` — 16 тестов, Challenger smoke без LLM

4. **Multi-LLM router** — `mas/providers/`: Anthropic, OpenAI, DeepSeek, Groq, Google, Kimi, OpenRouter, **Z.ai (`ZaiProvider`)** с fallback по ролям агентов.

   - **GLM-5.2** для `card_compiler` и `t4d`: OpenRouter `z-ai/glm-5.2` и/или прямой `ZAI_API_KEY` → `glm-5.2`
   - См. [[Сессия — GLM Exa zvec KB 2026-06-24]]

5. **Локальная KB (zvec)** — `mas/kb/`: hybrid FTS + vector search; demo `examples/zvec_kb_demo.py`; env `KB_*` в `mas/config.py`.

6. **Exa source discovery** — `mas/ingest/source_discovery.py`, `enrich_sources` в orchestrator/API; E2E `examples/run_exa_flow.py` (кейс Horizon, не Challenger).

7. **Схемы** — `mas/schemas/analysis.py` (`CaseAnalysis`, `ModeScore`, WMS, PNO, ACC, T4D, CAT, FPD, LBI, …).

8. **FastAPI** — `api/main.py`:
   - `POST /api/analyze` (JWT), `?enrich_sources=true`
   - `GET /api/taxonomy`, `/api/taxonomy/mode/{id}`, `/api/taxonomy/edges`
   - OAuth: Google, GitHub, Telegram

9. **Демо Challenger** — `examples/run_challenger.py` → `examples/challenger_output.json` (офлайн engine smoke).

10. **Демо Exa** — `examples/run_exa_flow.py` (UK Post Office Horizon + source discovery).

11. **Правила языка** — `mas/agents/base.py` + `errorlogy-mas/AGENTS.md` (μ ≠ вероятность, без обвинений).

### UI (`errorlogy-gui/`)

→ Подробно: [[errorlogy-gui — desktop app v0.2]]

- **Electron 0.2** — Dashboard, Analyze, Result, Taxonomy, **3D Globe**
- Подключён к FastAPI `:8000`; `GET /api/stats/countries` для глобуса
- Windows: `scripts/reinstall.ps1` (uninstall + NSIS install)

### Инфраструктура

- `.claude/settings.local.json` — разрешения Claude на pip / run_challenger
- `.cursor/hooks.json` — obsidian-memory после ответов агента

## Analytics Engine v1 (детали)

| Критерий | Статус |
|----------|--------|
| `pytest` green | ✅ 16 tests |
| Classifier ≥200 кандидатов | ✅ 217 atomic + universe pre-filter |
| weak evidence μ ≤ 0.65 | ✅ `guards.py` после fuzzy + alpha |
| Детерминизм WMS/PNO/ACC/CAT/FPD | ✅ engine path |
| Human-readable mode names | ✅ `taxonomy.get_mode_name()` |
| `GET /api/health` → `engine: v1-math` | ✅ |

**Out of scope v1:** корпус 200 кейсов, SSE streaming в GUI, LBI с cvxpy, production CI.

## Что не сделано

- GUI politic.bar (полный каталог, граф режимов)
- Корпус 200 кейсов из ТЗ
- Production deploy, CI pipeline
- Слияние со старым 8-агентным `politic_bar/` pipeline

## Запуск

> **Docker не нужен** для desktop dev — venv + локальный API + Electron GUI.

```bash
cd errorlogy-mas
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
# .env — ключи (см. mas/config.py): OPENROUTER_API_KEY, ZAI_API_KEY, EXA_API_KEY, …
python examples/run_challenger.py
python examples/run_challenger.py --engine-only   # без LLM, Challenger smoke
python examples/run_exa_flow.py                  # Exa + Horizon case
python examples/zvec_kb_demo.py                  # zvec hybrid KB
pytest tests/
python api/main.py
```

## Связи

| Ресурс | Роль |
|--------|------|
| [[Таксономия/00 — Индекс таксономии]] | Человекочитаемая карта v16 (Obsidian) |
| [[politic.bar — скетч MVP]] | OLD SKETCH: методология + seed cases |
| [[Flows/00 — Flow Index]] | Гипотезы и эксперименты |
| [[Сессия — GLM Exa zvec KB 2026-06-24]] | GLM, Z.ai, zvec, Exa, smoke-кейсы |
| `errorlogy-mas/README.md` | Техническая документация на английском |

## Теги

#active #errorlogy-mas #claude #politic-bar #mvp

→ [[00 — Главная]] · [[Карта артефактов]] · [[Для AI-агентов]]
