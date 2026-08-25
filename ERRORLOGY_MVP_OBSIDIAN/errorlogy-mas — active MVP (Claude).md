# errorlogy-mas - active MVP (Claude)

> **Status:** ACTIVE · **Build Author:** Claude (Claude Code) · **Product:** politic.bar backend

Fixed to prevent Cursor and other agents from confusing this code with **OLD SKETCH** in `errorlogy_old_version/`.

## What's done

### Backend MAS (`errorlogy-mas/`)

1. **14-agent pipeline** according to TZ (`Cursor_Project/TZ_Cursor_Errorlogy_politicalbar_FULL.md`):

```text
Scout → WMS → Classifier → Alpha → PNO → ACC → EGD → T4D → CAT → FPD → LBI
      → Red Team → Card Compiler → Neutrality Audit
```

2. **Ontology v16** - `data/errorlogy_unified_taxonomy_v16.json` (381 mode universe, alpha edges).

3. **Analytics Engine v1** (`mas/engine/`, `ENGINE_VERSION = v1-math`) - deterministic mathematics:
   - `fuzzy`, `alpha`, `wms`, `pno`, `acc`, `egd`, `t4d`, `cat`, `fpd`, `guards`
   - numpy/scipy/networkx/sklearn/sympy/ruptures
   - LLM **doesn't** count numbers - only Scout, LBI, Red Team, Card, Neutrality
   - `engine_only=True` in orchestrator and `POST /api/analyze?engine_only=true`
   - `pytest tests/` — 16 tests, Challenger smoke without LLM

4. **Multi-LLM router** - `mas/providers/`: Anthropic, OpenAI, DeepSeek, Groq, Google, Kimi, OpenRouter, **Z.ai (`ZaiProvider`)** with fallback by agent roles.

   - **GLM-5.2** for `card_compiler` and `t4d`: OpenRouter `z-ai/glm-5.2` and/or direct `ZAI_API_KEY` → `glm-5.2`
   - See [[Session – GLM Exa zvec KB 2026-06-24]]

5. **Local KB (zvec)** - `mas/kb/`: hybrid FTS + vector search; demo `examples/zvec_kb_demo.py`; env `KB_*` in `mas/config.py`.

6. **Exa source discovery** - `mas/ingest/source_discovery.py`, `enrich_sources` in orchestrator/API; E2E `examples/run_exa_flow.py` (Horizon case, not Challenger).

7. **Schemas** - `mas/schemas/analysis.py` (`CaseAnalysis`, `ModeScore`, WMS, PNO, ACC, T4D, CAT, FPD, LBI, …).

8. **FastAPI** - `api/main.py`:
   - `POST /api/analyze` (JWT), `?enrich_sources=true`
   - `GET /api/taxonomy`, `/api/taxonomy/mode/{id}`, `/api/taxonomy/edges`
   - OAuth: Google, GitHub, Telegram

9. **Challenger demo** - `examples/run_challenger.py` → `examples/challenger_output.json` (offline engine smoke).

10. **Exa demo** - `examples/run_exa_flow.py` (UK Post Office Horizon + source discovery).

11. **Language rules** - `mas/agents/base.py` + `errorlogy-mas/AGENTS.md` (μ ≠ probability, no accusations).

###UI (`errorlogy-gui/`)

→ Detail: [[errorlogy-gui - desktop app v0.2]]

- **Electron 0.2** — Dashboard, Analyze, Result, Taxonomy, **3D Globe**
- Connected to FastAPI `:8000`; `GET /api/stats/countries` for globe
- Windows: `scripts/reinstall.ps1` (uninstall + NSIS install)

### Infrastructure

- `.claude/settings.local.json` - Claude's pip/run_challenger permissions
- `.cursor/hooks.json` — obsidian-memory after agent responses

## Analytics Engine v1 (details)

| Criterion | Status |
|----------|--------|
| `pytest` green | ✅ 16 tests |
| Classifier ≥200 candidates | ✅ 217 atomic + universe pre-filter |
| weak evidence μ ≤ 0.65 | ✅ `guards.py` after fuzzy + alpha |
| Determinism WMS/PNO/ACC/CAT/FPD | ✅ engine path |
| Human-readable mode names | ✅ `taxonomy.get_mode_name()` |
| `GET /api/health` → `engine: v1-math` | ✅ |

**Out of scope v1:** body of 200 cases, SSE streaming in GUI, LBI with cvxpy, production CI.

## What hasn't been done

- GUI politic.bar (full catalog, mode graph)
- Case of 200 cases from technical specifications
- Production deploy, CI pipeline
- Merged with the old 8-agent `politic_bar/` pipeline

## Launch

> **Docker is not needed** for desktop dev - venv + local API + Electron GUI.

```bash
cd errorlogy-mas
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
# .env - keys (see mas/config.py): OPENROUTER_API_KEY, ZAI_API_KEY, EXA_API_KEY, ...
python examples/run_challenger.py
python examples/run_challenger.py --engine-only # no LLM, Challenger smoke
python examples/run_exa_flow.py # Exa + Horizon case
python examples/zvec_kb_demo.py # zvec hybrid KB
pytest tests/
python api/main.py
```

## Connections

| Resource | Role |
|--------|------|
| [[Taxonomy/00 - Taxonomy index]] | Human Readable Map v16 (Obsidian) |
| [[politic.bar - MVP sketch]] | OLD SKETCH: methodology + seed cases |
| [[Flows/00 - Flow Index]] | Hypotheses and experiments |
| [[Session – GLM Exa zvec KB 2026-06-24]] | GLM, Z.ai, zvec, Exa, smoke cases |
| `errorlogy-mas/README.md` | Technical documentation in English |

## Tags

#active #errorlogy-mas #claude #political-bar #mvp

→ [[00 — Home]] · [[Artifact map]] · [[For AI agents]]
