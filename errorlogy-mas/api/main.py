"""
Errorlogy MAS — FastAPI application
Запуск: python api/main.py  (или uvicorn api.main:app --reload)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from mas.config import JWT_SECRET
from api.auth.oauth import router as auth_router
from api.routers.analysis import router as analysis_router
from api.routers.stats import router as stats_router
from api.routers.metrics import router as metrics_router
from api.routers.ingest import router as ingest_router
from api.routers.signals import router as signals_router
from api.routers.forecast import router as forecast_router
from api.routers.cross_layer import router as cross_layer_router

app = FastAPI(
    title="Errorlogy MAS API",
    description="Multi-agent system for analytical monitoring of government management errors.",
    version="0.1.0",
)

app.add_middleware(SessionMiddleware, secret_key=JWT_SECRET)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(stats_router)
app.include_router(metrics_router)
app.include_router(ingest_router)
app.include_router(signals_router)
app.include_router(forecast_router)
app.include_router(cross_layer_router)


@app.on_event("startup")
async def startup():
    from mas.db import init_db
    init_db()


@app.get("/")
async def root():
    return {
        "project": "Errorlogy MAS",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health",
        "auth": {
            "google":   "/api/auth/google/login",
            "github":   "/api/auth/github/login",
            "telegram": "/api/auth/telegram/callback",
            "me":       "/api/auth/me",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
