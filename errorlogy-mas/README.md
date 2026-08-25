# Errorlogy MAS

> **STATUS: ACTIVE** — primary backend for politic.bar MVP (built by Claude).  
> Archive sketches: `../ERRORLOGY/errorlogy_old_version/` (OLD SKETCH).

Multi-agent AI system for analytical monitoring of government management errors.

> "A title is not competence. Authority is not ability. Errorlogy measures the gap."

## Analytics Engine v1

Deterministic numerics live in `mas/engine/` (numpy, scipy, networkx, sklearn, sympy, ruptures).
LLM agents handle extraction, narrative, adversarial review, and the public card only.

| Layer | Module | LLM role |
|-------|--------|----------|
| WMS, Classifier, Alpha, PNO, ACC, EGD, T4D, CAT, FPD | `mas/engine/*` | optional explanation text |
| Scout, LBI, Red Team, Card Compiler, Neutrality | `mas/agents/*` | full |

```bash
# Deterministic path — no API keys required
python -c "from mas.orchestrator import Orchestrator; ..."
# or POST /api/analyze?engine_only=true

pytest tests/   # TZ §13 unit + Challenger smoke (no LLM)
```

**Windows note:** `scikit-fuzzy` may require MSVC build tools; FPD falls back to numpy sigmoid if import fails.

Optional heavy deps: `pip install -r requirements-math-optional.txt` (statsmodels, cvxpy, …).

## What it does

Runs a 14-agent pipeline on a governance event description and produces:
- Fuzzy mode scores (μ) across 381 error modes from the Errorlogy taxonomy v16
- Alpha-propagated activation through the error graph
- PNO system regime classification
- ACC contribution cluster detection
- T4D temporal worldline reconstruction
- CAT catastrophe hypothesis
- FPD fuzzy forecast
- LBI betterment alternatives
- Public non-accusatory explanation card

## Pipeline

```
DATA (source text)
 └─ Scout             extract case structure + weak signals
 └─ WMS               Multisource Signal Index + CEP
 └─ Classifier        fuzzy μ scoring (217 atomic + universe)   ← engine
 └─ Alpha             α-propagation through taxonomy graph     ← engine
 └─ PNO               system regime (PNO-1..7)                 ← engine
 └─ ACC               contribution clusters (ACC-001..010)     ← engine
 └─ EGD               echo-room / small-group dynamics         ← engine
 └─ T4D               3D+1D temporal worldline                 ← engine
 └─ CAT               catastrophe theory hypothesis            ← engine
 └─ FPD               fuzzy trajectory forecast                ← engine
 └─ LBI               betterment alternatives
 └─ Red Team          adversarial review
 └─ Card Compiler     public explanation card
 └─ Neutrality Audit  language compliance check
```

## Setup

```bash
cd errorlogy-mas
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create `.env` file:
```
ANTHROPIC_API_KEY=sk-ant-...
# Optional ingest / source discovery:
EXA_API_KEY=exa-...
# EXA_PREFERRED=true
# EXA_AGENT_MODE=true
```

## Run demo (Challenger 1986)

Challenger is the **default offline smoke case** — well-documented, public domain, used in
`run_challenger.py`, pytest, and GUI demo JSON. It is not tied to Exa.

```bash
python examples/run_challenger.py              # full pipeline (needs LLM keys)
python examples/run_challenger.py --engine-only  # deterministic smoke, no keys
pytest tests/
```

Output saved to `examples/challenger_output.json`.

## Exa integration (ingest + source discovery)

Exa powers **ingest web search** and **pre-pipeline source bundle enrichment** (before Scout).
Scout itself does not call Exa — it receives enriched `raw_text` from the ingest layer.

| Layer | Entry | Exa role |
|-------|-------|----------|
| Cron / CLI | `scripts/fetch_gov_media.py --exa-only` | Search + ingest |
| API ingest | `POST /api/ingest/fetch-exa`, `fetch-web`, `fetch-all` | Search + ingest |
| Source discovery | `POST /api/ingest/discover-sources`, `enrich-bundle` | Hits only / merged bundle |
| Analyze | `POST /api/analyze?enrich_sources=true` | Append excerpts → Scout |
| GUI | Info Stream page | Fetch Exa / Web / All buttons |

Config (`.env`):

| Variable | Default | Meaning |
|----------|---------|---------|
| `EXA_API_KEY` | — | Enables Exa fetcher (graceful disable if unset) |
| `EXA_SEARCH_TYPE` | `auto` | Exa `/search` mode |
| `EXA_PREFERRED` | `false` | Prefer Exa over OpenRouter/Gemini in `fetch-web` |
| `EXA_AGENT_MODE` | `false` | Use Exa Agent API (usage-based) instead of `/search` |
| `EXA_AGENT_EFFORT` | `minimal` | Agent effort when agent mode is on |

```bash
# Config smoke (no key printed)
python scripts/exa_smoke.py

# Exa → enrich bundle → engine-only MAS (Horizon case, not Challenger)
python examples/run_exa_flow.py

# Ingest-only via Exa
python scripts/fetch_gov_media.py --exa-only -q "UK Post Office Horizon inquiry" --num-results 2
```

## Local KB demo (Zvec)

Optional embedded vector DB for KB experiments (`zvec>=0.5.0` in `requirements.txt`).

```bash
python examples/zvec_kb_demo.py
```

The demo inserts sample governance snippets, creates an FTS index on `text`, builds an HNSW
vector index, then runs vector-only, FTS-only, and hybrid queries (RRF-style merge via
`WeightedReRanker`). Hybrid results include separate FTS/vector scores when available.

Embedder selection (optional):

| Env | Values | Notes |
|-----|--------|-------|
| `KB_EMBEDDINGS` | `hash` (default), `sentence-transformers`, `fastembed` | Falls back to hash if optional dep missing |
| `KB_EMBEDDING_MODEL` | model id | e.g. `paraphrase-multilingual-MiniLM-L12-v2` |
| `KB_EMBEDDING_DIM` | int | hash embedder only (default `128`) |

Windows: `zvec` wheels are available; first run of `sentence-transformers` downloads model weights.

## Usage in code

```python
from mas.orchestrator import Orchestrator

orchestrator = Orchestrator()
analysis = orchestrator.run_from_text(
    case_id="MY-CASE-001",
    raw_text="...",
    title="Event title",
    country="USA",
    year=2023,
)
print(analysis.pno.dominant_pno)
print(analysis.public_explanation)

# Engine-only (deterministic, no LLM)
analysis = orchestrator.run_from_text(
    case_id="MY-CASE-001",
    raw_text="...",
    engine_only=True,
)
```

## API

- `GET /api/health` — includes `"engine": "v1-math"` and Exa config flags
- `POST /api/analyze?engine_only=true` — skip Scout/Card/LLM narrative
- `POST /api/analyze?enrich_sources=true` — Exa/web discovery before pipeline
- `POST /api/ingest/fetch-exa` — Exa search + ingest + auto-analyze
- `GET /api/ingest/status` — fetcher ON/OFF including `exa_preferred`, `exa_agent_mode`

### Cross-layer institutional events (AI Native Gov)

Runtime bridge to [ai-native-gov](https://github.com/errorlogy/ai-native-gov) contracts.
Framing stub only — fills `activated_layers` from `event_type`, sets `epistemic_label`:
`INSTITUTIONAL_MODEL`. Does **not** run analyze / μ pipeline.

| Method | Path | Notes |
|--------|------|-------|
| `POST` | `/api/events/cross-layer` | Body: umbrella `cross-layer-event.json` subset |
| `GET` | `/api/events/cross-layer` | List persisted events |
| `GET` | `/api/events/cross-layer/layers` | Valid institution layer IDs |
| `GET` | `/api/events/cross-layer/{event_id}` | Single event |

Vendored schemas: `schemas/cross-layer-event.json`, `schemas/institution-layer-id.json`.
Source of truth: umbrella `schemas/`. Tests: `tests/test_cross_layer.py`.

## Project structure

```
errorlogy-mas/
├── data/
│   └── errorlogy_unified_taxonomy_v16.json   ← ontology (381 modes)
├── mas/
│   ├── config.py
│   ├── taxonomy.py
│   ├── orchestrator.py
│   ├── engine/                ← deterministic analytics (v1-math)
│   │   ├── fuzzy.py, alpha.py, wms.py, pno.py, acc.py
│   │   ├── egd.py, t4d.py, cat.py, fpd.py, guards.py
│   │   └── types.py
│   ├── agents/
│   │   ├── base.py            ← BaseAgent + language rules
│   │   ├── scout.py
│   │   ├── wms.py
│   │   ├── classifier.py
│   │   ├── alpha.py           ← thin wrapper → engine
│   │   ├── pno.py
│   │   ├── acc.py
│   │   ├── egd.py
│   │   ├── t4d.py
│   │   ├── cat.py
│   │   ├── fpd.py
│   │   ├── lbi.py
│   │   ├── red_team.py
│   │   ├── neutrality.py
│   │   └── card_compiler.py
│   └── schemas/
│       ├── case.py
│       └── analysis.py
├── tests/                     ← pytest TZ §13
├── examples/
│   └── run_challenger.py
├── AGENTS.md
├── README.md
├── requirements.txt
└── requirements-math-optional.txt
```

## Language rules

All agents enforce:
- μ = fuzzy membership, not probability
- No legal accusations, no intent assertions without evidence
- Always cite `evidence_grade` alongside any score
- Use: "analytical contribution", "consistent with", "early-warning hypothesis"

See `AGENTS.md` for full rules.

## Ontology

Taxonomy v16 — 381 modes across 24 layers:
`CB` (189) · `SF` (14) · `MP` (14) · `GT` · `HM` · `LCJ` · `LBI` · `LAC` · `LCC`
`WMS` · `ACC` · `EGD` · `FPD` · `T4D` · `CAT` · `PNO` · `METHODS` · `LΩ` · ...

Alpha graph: 72 directed seed edges with weights ∈ [-1, 1].
