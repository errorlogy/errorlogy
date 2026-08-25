# errorlogy-gui

> **STATUS: ACTIVE** — Electron + Vite + React desktop UI for Errorlogy MAS.

Backend: [`../errorlogy-mas/`](../errorlogy-mas/) (FastAPI on port 8000).

## Features

- **Dashboard** — health, engine v1-math, LLM providers, 14-agent pipeline overview
- **MAS Metrics** — live pipeline timing, token usage, agent registry (`GET /api/metrics`)
- **Info Stream** — RSS, US gov APIs, URL ingest, CEP alerts (`/api/ingest`, `/api/signals`)
- **Globe** — 3D Earth with country-level stats + signal trends
- **Analyze** — full MAS, `engine_only`, LightweightScout, dual-run; SSE step progress
- **Result** — WMS/α/EGD/PNO/ACC/CAT/T4D/FPD/LBI, Red Team, Neutrality, public card
- **Taxonomy** — browse v16 modes and alpha edges

## Run (development)

**Terminal 1 — API:**
```bash
cd errorlogy-mas
pip install -r requirements.txt
python api/main.py
# or: uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — GUI (browser or Electron):**
```bash
cd errorlogy-gui
npm install
npm run dev:vite     # browser only — open http://localhost:5173 (Vite proxies /api → :8000)
npm run dev          # Vite + Electron (Electron auto-starts API)
```

**Seeing latest UI changes:** the Start Menu **Errorlogy** shortcut runs the last **installed** build (often stale). For current source, use `npm run dev` or `npm run dev:vite` in the repo — do not launch the old desktop shortcut. After `npm run build`, unpackaged `electron .` loads `dist/` when Vite is not running. To refresh the installed app: `npm run electron:build` then `powershell -ExecutionPolicy Bypass -File scripts\reinstall.ps1`.

Without API keys, use **Engine only** on Analyze or **Challenger demo (offline)** on the Analyze page.

Smoke test backend: `python errorlogy-mas/examples/run_challenger.py --engine-only`

## Environment

| Variable | Purpose |
|----------|---------|
| `VITE_API_BASE` | Override API URL (default: proxy in dev, `http://127.0.0.1:8000` in production build). Set when building for Electron if the API is not on localhost: `VITE_API_BASE=http://127.0.0.1:8000 npm run build` |
| `ERRORLOGY_PYTHON` | Electron only — Python executable for spawning FastAPI. Auto-detected: `py -3`, `python`, or `%LOCALAPPDATA%\Programs\Python\Python3xx\python.exe`. Must have `errorlogy-mas` deps installed (`pip install -r requirements.txt`). |
| `ERRORLOGY_MAS_DIR` | Electron only — path to `errorlogy-mas/` (packaged default: `%PUBLIC%\ERRORLOGY_MVP\errorlogy-mas`). **Required alongside the desktop app** — MAS is not bundled in the installer. |
| `ANTHROPIC_API_KEY` etc. | In `errorlogy-mas/.env` — required for full MAS / Scout |

OAuth scaffold: store JWT in `localStorage` key `errorlogy_token` — sent as `Authorization: Bearer` when present.

## Install desktop app (Windows)

The packaged app **auto-starts** the MAS FastAPI backend on `127.0.0.1:8000` when you open Errorlogy from the desktop shortcut — if nothing is already listening there.

**Co-install requirement:** `errorlogy-mas/` must be present on disk (not bundled inside the `.exe`). Default path:

`C:\Users\Public\ERRORLOGY_MVP\errorlogy-mas`

Override with the `ERRORLOGY_MAS_DIR` environment variable (system or user env, or set before launching).

**Python:** Electron spawns `uvicorn` via a Python 3.10+ install that has `pip install -r requirements.txt` applied in `errorlogy-mas/`. Discovery order: `ERRORLOGY_PYTHON` → `py -3` → `python` → `%LOCALAPPDATA%\Programs\Python\Python3xx\python.exe`.

**Manual fallback** (if the shortcut shows "Backend unavailable"):

```powershell
cd C:\Users\Public\ERRORLOGY_MVP\errorlogy-mas
pip install -r requirements.txt
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Then relaunch Errorlogy or click **Refresh** on Stream Forecast.

```powershell
cd errorlogy-gui
powershell -ExecutionPolicy Bypass -File scripts\reinstall.ps1
```

Rebuilds the installer from current source and refreshes Start Menu / desktop shortcuts.

## Stack

- React 19, Tailwind v4, Recharts, **react-globe.gl** (Three.js)
- API client: `src/lib/api.ts` — types mirror `errorlogy-mas/mas/schemas/analysis.py`
