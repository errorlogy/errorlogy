# errorlogy-gui-v2

Simplified browser UI for **Errorlogy MAS forecasting** — focus on stream and case forecast, data streams, and transparent methodology.

Full desktop UI remains in [`errorlogy-gui/`](../errorlogy-gui/) (v0.2.x, Electron).

## Run alongside v1

**Terminal 1 — API** (shared by both UIs):

```bash
cd errorlogy-mas
python api/main.py
```

**Terminal 2 — v2** (port **5174**):

```bash
cd errorlogy-gui-v2
npm install
npm run dev
```

Open http://localhost:5174

**Terminal 3 (optional) — v1** (port 5173):

```bash
cd errorlogy-gui
npm run dev:vite
```

Vite proxies `/api` → `http://127.0.0.1:8000`.

## Pages

| Path | Purpose |
|------|---------|
| `/` | Overview: health, case vs stream forecast, methodology |
| `/stream` | Stream forecast — `GET /api/forecast/stream` |
| `/case` | Case forecast — `POST /api/analyze` (SSE or sync) |
| `/data` | Data streams — ingest, RSS, manual input |

## Build

```bash
npm run build
```

## Differences from v1

- 4 pages instead of 10+ (no globe, full taxonomy, MAS metrics, Electron)
- Horizontal navigation, English UI by default
- Emphasis on μ ≠ probability and `methodology` field from API
- Browser-only (no OAuth, no packaging)

## Variables

- `VITE_API_BASE` — if API is not on localhost:8000 (production)
