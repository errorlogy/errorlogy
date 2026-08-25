# Session – GLM, Exa, zvec KB (2026-06-24)

> **Context:** integration of LLM providers, local KB, Exa source discovery and clarification of smoke cases for ACTIVE MVP (`errorlogy-mas/`).  
> **Connections:** [[errorlogy-mas - active MVP (Claude)]], [[Ingest - info stream layer]], [[Roadmap - implementation log]], `AGENTS.md`

---

## Executive summary

1. **GLM-5.2** is assigned to long narratives: `card_compiler` and `t4d` - via OpenRouter (`z-ai/glm-5.2`) and/or direct **Z.ai API** (`ZaiProvider`, `ZAI_API_KEY`).
2. **Local KB on zvec** - hybrid FTS + vector (RRF), module `mas/kb/`; context for the T4D engine via `case.metadata.kb_context`.
3. **Exa** - full loop: ingest, `source_discovery`, API `enrich_sources`, CLI `run_exa_flow.py`; `EXA_API_KEY` is configured (the value should not be stored in vault).
4. **Docker not needed** for desktop MVP: venv + `python api/main.py` + `npm run dev` in `errorlogy-gui/`.
5. **loop-library** — global Cursor skill + section in the root `AGENTS.md`.
6. **Challenger vs Horizon (case)** — Challenger for offline engine smoke; UK Post Office Horizon - for Exa-enriched flow (not to be confused with Roadmap Horizon H1–H3).

---

## GLM-5.2 - card_compiler and T4D

Two ways to one model:

| Path | Provider | Env | Model |
|------|-----------|-----|--------|
| OpenRouter | `OpenRouterProvider` | `OPENROUTER_API_KEY` | `z-ai/glm-5.2` |
| Direct Z.ai | `ZaiProvider` | `ZAI_API_KEY` | `glm-5.2` |

**Router** (`errorlogy-mas/mas/providers/router.py`):

- `AGENT_PREFERENCES`: for `card_compiler` and `t4d` in the chain after `openai` there is `zai`, then `kimi`, `deepseek`, `openrouter`.
- `OPENROUTER_MODEL_MAP`: explicitly `z-ai/glm-5.2` for `card_compiler` and `t4d` (long structured cards and worldline narrative).
- `ZAI_MODEL_MAP`: `glm-5.2` for the same roles.

**Why GLM on these agents:** Card Compiler generates an 8-section public card; T4D (LLM wrapper) adds text to the engine worldline. Both require long, coherent output while respecting `LANGUAGE_RULES` (`errorlogy-mas/AGENTS.md`).

**Registration:** `mas/providers/__init__.py` → `build_router()` registers `ZaiProvider` if `ZAI_API_KEY` is present. Base URL: `https://api.z.ai/api/paas/v4`.

```bash
# .env (   —  )
OPENROUTER_API_KEY=...
ZAI_API_KEY=...
```

---

## zvec - local knowledge base

| Component | Path |
|-----------|------|
| Store (hybrid query) | `errorlogy-mas/mas/kb/zvec_store.py` |
| Pipeline retrieval | `errorlogy-mas/mas/kb/retrieval.py` |
| Demo | `errorlogy-mas/examples/zvec_kb_demo.py` |
| Default data | `errorlogy-mas/.data/zvec_kb/` |

**Search mode:** `KB_QUERY_MODE=hybrid` (default) - FTS + HNSW vector, merge via `WeightedReRanker` (RRF-style).

**Config** (`mas/config.py`):

| Variable | Default | Meaning |
|------------|---------|-------|
| `KB_ENABLED` | `true` | Enable KB (graceful off without `zvec`) |
| `KB_ZVEC_PATH` | `.data/zvec_kb` | Collection path |
| `KB_TOPK` | `5` | Number of snippets |
| `KB_QUERY_MODE` | `hybrid` | `vector` / `fts` / `hybrid` |
| `KB_INGEST_ON_SCOUT` | `false` | Index after Scout |
| `KB_INGEST_ON_COMPLETE` | `false` | Index after full run |
| `KB_EMBEDDINGS` | `hash` | `sentence-transformers`, `fastembed` |

**Pipeline flow:**

1. `build_case_query()` assembles a query from title, description, weak signals, top modes.
2. `attach_kb_context()` → hybrid search → `case.metadata["kb_context"]`.
3. **Engine T4D** (`mas/engine/t4d.py`, `_case_text`) supplements `source_text` with KB context when building the worldline.

> **Status wiring:** infrastructure and T4D consumption are ready; calling `attach_kb_context` in `orchestrator` before the T4D/Card Compiler steps is the next integration step (the context for the LLM Card is not in the prompt yet).

**Smoke without keys:**

```bash
cd errorlogy-mas
python examples/zvec_kb_demo.py
```

---

## Exa - full integration

| Layer | Entry | Role of Exa |
|-----------|-------|----------|
| Fetcher | `mas/ingest/fetchers/exa.py` | `/search` or Agent API |
| Source discovery | `mas/ingest/source_discovery.py` | `discover_sources`, `enrich_source_bundle` |
| Orchestrator | `enrich_sources=True` in `run_from_text` | Add. sources → `raw_text` to Scout |
| API analyze | `POST /api/analyze?enrich_sources=true` | Same via REST |
| API ingest | `POST /api/ingest/fetch-exa`, `fetch-web`, `fetch-all` | Search + ingest |
| API discovery | `POST /api/ingest/discover-sources`, `/enrich-bundle` | Hits/merged bundle |
| CLI | `scripts/fetch_gov_media.py --exa-only` | Cron-friendly ingest |
| E2E demo | `examples/run_exa_flow.py` | Exa → bundle → engine-only MAS |
| Smoke | `scripts/exa_smoke.py` | Checking the config (the key is not printed) |

**Env** (names only):

| Variable | Default | Meaning |
|------------|---------|-------|
| `EXA_API_KEY` | — | Enables Exa (graceful disable) |
| `EXA_SEARCH_TYPE` | `auto` | Mode `/search` |
| `EXA_PREFERRED` | `false` | Exa priority in `fetch-web` |
| `EXA_AGENT_MODE` | `false` | Agent API instead of search |
| `EXA_AGENT_EFFORT` | `minimal` | Agent Effort |

**Web search priority** (without Exa): OpenRouter → Gemini → Exa. See [[Ingest - info stream layer]].

```bash
python scripts/exa_smoke.py
python examples/run_exa_flow.py
python examples/run_exa_flow.py --no-enrich    # seed only
python examples/run_exa_flow.py --ingest       # + persist raw_documents
```

Tests: `tests/test_source_discovery.py`, `tests/test_ingest_fetchers.py` (mock Exa).

---

## Docker - not required for desktop MVP

For local development it is enough:

```bash
#Backend
cd errorlogy-mas
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# .env with keys
python api/main.py

#GUI
cd errorlogy-gui
npm install
npm run dev:vite # or npm run dev for Electron
```

Containers in the repository are not described and are not needed for smoke/E2E on Windows. SQLite + local zvec path - file-based.

---

## loop-library (Cursor)

Global skill: `~/.agents/skills/loop-library/`  
Installation: `npx skills add Forward-Future/loop-library --skill loop-library -g`

Documented in root `AGENTS.md` → **Cursor agent tooling** section:

- **loop-library** —  bounded repeatable workflows (, , , stop).
- **/loop** —  session cadence (  loop-library).

Example loops for Errorlogy: pre-merge `pytest`, `run_challenger.py --engine-only`, health `GET /api/health`.

---

## Challenger vs Horizon —  smoke-

| | **Challenger (STS-51L, 1986)** | **Horizon (UK Post Office, 1999+)** |
|---|-------------------------------|-------------------------------------|
|  | `examples/run_challenger.py` | `examples/run_exa_flow.py` |
| Purpose |  engine smoke, pytest golden, GUI demo JSON | Exa source discovery + enriched bundle |
|  | `--engine-only`  API | `EXA_API_KEY`  enrich |
|  corpus | `scripts/seed_corpus.py` (USA) | `GB-POL-1999-HORIZON-01` |

**Why is Challenger in smoke by default:**

-  , public domain,   weak signals   engine.
-       API —  CI (`pytest`, `--engine-only`).
- Golden snapshot  dual-run benchmarks   Challenger.

**Horizon** —  governance-   Exa ingest/discovery  UK media/gov ;  `run_exa_flow.py`  : *«not Challenger»*.

> **Do not be confused:** Roadmap **Horizon 1/2/3** ([[Roadmap - MAS math development TZ]]) - development horizons (engineering / Weak Signal / Homo-MAS), not the Post Office case.

---

##   smoke

```bash
# Engine-only, no keys
python errorlogy-mas/examples/run_challenger.py --engine-only
pytest errorlogy-mas/tests/ -q -m "not llm_eval"

# Exa + engine (Horizon)
python errorlogy-mas/examples/run_exa_flow.py

# zvec KB demo
python errorlogy-mas/examples/zvec_kb_demo.py
```

---

## 

#active #errorlogy-mas #session #glm #exa #zvec #ingest #cursor

→ [[00 — Home]] · [[For AI agents]] · [[Roadmap — implementation log]]
