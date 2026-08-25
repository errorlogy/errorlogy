# ERRORLOGY_MVP status analysis — snapshot 2026-06-12

> Source: Cursor IDE analysis of the live project tree

---

## 1. Maturity: where we are on the map

| Zone | Status | Maturity |
|------|--------|----------|
| `errorlogy-mas/` | ACTIVE | ~MVP backend: pipeline built, Challenger demo, API |
| `errorlogy-gui/` | ACTIVE | ~alpha UI: Electron + React, API-connected, no catalog/history |
| `ERRORLOGY/errorlogy_old_version/` | OLD SKETCH | Methodology v0.6 reference, seed cases, spec |
| `ERRORLOGY_MVP_OBSIDIAN/` | Documentation | Good navigation; GUI description outdated |
| Tests / CI / deploy | — | Missing in active part |

**Summary:** a research MVP with one end-to-end scenario (text → 14 steps → JSON + card), not public politic.bar.

---

## 2. Architecture (current)

```
errorlogy-gui Electron
  └─ fetch → errorlogy-mas FastAPI :8000
               ├─ /api/health
               ├─ /api/analyze → pipeline:
               │     Scout → WMS → Classifier → Alpha (algo)
               │     → PNO → ACC → EGD → T4D → CAT
               │     → FPD → LBI → Red Team → Card Compiler → Neutrality
               └─ /api/taxonomy/*
                     └─ errorlogy_unified_taxonomy_v16.json

LLM Router (fallback): Anthropic → OpenAI → DeepSeek → Groq → Google → Kimi → OpenRouter
Only non-LLM step: AlphaPropagationAgent — pure math on graph edges
```

---

## Priorities for next step

1. **Persistence** — SQLite or JSON files for case history
2. **Classifier coverage** — GT, HM, EGD, etc. in prompt
3. **Real progress streaming** — SSE or WebSocket
4. **Seed case corpus** — import 5 cases from OLD SKETCH
5. **JWT in GUI** — OAuth login flow in Electron

Full version: see Obsidian source or `ERRORLOGY_MVP_OBSIDIAN/`.
