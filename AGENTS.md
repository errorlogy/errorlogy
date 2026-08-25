# Guidance for AI agents

## Active vs archive

| Label | Path | Meaning |
|-------|------|---------|
| **ACTIVE** | `errorlogy-mas/`, `errorlogy-gui/` | Current MVP development |
| **RESEARCH** | `errorlogy-trn-sim/` | TRN synthetic simulation — not in 14-agent pipeline |
| **OLD SKETCH** | `ERRORLOGY/errorlogy_old_version/` | Historical sketches — reference only |

Human-readable docs: `ERRORLOGY_MVP_OBSIDIAN/` (see `errorlogy-mas — active MVP (Claude).md`).

## Active: errorlogy-mas

**Primary codebase.** Built by Claude (session ~2026): 14-agent pipeline, taxonomy v16, FastAPI, multi-LLM router.

- Read `errorlogy-mas/AGENTS.md` before editing MAS code
- Ontology: `errorlogy-mas/data/errorlogy_unified_taxonomy_v16.json`
- Output types: `errorlogy-mas/mas/schemas/analysis.py`
- E2E check: `python errorlogy-mas/examples/run_challenger.py`
- Do **not** commit `.env` or API keys

### errorlogy-gui

Electron + Vite + React desktop UI (v0.2.4) — ~90% wired to MAS FastAPI (`src/lib/api.ts`). New UI work goes here unless user says otherwise.

Run: start `errorlogy-mas` API (`python api/main.py`), then `cd errorlogy-gui && npm run dev:vite` (or `npm run dev` for Electron). See `errorlogy-gui/README.md`.

## Research: errorlogy-trn-sim

Synthetic TRN agent simulation for polarization / anticonsensus experiments. Separate from MAS agents; optional future bridge via `errorlogy-trn-sim/bridge/egd_stub.py`.

- Read `errorlogy-trn-sim/docs/SAFETY_AND_SCOPE.md` before edits
- Run: `python errorlogy-trn-sim/run_experiments.py --config errorlogy-trn-sim/configs/default_config.json --out errorlogy-trn-sim/outputs`
- Validate CSV: `python errorlogy-trn-sim/scripts/validate_outputs.py errorlogy-trn-sim/outputs --recursive`
- Do **not** merge into `errorlogy-mas/mas/agents/` without an explicit migration task

## OLD SKETCH: errorlogy_old_version

Everything under `ERRORLOGY/errorlogy_old_version/` is historical unless the user explicitly directs work there.

### Do

- Use `Windows_old_MVP/Politic Bar (pre errorlogy)/` for methodology + seed `cases/`
- Use `Cursor_Project/TZ_Cursor_Errorlogy_politicbar_FULL.md` as pipeline spec (MAS implements it)
- Treat old `errorlogy_unified_taxonomy_v*.json` copies as drafts; **MAS copy in `errorlogy-mas/data/` is active for code**
- Prefix paths in chat: **OLD SKETCH:** `errorlogy_old_version/...`

### Do not

- Extend OLD SKETCH by default when the task is “implement MVP”
- Merge politic.bar v0.6 (3 taxonomy files) with MAS without a migration task
- Use secrets from old folders (e.g. `anthropic_api_key.txt`)

## Repo layout

```
ERRORLOGY_MVP/
├── README.md, AGENTS.md
├── errorlogy-mas/              ← ACTIVE (MAS + API)
├── errorlogy-gui/              ← ACTIVE (desktop UI, API-integrated)
├── errorlogy-trn-sim/          ← RESEARCH (TRN simulation)
├── ERRORLOGY_MVP_OBSIDIAN/
└── ERRORLOGY/errorlogy_old_version/   ← OLD SKETCH
```

## Cursor agent tooling

Global skills (installed via `npx skills add … -g`) live under `~/.agents/skills/`. Cursor picks them up automatically; no change to `.cursor/hooks.json` is required.

### loop-library

Design, discover, audit, or adapt **bounded repeatable workflows** (explicit triggers, verification, stop conditions). Use when turning repeated Errorlogy work into a copy-ready loop — e.g. pre-merge `pytest`, `run_challenger.py --engine-only` smoke, or GUI/API integration checks.

Example prompts:

- "Analyze `errorlogy-mas/` and propose a loop for recurring development tasks"
- "Find a published loop for CI smoke tests and adapt it to this repository"
- "Audit this loop for weak verification and unbounded repetition"

Install/update: `npx skills add Forward-Future/loop-library --skill loop-library -g`

### /loop (session cadence)

Built-in Cursor skill for **recurring in-session prompts**, not workflow design. Syntax: `/loop [interval] <prompt>` (e.g. `/loop 10m run pytest errorlogy-mas/tests` or `/loop 5m check MAS API health`). Separate from loop-library.
