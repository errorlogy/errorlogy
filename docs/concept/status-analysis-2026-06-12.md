# Анализ статуса ERRORLOGY_MVP — срез 2026-06-12

> Источник: анализ Cursor IDE по живому дереву проекта

---

## 1. Зрелость: где мы на карте

| Зона | Статус | Зрелость |
|------|--------|----------|
| `errorlogy-mas/` | ACTIVE | ~MVP backend: пайплайн собран, есть дemo Challenger, API |
| `errorlogy-gui/` | ACTIVE | ~alpha UI: Electron + React, подключён к API, без каталога/истории |
| `ERRORLOGY/errorlogy_old_version/` | OLD SKETCH | Референс методологии v0.6, seed-кейсы, ТЗ |
| `ERRORLOGY_MVP_OBSIDIAN/` | Документация | Хорошая навигация; GUI описан устаревше |
| Тесты / CI / deploy | — | Отсутствуют в active-части |

**Итог:** это исследовательский MVP с одним end-to-end сценарием (текст → 14 шагов → JSON + карточка), а не публичный politic.bar.

---

## 2. Архитектура (как сейчас)

```
errorlogy-gui Electron
  └─ fetch → errorlogy-mas FastAPI :8000
               ├─ /api/health
               ├─ /api/analyze → pipeline:
               │     Scout → WMS → Classifier → Alpha (algo)
               │     → PNO → ACC → EGD → T4D → CAT
               │     → FPD → LBI → Red Team → Card Compiler → Neutrality
               └─ /api/taxonomy/*
                     └─ errorlogy_unified_taxonomy_v16.json

LLM Router (fallback): Anthropic → OpenAI → DeepSeek → Groq → Google → Kimi → OpenRouter
Единственный не-LLM шаг: AlphaPropagationAgent — чистая математика по рёбрам графа
```

---

## Приоритеты для следующего шага

1. **Persistence** — SQLite или JSON-файлы для истории кейсов
2. **Classifier coverage** — GT, HM, EGD и др. в промпте
3. **Реальный streaming прогресса** — SSE или WebSocket
4. **Corpus seed-кейсов** — импорт 5 кейсов из OLD SKETCH
5. **JWT в GUI** — OAuth login flow в Electron

Полная версия: см. исходник в Obsidian или `ERRORLOGY_MVP_OBSIDIAN/`.
