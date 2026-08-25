# For AI agents

Short guide for **Cursor**, **Claude Code**, **Codex**, and others.

## Two repository modes

```
errorlogy-mas/  errorlogy-gui/     →  ACTIVE (new MVP)
ERRORLOGY/errorlogy_old_version/  →  OLD SKETCH (archive)
```

In chat: **ACTIVE:** `errorlogy-mas/…` · **OLD SKETCH:** `errorlogy_old_version/…`

## Read first

1. `README.md`, `AGENTS.md` (root)
2. [[errorlogy-mas — active MVP (Claude)]] — backend + Analytics Engine v1
3. [[errorlogy-gui — desktop app v0.2]] — Electron UI, Globe, MAS metrics `/#/mas`, `reinstall.ps1`
4. [[Taxonomy vs Engine — formalization gap]] — ontology vs math, v2 strategy
5. [[MAS — orchestrator metrics]] — `GET /api/metrics`, pipeline timing
6. [[Claude analysis — engine v1 status]] — engine audit, calibration gaps, priority queue
7. `errorlogy-mas/AGENTS.md` — MAS and language rules
8. `.cursor/rules/errorlogy-mas-active.mdc` + `errorlogy-archive.mdc`
9. [[Repository status — OLD SKETCH]] — archive only

## Do

- New backend / agents / API → **`errorlogy-mas/`**
- New UI → **`errorlogy-gui/`**; after changes — `scripts/reinstall.ps1` (Start Menu shortcut = packaged exe)
- Methodology and seed cases → OLD SKETCH `Politic Bar (pre errorlogy)/`
- Ontology for code → `errorlogy-mas/data/errorlogy_unified_taxonomy_v16.json`
- E2E check → `python errorlogy-mas/examples/run_challenger.py` (Challenger, engine smoke)
- Exa flow → `python errorlogy-mas/examples/run_exa_flow.py` (Horizon + source discovery)
- zvec KB demo → `python errorlogy-mas/examples/zvec_kb_demo.py`
- Taxonomy in Obsidian → [[Taxonomy/00 — Taxonomy index]]
- Session 2026-06-24 → [[Session — GLM Exa zvec KB 2026-06-24]]

## Do not

- Write MVP code in `errorlogy_old_version/` without explicit request
- Commit `.env`, API keys
- Describe AGIU / v0.6 pipeline as "current product"
- Merge v0.6 taxonomy and v16 without a migration task

## Cursor tooling

- **loop-library** — global skill (`~/.agents/skills/loop-library/`); see `AGENTS.md` → Cursor agent tooling
- **/loop** — recurring in-session prompts (separate from loop-library)
- `.cursor/hooks/obsidian-memory.ps1` — auto MEM in `ERRORLOGY_MVP_OBSIDIAN/Memory/` (vault path from repo cwd)

## Obsidian

- [[Flows/00 — Flow Index]] — hypotheses and experiments
- Regenerate taxonomy branch: `python ERRORLOGY_MVP_OBSIDIAN/_scripts/generate_taxonomy_branch.py`

→ [[00 — Home]]

#agents #active #errorlogy-mas #cursor
