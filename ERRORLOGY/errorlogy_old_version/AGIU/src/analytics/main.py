"""Errorlogy Analytics — local FastAPI microservice."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from analytics.config import ANALYTICS_HOST, ANALYTICS_PORT, cors_allow_origins
from analytics.api import health, taxonomy, math_demo
from analytics.core.taxonomy_loader import TaxonomyLoader


@asynccontextmanager
async def lifespan(_app: FastAPI):
    TaxonomyLoader.load()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Errorlogy Analytics",
        description="Local math engine for the Errorlogy taxonomy.",
        version="0.1.0",
        lifespan=lifespan,
    )

    origins = cors_allow_origins()
    if origins is None:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(health.router, prefix="/api/v1")
    app.include_router(taxonomy.router, prefix="/api/v1")
    app.include_router(math_demo.router, prefix="/api/v1")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "analytics.main:app",
        host=ANALYTICS_HOST,
        port=ANALYTICS_PORT,
        reload=True,
    )
