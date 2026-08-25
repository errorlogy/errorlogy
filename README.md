# Errorlogy

**https://errorlogy.com** — analytical platform for governance error patterns (non-accusatory framing).

> *Errors in governance as observable objects: the gap between what was declared, what was known, and what was decided.*

**Errorlogy** models governance errors as observable objects (gap: declared / known / decided).  
**politic.bar** is the first product: an analytical catalog of public error cards without accusatory language.

## Analysis layers

```text
DATA → WMS → CB/SF/MP/GT/HM/... → α → ACC → PNO → FPD
```

More detail: [`docs/concept/`](docs/concept/) · Obsidian: [`ERRORLOGY_MVP_OBSIDIAN/`](ERRORLOGY_MVP_OBSIDIAN/)

---

## Components

| Component | Path | Role |
|-----------|------|------|
| **errorlogy-mas** | `errorlogy-mas/` | FastAPI backend — 14-agent pipeline, taxonomy v16 |
| **errorlogy-gui** | `errorlogy-gui/` | Electron + Vite + React desktop UI (v0.2.x) |
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

## Repository layout

The workspace combines **active development** (new MVP) and an **archive of sketches** (early iterations).

| Path | Status | Purpose |
|------|--------|---------|
| `errorlogy-mas/` | **ACTIVE** | Multi-agent politic.bar backend: 14-agent pipeline, taxonomy v16, FastAPI, multi-LLM router *(built by Claude)* |
| `errorlogy-gui/` | **ACTIVE** | Electron + Vite + React desktop UI v0.2.4 (~90% API integration) |
| `errorlogy-gui-v2/` | **ACTIVE** | Browser UI v0.1 — forecast, streams, methodology (port 5174) |
| `ERRORLOGY/errorlogy_old_version/` | **OLD / SKETCH** | Early artifacts: politic.bar v0.6, AGIU, spec, taxonomy copies |
| `ERRORLOGY_MVP_OBSIDIAN/` | **Documentation** | Obsidian: concept, taxonomy, map, work journal |

More on what Claude built: [Obsidian — errorlogy-mas active MVP](ERRORLOGY_MVP_OBSIDIAN/errorlogy-mas%20%E2%80%94%20active%20MVP%20(Claude).md).

## Active MVP: errorlogy-mas

```bash
cd errorlogy-mas
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
# .env — LLM keys (see mas/config.py)
python examples/run_challenger.py
```

API: `python api/main.py` → http://127.0.0.1:8000/docs

## GUI: errorlogy-gui

**Terminal 1 — API:** `cd errorlogy-mas && python api/main.py`  
**Terminal 2 — UI:** `cd errorlogy-gui && npm install && npm run dev:vite` (Vite proxies `/api` → `:8000`)

Without LLM keys: **Engine only** on the Analyze page. See [`errorlogy-gui/README.md`](errorlogy-gui/README.md).

**Simplified forecast UI:** [`errorlogy-gui-v2/README.md`](errorlogy-gui-v2/README.md) — `npm run dev` on port 5174.

Pipeline:

```text
Scout → WMS → Classifier → Alpha → PNO → ACC → EGD → T4D → CAT → FPD → LBI
      → Red Team → Card Compiler → Neutrality Audit
```

Source of truth for code: `errorlogy-mas/AGENTS.md`, ontology: `errorlogy-mas/data/errorlogy_unified_taxonomy_v16.json`.

## OLD SKETCH (do not extend without explicit request)

| Path | Contents |
|------|----------|
| `…/Windows_old_MVP/Politic Bar (pre errorlogy)/` | Methodology v0.6, seed cases, 8-agent pipeline |
| `…/AGIU/` | Hono health + demo FastAPI analytics |
| `…/Cursor_Project/` | Full web-MVP specification |

## Documentation

- Obsidian: [`ERRORLOGY_MVP_OBSIDIAN/`](ERRORLOGY_MVP_OBSIDIAN/) — [home](ERRORLOGY_MVP_OBSIDIAN/00%20%E2%80%94%20Home.md)
- Cursor: [`AGENTS.md`](AGENTS.md), [`.cursor/rules/`](.cursor/rules/)
- **OSS evaluation funnel:** [`docs/oss-integration-funnel.md`](docs/oss-integration-funnel.md) — open-source candidate evaluation funnel; tracker [`research/oss-candidates.yaml`](research/oss-candidates.yaml); checklist `python research/score_candidate.py`
- **Harness engineering:** [`docs/reference/harness-engineering/README.md`](docs/reference/harness-engineering/README.md) — eval/agent harness, principles and checklist for MAS

## Idea

**Errorlogy** — governance errors as observable objects (gap: declared / known / decided).  
**politic.bar** — first product: analytical catalog without accusatory language.
