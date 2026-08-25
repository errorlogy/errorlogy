# Artifact map

Base path: `<repo-root>/` (local clone)

```
ERRORLOGY_MVP/
├── README.md, AGENTS.md
├── errorlogy-mas/                   ← ACTIVE (Claude): MAS + FastAPI
│   ├── mas/                         orchestrator, agents, providers, schemas
│   ├── api/                         FastAPI, OAuth, /api/analyze
│   ├── data/errorlogy_unified_taxonomy_v16.json
│   ├── examples/run_challenger.py
│   ├── examples/run_exa_flow.py
│   ├── examples/zvec_kb_demo.py
│   ├── mas/kb/                      zvec hybrid KB
│   └── examples/challenger_output.json
├── errorlogy-gui/                   ← ACTIVE v0.2: Electron + React + 3D Globe
│   ├── dist-electron/               Errorlogy Setup 0.2.0.exe
│   └── scripts/reinstall.ps1        uninstall + install Windows
├── ERRORLOGY_MVP_OBSIDIAN/          ← this vault
│   ├── Taxonomy/
│   └── Flows/
└── ERRORLOGY/
    └── errorlogy_old_version/       ← OLD SKETCH
        ├── Windows_old_MVP/
        │   └── Politic Bar (pre errorlogy)/  … v0.6 pipeline, cases
        ├── AGIU/                    … health + analytics demo
        └── Cursor_Project/          … spec + taxonomy copy
```

## Active MVP (Claude)

Detail: [[errorlogy-mas — active MVP (Claude)]]

| Component | Path |
|-----------|------|
| 14-agent pipeline | `errorlogy-mas/mas/orchestrator.py` |
| LLM router | `errorlogy-mas/mas/providers/` (incl. `ZaiProvider`, GLM-5.2 map) |
| Local KB | `errorlogy-mas/mas/kb/` |
| Exa discovery | `errorlogy-mas/mas/ingest/source_discovery.py` |
| REST API | `errorlogy-mas/api/main.py` |
| Demo output | `errorlogy-mas/examples/challenger_output.json` |
| Analytics engine | `errorlogy-mas/mas/engine/` |

### Desktop UI (v0.2)

→ [[errorlogy-gui — desktop app v0.2]]

| Component | Path |
|-----------|------|
| Electron shell | `errorlogy-gui/electron/main.cjs` |
| 3D Globe | `errorlogy-gui/src/pages/GlobePage.tsx` |
| Country stats API | `errorlogy-mas/api/routers/stats.py` |
| Windows reinstall | `errorlogy-gui/scripts/reinstall.ps1` |
| MAS metrics API | `GET /api/metrics` |
| MAS metrics GUI | `/#/mas` |
| Installer | `errorlogy-gui/dist-electron/Errorlogy Setup 0.2.0.exe` |

## OLD SKETCH

See [[politic.bar — MVP sketch]], [[AGIU — platform sketch]].

## Ontology

| Where | File | Used by |
|-----|------|----------------|
| **ACTIVE** | `errorlogy-mas/data/…v16.json` | MAS pipeline, API |
| Obsidian | [[Taxonomy/00 — Taxonomy index]] | navigation |
| OLD | `errorlogy_old_version/…/taxonomy/*.json` | politic.bar v0.6 |
| OLD | copies of `errorlogy_unified_taxonomy_v*.json` | AGIU, archive |

## Missing from repo

- `errorlogy_retrospective_200_case_seed_v3.json` (mentioned in spec)

→ [[00 — Home]] · [[For AI agents]]

#map #active #old-sketch
