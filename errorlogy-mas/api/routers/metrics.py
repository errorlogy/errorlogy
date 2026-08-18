"""MAS orchestrator metrics API."""
import pathlib
import sys

from fastapi import APIRouter

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from mas import metrics

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("")
async def get_metrics():
    return metrics.summary()
