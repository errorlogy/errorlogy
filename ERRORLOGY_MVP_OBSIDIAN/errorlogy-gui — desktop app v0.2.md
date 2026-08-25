# errorlogy-gui - desktop app v0.2

> **Status:** ACTIVE · **Version:** 0.2.1 · **Product:** politic.bar desktop UI  
> **Backend:** [[errorlogy-mas - active MVP (Claude)]] (FastAPI `:8000`)

Desktop application Errorlogy MAS: analysis of governance cases, visualization of results, 3D globe with statistics by country.

## What is this

| Parameter | Value |
|----------|----------|
| Path to repo | `errorlogy-gui/` |
| Stack | Electron 42 + Vite 8 + React 19 + Tailwind 4 |
| 3D | `react-globe.gl` + Three.js |
| Charts | Recharts (Result page) |
| Installation (Windows) | NSIS → `%LOCALAPPDATA%\Programs\errorlogy-gui\` |
| Start Shortcut | `Errorlogy.lnk` → `Errorlogy.exe` |

## Pages (HashRouter)

| Route | Screen | Purpose |
|---------|-------|-----------|
| `/` | Dashboard | health, engine v1-math, LLM providers, pipeline 14 agents |
| `/globe` | Globe | **3D Globe** – choropleth + extrusion by country |
| `/analyze` | Analyze | case input, full MAS or `engine_only` |
| `/result` | Result | KPI, charts, worldline, public card |
| `/taxonomy` | Taxonomy | browse modes v16 + alpha edges |

## Communication with backend

At startup, Electron picks up uvicorn from `errorlogy-mas/` (`api.main:app`, port 8000).

| API | Use in GUI |
|-----|---------------------|
| `GET /api/health` | Dashboard (status, engine, providers, taxonomy) |
| `POST /api/analyze?engine_only=true` | Analyze (optional without LLM) |
| `GET /api/stats/countries` | Globe - seed statistics for 15 countries |
| `GET /api/taxonomy/modes` | Taxonomy |
| `GET /api/taxonomy/edges` | Taxonomy (Graph tab - list) |

Client: `errorlogy-gui/src/lib/api.ts` → `http://127.0.0.1:8000`

## Analytics Engine v1 in UI

- Dashboard: **Engine v1-math** badge, **engine** legend (red) vs **LLM** (amber) in pipeline
- Analyze: checkbox **Engine only** - deterministic analytics without Scout/Card/Red Team
- Result: label `engine_only` / `metadata.engine` from MAS response
- Numbers μ, MSI, PNO, ACC, CAT, FPD are counted by `mas/engine/`, not LLM

## 3D Globe - filling with statistics

**Data sources (merge on client):**

1. **Seed** - `errorlogy-mas/data/country_stats_seed.json` → `GET /api/stats/countries`  
   USA (Challenger), JPN (Fukushima), RUS (Kursk), GBR (Hillsborough), etc. (15 countries)
2. **Local analyses** - `localStorage` (`errorlogy_case_history`) after Run Analyze with the **Country** field

**Visualization:**

- polygon color - density of cases (red choropleth)
- extrusion height - number of cases
- click → panel: cases, avg μ, CEP, echo pressure, PNO, families, recent cases
- hover → HTML tooltip

- GeoJSON **embedded** in package: `public/geo/countries-110m.geojson`
- Earth textures - `https://cdn.jsdelivr.net/...` (internet required)

**v0.2.1 fix:** in Electron `file://` URL `//cdn...` was broken - the globe was empty. Corrected to `https://` + local GeoJSON.

Code: `src/components/ErrorlogyGlobe.tsx`, `src/pages/GlobePage.tsx`, `src/lib/countryStats.ts`

## Installation and update (important)

The **Start** shortcut launches the **packaged** `.exe`, rather than the sources from the repo.

After changes to the GUI you need **rebuild + reinstall**:

```powershell
cd C:\Users\Public\ERRORLOGY_MVP\errorlogy-gui
powershell -ExecutionPolicy Bypass -File scripts\reinstall.ps1
```

Script:
1. closes `Errorlogy.exe`
2. `Uninstall Errorlogy.exe /S` (old copy in Programs)
3. installs `dist-electron\Errorlogy Setup 0.2.0.exe /S`

**Installation path:** `C:\Users\<user>\AppData\Local\Programs\errorlogy-gui\Errorlogy.exe`

`npm run dev` - for development (Vite `:5173` + Electron, live hot reload).

## Development

```bash
cd errorlogy-gui
npm install
npm run dev #dev mode
npm run build # frontend only dist/
npm run electron:build # NSIS installer to dist-electron/
```

## What hasn't been done

- SSE / real progress of agents with backend (now timer in Analyze)
- Full catalog of cases politic.bar
- Offline cache of GeoJSON/globe textures
- Auth UI (OAuth is in the API, GUI does not use JWT)
- CI for electron:build

## Connections

| Resource | Role |
|--------|------|
| [[errorlogy-mas - active MVP (Claude)]] | backend, engine, API |
| [[Artifact map]] | repo structure |
| `errorlogy-gui/README.md` | technical doc in English |
| `errorlogy-gui/scripts/reinstall.ps1` | clean reinstallation of Windows |

## Tags

#active #errorlogy-gui #electron #globe #political-bar #mvp #v0.2

→ [[00 - Home]] · [[Artifact map]] · [[errorlogy-mas - active MVP (Claude)]]