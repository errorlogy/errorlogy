"""Country-level Errorlogy statistics for the globe UI."""
import json
import pathlib
import sys

from fastapi import APIRouter

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from mas import db as case_db
from mas.engine import ENGINE_VERSION

router = APIRouter(prefix="/api/stats", tags=["stats"])

_SEED_PATH = pathlib.Path(__file__).parent.parent.parent / "data" / "country_stats_seed.json"


@router.get("/countries")
async def country_stats():
    if case_db.case_count() > 0:
        data = case_db.country_stats_globe()
        return {
            "engine": ENGINE_VERSION,
            "source": "database",
            "total_cases": data["total_cases"],
            "countries": data["countries"],
        }
    if _SEED_PATH.exists():
        with open(_SEED_PATH, encoding="utf-8") as f:
            data = json.load(f)
        countries = data.get("countries", [])
        total_cases = sum(c.get("cases", 0) for c in countries)
        return {
            "engine": ENGINE_VERSION,
            "source": "seed",
            "total_cases": total_cases,
            "countries": countries,
        }
    return {"engine": ENGINE_VERSION, "source": "empty", "total_cases": 0, "countries": []}


@router.get("/cases")
async def list_cases(limit: int = 50):
    return {"cases": case_db.list_cases(limit=limit)}
