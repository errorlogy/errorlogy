# Errorlogy MAS + GUI — Артефакт локальной разработки

> Создан: 2026-06-12 · Статус: установлен и готов к запуску

## Компоненты

| Компонент | Путь | Назначение |
|-----------|------|------------|
| **MAS Backend** | `errorlogy-mas/` | FastAPI + 14 агентов, Python 3.12 |
| **Electron GUI** | `errorlogy-gui/` | Desktop Electron + React + Tailwind |
| **Таксономия** | `errorlogy-mas/data/errorlogy_unified_taxonomy_v16.json` | 381 режим, 89 α-рёбер |

## 14 агентов — пайплайн анализа

```
DATA (raw_text)
  ├─ 01 Scout           — извлечение структуры кейса
  ├─ 02 WMS             — слабые мультисредные сигналы (MSI, CEP)
  ├─ 03 FuzzyClassifier — fuzzy μ-скоринг режимов
  ├─ 04 AlphaPropagation — граф-распространение (89 рёбер)
  ├─ 05 PNO             — системный режим PNO-1..7
  ├─ 06 ACC             — кластеры максимального вклада
  ├─ 07 EGD             — эхо-камерная динамика
  ├─ 08 T4D             — темпоральная топология (3D+1D)
  ├─ 09 CAT             — гипотеза катастрофы
  ├─ 10 FPD             — нечёткий прогноз
  ├─ 11 LBI             — альтернативы улучшения
  ├─ 12 RedTeam         — adversarial review
  ├─ 13 CardCompiler    — публичная карточка
  └─ 14 NeutralityAudit — аудит языка (anti-overclaim)
```

## LLM-роутер — 7 провайдеров

OpenAI → DeepSeek → Groq → Google Gemini → Kimi → OpenRouter → Anthropic Claude

Ключи: `errorlogy-mas/.env` (не коммитить).

## GUI — экраны

| Экран | Роут | Описание |
|-------|------|----------|
| Dashboard | `/` | Статус системы, провайдеры, пайплайн |
| Analyze | `/analyze` | Форма ввода кейса + прогресс агентов |
| Result | `/result` | μ-гистограмма, PNO, T4D, ACC, CAT, FPD, LBI, Public Card |
| Taxonomy | `/taxonomy` | Поиск/фильтр режимов, α-связи |

Стек: Electron + React + Vite + Tailwind + Recharts
