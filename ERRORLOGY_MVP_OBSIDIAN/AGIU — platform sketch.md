# AGIU - platform sketch

> **OLD SKETCH** - `ERRORLOGY/errorlogy_old_version/AGIU/`

## Idea

Monorepo preparation for the future Errorlogy platform:

| Part | Stack | Actual condition |
|-------|------|------------------------|
| Platform API | Node 20+, Hono, Drizzle, pg, BullMQ, Redis, OpenAI | Only `GET /health` |
| Analytics | Python FastAPI, numpy, sklearn | Taxonomy API + demo FPD/ACC |

## Analytics API (port 8000)

- `GET /api/v1/taxonomy/meta`, `/layers`, `/layer/{name}`
- `POST /api/v1/math/fuzzy/trajectory`
- `POST /api/v1/math/cluster/kmeans`

Ontology: `errorlogy_unified_taxonomy_v16_max_catastrophe_2.json`

## Launch

```bash
cd AGIU
npm install
# Python: .venv + pip install -r requirements.txt
npm run analytics:dev
```

## Node dependencies (for the future)

`package.json` already contains drizzle, bullmq, openai, pg - the infrastructure is **not connected** in `server.ts`.

→ [[Artifact map]] · [[Errorlogy - concept]]

#agiu #old-sketch