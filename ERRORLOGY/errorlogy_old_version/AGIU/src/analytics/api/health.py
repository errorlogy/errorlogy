"""Health & readiness endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"ok": True, "service": "errorlogy-analytics"}


@router.get("/ready")
def ready() -> dict:
    return {"ready": True}
