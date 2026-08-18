---
id: TZ-002
title: SQLite persistence — история кейсов + /api/cases + Globe из DB
status: done
priority: 2
estimated: 2-3h
author: Claude
created: 2026-06-12
depends_on: []
---

## Контекст

Сейчас результаты анализа нигде не сохраняются после завершения запроса.
`sessionStorage` в GUI хранит только последний ран текущей сессии браузера.
`country_stats_seed.json` — статичный файл, не обновляется после Analyze.

Цель: персистировать каждый `CaseAnalysis` в SQLite. Без ORM — только stdlib `sqlite3`.

---

## Шаг 1 — Создать `mas/db.py`

**Новый файл:** `c:\Users\Public\ERRORLOGY_MVP\errorlogy-mas\mas\db.py`

```python
"""SQLite persistence for case analysis results."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "errorlogy.db"


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    with _conn() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                case_id     TEXT PRIMARY KEY,
                title       TEXT,
                country     TEXT,
                year        INTEGER,
                engine_only INTEGER DEFAULT 0,
                created_at  TEXT,
                result_json TEXT
            )
        """)
        con.execute("CREATE INDEX IF NOT EXISTS idx_country ON cases(country)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_year    ON cases(year)")


def save_case(
    case_id: str,
    title: str,
    country: str,
    year: int,
    engine_only: bool,
    result: dict,
) -> None:
    with _conn() as con:
        con.execute(
            """INSERT OR REPLACE INTO cases
               (case_id, title, country, year, engine_only, created_at, result_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                case_id, title, country, year, int(engine_only),
                datetime.now(timezone.utc).isoformat(),
                json.dumps(result, ensure_ascii=False),
            ),
        )


def get_case(case_id: str) -> dict | None:
    with _conn() as con:
        row = con.execute(
            "SELECT result_json FROM cases WHERE case_id = ?", (case_id,)
        ).fetchone()
    return json.loads(row["result_json"]) if row else None


def list_cases(limit: int = 50) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            """SELECT case_id, title, country, year, engine_only, created_at
               FROM cases ORDER BY created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def country_stats() -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            """SELECT country,
                      COUNT(*)        AS total_cases,
                      MAX(created_at) AS last_seen
               FROM   cases
               WHERE  country != ''
               GROUP  BY country
               ORDER  BY total_cases DESC"""
        ).fetchall()
    return [dict(r) for r in rows]
```

---

## Шаг 2 — Инициализировать DB при старте FastAPI

**Файл:** `api/main.py`

Найти `lifespan` или `startup` event handler и добавить:
```python
from mas.db import init_db

# В lifespan или @app.on_event("startup"):
init_db()
```

Если `lifespan` не используется, добавить:
```python
@app.on_event("startup")
async def startup():
    from mas.db import init_db
    init_db()
```

---

## Шаг 3 — Сохранять результат в оркестраторе

**Файл:** `mas/orchestrator.py`

Добавить импорт в начало файла:
```python
from . import db as case_db
```

В `run_engine_from_case` — добавить после `pipeline_metrics.finish_run(status="ok")`:
```python
case_db.save_case(
    case_id=case.case_id,
    title=case.title,
    country=case.country,
    year=case.year,
    engine_only=True,
    result=result.model_dump(),
)
```

В `run_from_text` — добавить после `pipeline_metrics.finish_run(status="ok")`:
```python
case_db.save_case(
    case_id=case_id,
    title=case.title,
    country=case.country,
    year=case.year,
    engine_only=False,
    result=result.model_dump(),
)
```

---

## Шаг 4 — Обновить stats router

**Файл:** `api/routers/stats.py`

Заменить реализацию `country_stats` endpoint:
```python
import json
from pathlib import Path
from fastapi import APIRouter
from mas import db as case_db
from mas.engine import ENGINE_VERSION

router = APIRouter(prefix="/api/stats", tags=["stats"])
_SEED = Path(__file__).parent.parent.parent / "data" / "country_stats_seed.json"


@router.get("/countries")
async def country_stats():
    rows = case_db.country_stats()
    if not rows and _SEED.exists():
        # Fallback: seed JSON пока DB пустая
        return json.loads(_SEED.read_text(encoding="utf-8"))
    return {
        "engine": ENGINE_VERSION,
        "total_cases": sum(r["total_cases"] for r in rows),
        "countries": rows,
    }


@router.get("/cases")
async def list_cases(limit: int = 50):
    return {"cases": case_db.list_cases(limit=limit)}
```

---

## Шаг 5 — Добавить endpoint для получения кейса по ID

**Файл:** `api/routers/analysis.py`

Добавить новый endpoint:
```python
@router.get("/api/cases/{case_id}")
async def get_case(case_id: str):
    from mas.db import get_case
    result = get_case(case_id)
    if not result:
        raise HTTPException(status_code=404, detail="Case not found")
    return result
```

---

## Проверка

```bash
cd c:\Users\Public\ERRORLOGY_MVP\errorlogy-mas

# Инициализация вручную:
python -c "from mas.db import init_db; init_db(); print('DB created at data/errorlogy.db')"

# После одного запроса /api/analyze:
python -c "from mas.db import list_cases; import json; print(json.dumps(list_cases(), indent=2))"
# Ожидается: 1 запись

# Тесты не должны сломаться:
pytest tests/ -x -q
```

---

## Что НЕ делать

- Не добавлять SQLAlchemy / Alembic / другие ORM — только stdlib sqlite3
- Не изменять схему `CaseAnalysis` — сохраняем как `model_dump()` JSON
- Не удалять `country_stats_seed.json` — он нужен как fallback
- Не добавлять endpoints DELETE/UPDATE для кейсов (scope creep)
