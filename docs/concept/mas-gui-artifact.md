# Errorlogy MAS + GUI — local development artifact

> Created: 2026-06-12 · Status: installed and ready to run

## Components

| Component | Path | Role |
|-----------|------|------|
| **MAS Backend** | `errorlogy-mas/` | FastAPI + 14 agents, Python 3.12 |
| **Electron GUI** | `errorlogy-gui/` | Desktop Electron + React + Tailwind |
| **Taxonomy** | `errorlogy-mas/data/errorlogy_unified_taxonomy_v16.json` | 381 modes, 89 α-edges |

## 14 agents — analysis pipeline

```
DATA (raw_text)
  ├─ 01 Scout           — case structure extraction
  ├─ 02 WMS             — weak multisource signals (MSI, CEP)
  ├─ 03 FuzzyClassifier — fuzzy μ mode scoring
  ├─ 04 AlphaPropagation — graph propagation (89 edges)
  ├─ 05 PNO             — system regime PNO-1..7
  ├─ 06 ACC             — maximum contribution clusters
  ├─ 07 EGD             — echo-room dynamics
  ├─ 08 T4D             — temporal topology (3D+1D)
  ├─ 09 CAT             — catastrophe hypothesis
  ├─ 10 FPD             — fuzzy forecast
  ├─ 11 LBI             — improvement alternatives
  ├─ 12 RedTeam         — adversarial review
  ├─ 13 CardCompiler    — public card
  └─ 14 NeutralityAudit — language audit (anti-overclaim)
```

## LLM router — 7 providers

OpenAI → DeepSeek → Groq → Google Gemini → Kimi → OpenRouter → Anthropic Claude

Keys: `errorlogy-mas/.env` (do not commit).

## GUI — screens

| Screen | Route | Description |
|--------|-------|-------------|
| Dashboard | `/` | System status, providers, pipeline |
| Analyze | `/analyze` | Case input form + agent progress |
| Result | `/result` | μ histogram, PNO, T4D, ACC, CAT, FPD, LBI, Public Card |
| Taxonomy | `/taxonomy` | Mode search/filter, α links |

Stack: Electron + React + Vite + Tailwind + Recharts
