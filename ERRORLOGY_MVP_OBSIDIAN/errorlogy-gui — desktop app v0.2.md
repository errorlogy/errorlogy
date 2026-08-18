# errorlogy-gui — desktop app v0.2

> **Статус:** ACTIVE · **Версия:** 0.2.1 · **Продукт:** politic.bar desktop UI  
> **Backend:** [[errorlogy-mas — активный MVP (Claude)]] (FastAPI `:8000`)

Desktop-приложение Errorlogy MAS: анализ governance-кейсов, визуализация результатов, 3D-глобус со статистикой по странам.

## Что это

| Параметр | Значение |
|----------|----------|
| Путь в репо | `errorlogy-gui/` |
| Стек | Electron 42 + Vite 8 + React 19 + Tailwind 4 |
| 3D | `react-globe.gl` + Three.js |
| Графики | Recharts (Result page) |
| Установка (Windows) | NSIS → `%LOCALAPPDATA%\Programs\errorlogy-gui\` |
| Ярлык Пуск | `Errorlogy.lnk` → `Errorlogy.exe` |

## Страницы (HashRouter)

| Маршрут | Экран | Назначение |
|---------|-------|------------|
| `/` | Dashboard | health, engine v1-math, LLM providers, пайплайн 14 агентов |
| `/globe` | Globe | **3D Земной шар** — choropleth + extrusion по странам |
| `/analyze` | Analyze | ввод кейса, full MAS или `engine_only` |
| `/result` | Result | KPI, charts, worldline, public card |
| `/taxonomy` | Taxonomy | browse режимов v16 + alpha edges |

## Связь с backend

Electron при старте поднимает uvicorn из `errorlogy-mas/` (`api.main:app`, порт 8000).

| API | Использование в GUI |
|-----|---------------------|
| `GET /api/health` | Dashboard (status, engine, providers, taxonomy) |
| `POST /api/analyze?engine_only=true` | Analyze (опционально без LLM) |
| `GET /api/stats/countries` | Globe — seed-статистика по 15 странам |
| `GET /api/taxonomy/modes` | Taxonomy |
| `GET /api/taxonomy/edges` | Taxonomy (вкладка Graph — список) |

Клиент: `errorlogy-gui/src/lib/api.ts` → `http://127.0.0.1:8000`

## Analytics Engine v1 в UI

- Dashboard: бейдж **Engine v1-math**, легенда **engine** (красный) vs **LLM** (янтарный) в пайплайне
- Analyze: чекбокс **Engine only** — детерминированная аналитика без Scout/Card/Red Team
- Result: метка `engine_only` / `metadata.engine` из ответа MAS
- Числа μ, MSI, PNO, ACC, CAT, FPD считает `mas/engine/`, не LLM

## 3D Globe — наполнение статистикой

**Источники данных (мерж на клиенте):**

1. **Seed** — `errorlogy-mas/data/country_stats_seed.json` → `GET /api/stats/countries`  
   USA (Challenger), JPN (Fukushima), RUS (Kursk), GBR (Hillsborough) и др. (15 стран)
2. **Локальные анализы** — `localStorage` (`errorlogy_case_history`) после Run Analyze с полем **Country**

**Визуализация:**

- цвет полигона — плотность кейсов (красный choropleth)
- высота extrusion — число кейсов
- клик → панель: cases, avg μ, CEP, echo pressure, PNO, families, recent cases
- hover → HTML tooltip

- GeoJSON **встроен** в пакет: `public/geo/countries-110m.geojson`
- Текстуры Earth — `https://cdn.jsdelivr.net/...` (нужен интернет)

**v0.2.1 fix:** в Electron `file://` ломались URL `//cdn...` — глобус был пустым. Исправлено на `https://` + локальный GeoJSON.

Код: `src/components/ErrorlogyGlobe.tsx`, `src/pages/GlobePage.tsx`, `src/lib/countryStats.ts`

## Установка и обновление (важно)

Ярлык **Пуск** запускает **упакованный** `.exe`, а не исходники из репо.

После изменений в GUI нужен **rebuild + reinstall**:

```powershell
cd C:\Users\Public\ERRORLOGY_MVP\errorlogy-gui
powershell -ExecutionPolicy Bypass -File scripts\reinstall.ps1
```

Скрипт:
1. закрывает `Errorlogy.exe`
2. `Uninstall Errorlogy.exe /S` (старая копия в Programs)
3. ставит `dist-electron\Errorlogy Setup 0.2.0.exe /S`

**Путь установки:** `C:\Users\<user>\AppData\Local\Programs\errorlogy-gui\Errorlogy.exe`

`npm run dev` — для разработки (Vite `:5173` + Electron, живой hot reload).

## Разработка

```bash
cd errorlogy-gui
npm install
npm run dev              # dev mode
npm run build            # только frontend dist/
npm run electron:build   # NSIS installer в dist-electron/
```

## Что не сделано

- SSE / реальный прогресс агентов с backend (сейчас таймер в Analyze)
- Полный каталог кейсов politic.bar
- Offline-кэш GeoJSON / текстур глобуса
- Auth UI (OAuth есть в API, GUI не использует JWT)
- CI для electron:build

## Связи

| Ресурс | Роль |
|--------|------|
| [[errorlogy-mas — активный MVP (Claude)]] | backend, engine, API |
| [[Карта артефактов]] | структура репо |
| `errorlogy-gui/README.md` | техдок на английском |
| `errorlogy-gui/scripts/reinstall.ps1` | чистая переустановка Windows |

## Теги

#active #errorlogy-gui #electron #globe #politic-bar #mvp #v0.2

→ [[00 — Главная]] · [[Карта артефактов]] · [[errorlogy-mas — активный MVP (Claude)]]
