# AGIU — скетч платформы

> **OLD SKETCH** — `ERRORLOGY/errorlogy_old_version/AGIU/`

## Задумка

Monorepo-заготовка под будущую платформу Errorlogy:

| Часть | Стек | Фактическое состояние |
|-------|------|------------------------|
| Platform API | Node 20+, Hono, Drizzle, pg, BullMQ, Redis, OpenAI | Только `GET /health` |
| Analytics | Python FastAPI, numpy, sklearn | Taxonomy API + demo FPD/ACC |

## Analytics API (порт 8000)

- `GET /api/v1/taxonomy/meta`, `/layers`, `/layer/{name}`
- `POST /api/v1/math/fuzzy/trajectory`
- `POST /api/v1/math/cluster/kmeans`

Онтология: `errorlogy_unified_taxonomy_v16_max_catastrophe_2.json`

## Запуск

```bash
cd AGIU
npm install
# Python: .venv + pip install -r requirements.txt
npm run analytics:dev
```

## Зависимости Node (на будущее)

В `package.json` уже указаны drizzle, bullmq, openai, pg — инфраструктура **не подключена** в `server.ts`.

→ [[Карта артефактов]] · [[Errorlogy — концепция]]

#agiu #old-sketch
