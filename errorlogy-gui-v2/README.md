# errorlogy-gui-v2

Упрощённый браузерный UI для **прогнозирования** Errorlogy MAS — фокус на потоковом и кейсовом прогнозе, потоках данных и прозрачной методологии.

Полный desktop UI остаётся в [`errorlogy-gui/`](../errorlogy-gui/) (v0.2.x, Electron).

## Запуск рядом с v1

**Терминал 1 — API** (общий для обоих UI):

```bash
cd errorlogy-mas
python api/main.py
```

**Терминал 2 — v2** (порт **5174**):

```bash
cd errorlogy-gui-v2
npm install
npm run dev
```

Откройте http://localhost:5174

**Терминал 3 (опционально) — v1** (порт 5173):

```bash
cd errorlogy-gui
npm run dev:vite
```

Vite проксирует `/api` → `http://127.0.0.1:8000`.

## Страницы

| Путь | Назначение |
|------|------------|
| `/` | Обзор: health, кейсовый vs потоковый прогноз, методология |
| `/stream` | Прогноз потока — `GET /api/forecast/stream` |
| `/case` | Прогноз по кейсу — `POST /api/analyze` (SSE или sync) |
| `/data` | Потоки данных — ingest, RSS, ручной ввод |

## Сборка

```bash
npm run build
```

## Отличия от v1

- 4 страницы вместо 10+ (нет глобуса, полной таксономии, MAS-метрик, Electron)
- Горизонтальная навигация, русский UI по умолчанию
- Акцент на μ ≠ probability и пояснения methodology_ru из API
- Браузер-only (без OAuth, без упаковки)

## Переменные

- `VITE_API_BASE` — если API не на localhost:8000 (production)
