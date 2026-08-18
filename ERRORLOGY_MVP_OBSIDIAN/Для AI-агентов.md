# Для AI-агентов

Краткая инструкция для **Cursor**, **Claude Code**, **Codex** и др.

## Два режима репозитория

```
errorlogy-mas/  errorlogy-gui/     →  ACTIVE (новый MVP)
ERRORLOGY/errorlogy_old_version/  →  OLD SKETCH (архив)
```

В чате: **ACTIVE:** `errorlogy-mas/…` · **OLD SKETCH:** `errorlogy_old_version/…`

## Читать первыми

1. `README.md`, `AGENTS.md` (корень)
2. [[errorlogy-mas — активный MVP (Claude)]] — backend + Analytics Engine v1
3. [[errorlogy-gui — desktop app v0.2]] — Electron UI, Globe, MAS metrics `/#/mas`, `reinstall.ps1`
4. [[Таксономия vs Engine — formalization gap]] — онтология vs math, стратегия v2
5. [[MAS — метрики оркестратора]] — `GET /api/metrics`, pipeline timing
6. [[Анализ Claude — состояние engine v1]] — audit engine, calibration gaps, priority queue
7. `errorlogy-mas/AGENTS.md` — правила MAS и языка
8. `.cursor/rules/errorlogy-mas-active.mdc` + `errorlogy-archive.mdc`
9. [[Статус репозитория — OLD SKETCH]] — только для архива

## Do

- Новый backend / агенты / API → **`errorlogy-mas/`**
- Новый UI → **`errorlogy-gui/`**; после изменений — `scripts/reinstall.ps1` (ярлык Пуск = packaged exe)
- Методология и seed-кейсы → OLD SKETCH `Politic Bar (pre errorlogy)/`
- Онтология для кода → `errorlogy-mas/data/errorlogy_unified_taxonomy_v16.json`
- Проверка E2E → `python errorlogy-mas/examples/run_challenger.py` (Challenger, engine smoke)
- Exa flow → `python errorlogy-mas/examples/run_exa_flow.py` (Horizon + source discovery)
- zvec KB demo → `python errorlogy-mas/examples/zvec_kb_demo.py`
- Таксономия в Obsidian → [[Таксономия/00 — Индекс таксономии]]
- Сессия 2026-06-24 → [[Сессия — GLM Exa zvec KB 2026-06-24]]

## Do not

- Писать MVP в `errorlogy_old_version/` без явной просьбы
- Коммитить `.env`, API keys
- Описывать AGIU / v0.6 pipeline как «текущий продукт»
- Мержить v0.6 taxonomy и v16 без задачи миграции

## Cursor tooling

- **loop-library** — глобальный skill (`~/.agents/skills/loop-library/`); см. `AGENTS.md` → Cursor agent tooling
- **/loop** — recurring in-session prompts (отдельно от loop-library)
- `.cursor/hooks/obsidian-memory.ps1` — auto MEM в `ERRORLOGY_MVP_OBSIDIAN/Memory/` (путь vault от cwd репозитория)

## Obsidian

- [[Flows/00 — Flow Index]] — гипотезы и эксперименты
- Регенерация ветки таксономии: `python ERRORLOGY_MVP_OBSIDIAN/_scripts/generate_taxonomy_branch.py`

→ [[00 — Главная]]

#agents #active #errorlogy-mas #cursor
