"""SQLite persistence for case analysis results and pipeline runs."""

from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "errorlogy.db"

_COUNTRY_ISO3: dict[str, str] = {
    "usa": "USA",
    "united states": "USA",
    "uk": "GBR",
    "united kingdom": "GBR",
    "ussr": "RUS",
    "russia": "RUS",
    "france": "FRA",
    "germany": "DEU",
    "japan": "JPN",
    "china": "CHN",
    "india": "IND",
    "brazil": "BRA",
    "canada": "CAN",
    "australia": "AUS",
    "mexico": "MEX",
    "south korea": "KOR",
    "korea": "KOR",
    "italy": "ITA",
    "spain": "ESP",
    "netherlands": "NLD",
    "sweden": "SWE",
    "norway": "NOR",
    "poland": "POL",
    "ukraine": "UKR",
    "israel": "ISR",
    "turkey": "TUR",
    "saudi arabia": "SAU",
    "south africa": "ZAF",
    "argentina": "ARG",
    "indonesia": "IDN",
    "thailand": "THA",
    "vietnam": "VNM",
    "egypt": "EGY",
    "nigeria": "NGA",
}

_ISO3_NAMES: dict[str, str] = {
    "USA": "United States",
    "GBR": "United Kingdom",
    "RUS": "Russia",
    "FRA": "France",
    "DEU": "Germany",
    "JPN": "Japan",
    "CHN": "China",
    "IND": "India",
    "BRA": "Brazil",
    "CAN": "Canada",
    "AUS": "Australia",
    "MEX": "Mexico",
    "KOR": "South Korea",
    "ITA": "Italy",
    "ESP": "Spain",
    "NLD": "Netherlands",
    "SWE": "Sweden",
    "NOR": "Norway",
    "POL": "Poland",
    "UKR": "Ukraine",
    "ISR": "Israel",
    "TUR": "Turkey",
    "SAU": "Saudi Arabia",
    "ZAF": "South Africa",
    "ARG": "Argentina",
    "IDN": "Indonesia",
    "THA": "Thailand",
    "VNM": "Vietnam",
    "EGY": "Egypt",
    "NGA": "Nigeria",
}


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
        con.execute("CREATE INDEX IF NOT EXISTS idx_cases_country ON cases(country)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_cases_year ON cases(year)")
        con.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id       TEXT PRIMARY KEY,
                case_id      TEXT,
                engine_only  INTEGER DEFAULT 0,
                status       TEXT,
                started_at   TEXT,
                finished_at  TEXT,
                steps_json   TEXT,
                totals_json  TEXT
            )
        """)
        con.execute("CREATE INDEX IF NOT EXISTS idx_runs_case ON pipeline_runs(case_id)")
        con.execute("""
            CREATE TABLE IF NOT EXISTS raw_documents (
                doc_id       TEXT PRIMARY KEY,
                source       TEXT,
                source_type  TEXT,
                url          TEXT,
                title        TEXT,
                country      TEXT,
                text         TEXT,
                status       TEXT DEFAULT 'pending',
                error_msg    TEXT,
                case_id      TEXT,
                ingested_at  TEXT,
                analyzed_at  TEXT
            )
        """)
        con.execute("CREATE INDEX IF NOT EXISTS idx_docs_status ON raw_documents(status)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_docs_source ON raw_documents(source)")
        con.execute("""
            CREATE TABLE IF NOT EXISTS signal_timeseries (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                country        TEXT,
                iso3           TEXT,
                case_id        TEXT,
                doc_id         TEXT,
                recorded_at    TEXT,
                msi            REAL,
                cep            REAL,
                echo_pressure  REAL,
                dominant_pno   TEXT,
                cat            TEXT
            )
        """)
        con.execute("CREATE INDEX IF NOT EXISTS idx_signals_iso ON signal_timeseries(iso3)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_signals_time ON signal_timeseries(recorded_at)")
        con.execute("""
            CREATE TABLE IF NOT EXISTS cross_layer_events (
                event_id     TEXT PRIMARY KEY,
                story_id     TEXT NOT NULL,
                event_type   TEXT NOT NULL,
                epistemic_label TEXT NOT NULL,
                envelope_json TEXT NOT NULL,
                created_at   TEXT NOT NULL
            )
        """)
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_cle_story ON cross_layer_events(story_id)"
        )
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_cle_type ON cross_layer_events(event_type)"
        )
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_cle_created ON cross_layer_events(created_at)"
        )


def save_cross_layer_event(event_id: str, envelope: dict) -> dict:
    """Persist a framed cross-layer envelope. INSTITUTIONAL_MODEL storage only."""
    now = datetime.now(timezone.utc).isoformat()
    with _conn() as con:
        con.execute(
            """
            INSERT INTO cross_layer_events
                (event_id, story_id, event_type, epistemic_label, envelope_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                envelope["story_id"],
                envelope["event_type"],
                envelope["epistemic_label"],
                json.dumps(envelope, ensure_ascii=False),
                now,
            ),
        )
    return {"event_id": event_id, "created_at": now, **envelope}


def list_cross_layer_events(
    limit: int = 50,
    story_id: str | None = None,
    event_type: str | None = None,
) -> list[dict]:
    clauses: list[str] = []
    params: list = []
    if story_id:
        clauses.append("story_id = ?")
        params.append(story_id)
    if event_type:
        clauses.append("event_type = ?")
        params.append(event_type)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    params.append(max(1, min(limit, 500)))
    with _conn() as con:
        rows = con.execute(
            f"""
            SELECT event_id, story_id, event_type, epistemic_label, envelope_json, created_at
            FROM cross_layer_events
            {where}
            ORDER BY created_at DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
    out: list[dict] = []
    for row in rows:
        env = json.loads(row["envelope_json"])
        out.append(
            {
                "event_id": row["event_id"],
                "created_at": row["created_at"],
                **env,
            }
        )
    return out


def get_cross_layer_event(event_id: str) -> dict | None:
    with _conn() as con:
        row = con.execute(
            """
            SELECT event_id, envelope_json, created_at
            FROM cross_layer_events WHERE event_id = ?
            """,
            (event_id,),
        ).fetchone()
    if not row:
        return None
    env = json.loads(row["envelope_json"])
    return {"event_id": row["event_id"], "created_at": row["created_at"], **env}


def country_to_iso3(country: str) -> str:
    if not country:
        return ""
    key = country.strip().lower()
    if key.upper() in _ISO3_NAMES:
        return key.upper()
    return _COUNTRY_ISO3.get(key, country.strip().upper()[:3] if len(country.strip()) >= 3 else country.strip().upper())


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
                case_id,
                title,
                country,
                year,
                int(engine_only),
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


def case_count() -> int:
    with _conn() as con:
        row = con.execute("SELECT COUNT(*) AS n FROM cases").fetchone()
    return int(row["n"]) if row else 0


def save_pipeline_run(run_dict: dict) -> None:
    with _conn() as con:
        con.execute(
            """INSERT OR REPLACE INTO pipeline_runs
               (run_id, case_id, engine_only, status, started_at, finished_at, steps_json, totals_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                run_dict["run_id"],
                run_dict["case_id"],
                int(run_dict.get("engine_only", False)),
                run_dict.get("status", "ok"),
                run_dict.get("started_at"),
                run_dict.get("finished_at"),
                json.dumps(run_dict.get("steps", []), ensure_ascii=False),
                json.dumps(run_dict.get("totals", {}), ensure_ascii=False),
            ),
        )


def list_pipeline_runs(limit: int = 30) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            """SELECT run_id, case_id, engine_only, status, started_at, finished_at,
                      steps_json, totals_json
               FROM pipeline_runs ORDER BY started_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["engine_only"] = bool(d["engine_only"])
        d["steps"] = json.loads(d.pop("steps_json") or "[]")
        d["totals"] = json.loads(d.pop("totals_json") or "{}")
        out.append(d)
    return out


def _family_from_mode_id(mode_id: str) -> str:
    if "-" in mode_id:
        return mode_id.split("-")[0]
    return mode_id[:3] if mode_id else "CB"


def save_raw_document(
    *,
    doc_id: str,
    source: str,
    source_type: str,
    url: str,
    title: str,
    country: str,
    text: str,
    status: str = "pending",
) -> None:
    with _conn() as con:
        con.execute(
            """INSERT OR REPLACE INTO raw_documents
               (doc_id, source, source_type, url, title, country, text, status,
                ingested_at, analyzed_at, case_id, error_msg)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL)""",
            (
                doc_id, source, source_type, url, title, country, text, status,
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def mark_document_analyzed(doc_id: str, *, case_id: str) -> None:
    with _conn() as con:
        con.execute(
            """UPDATE raw_documents
               SET status = 'analyzed', analyzed_at = ?, case_id = ?
               WHERE doc_id = ?""",
            (datetime.now(timezone.utc).isoformat(), case_id, doc_id),
        )


def update_document_status(doc_id: str, status: str, error_msg: str = "") -> None:
    with _conn() as con:
        con.execute(
            "UPDATE raw_documents SET status = ?, error_msg = ? WHERE doc_id = ?",
            (status, error_msg, doc_id),
        )


def list_raw_documents(
    *,
    status: str | None = None,
    limit: int = 50,
) -> list[dict]:
    with _conn() as con:
        if status:
            rows = con.execute(
                """SELECT doc_id, source, source_type, url, title, country, status,
                          case_id, ingested_at, analyzed_at,
                          LENGTH(text) AS text_len
                   FROM raw_documents WHERE status = ?
                   ORDER BY ingested_at DESC LIMIT ?""",
                (status, limit),
            ).fetchall()
        else:
            rows = con.execute(
                """SELECT doc_id, source, source_type, url, title, country, status,
                          case_id, ingested_at, analyzed_at,
                          LENGTH(text) AS text_len
                   FROM raw_documents ORDER BY ingested_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
    return [dict(r) for r in rows]


def get_raw_document(doc_id: str) -> dict | None:
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM raw_documents WHERE doc_id = ?", (doc_id,)
        ).fetchone()
    return dict(row) if row else None


def save_signal_point(
    *,
    country: str,
    iso3: str,
    case_id: str,
    doc_id: str,
    msi: float,
    cep: float,
    echo_pressure: float,
    dominant_pno: str,
    cat: str,
) -> None:
    with _conn() as con:
        con.execute(
            """INSERT INTO signal_timeseries
               (country, iso3, case_id, doc_id, recorded_at, msi, cep,
                echo_pressure, dominant_pno, cat)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                country, iso3, case_id, doc_id,
                datetime.now(timezone.utc).isoformat(),
                msi, cep, echo_pressure, dominant_pno, cat,
            ),
        )


def list_signal_timeseries(
    *,
    country: str | None = None,
    iso3: str | None = None,
    limit: int = 100,
) -> list[dict]:
    with _conn() as con:
        if iso3:
            rows = con.execute(
                """SELECT * FROM signal_timeseries WHERE iso3 = ?
                   ORDER BY recorded_at DESC LIMIT ?""",
                (iso3, limit),
            ).fetchall()
        elif country:
            rows = con.execute(
                """SELECT * FROM signal_timeseries WHERE country = ?
                   ORDER BY recorded_at DESC LIMIT ?""",
                (country, limit),
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT * FROM signal_timeseries ORDER BY recorded_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
    return [dict(r) for r in rows]


def signal_stream_summary() -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            """SELECT iso3, country,
                      COUNT(*) AS points,
                      MAX(recorded_at) AS last_signal_at,
                      MAX(cep) AS max_cep,
                      AVG(msi) AS avg_msi
               FROM signal_timeseries
               WHERE iso3 != ''
               GROUP BY iso3
               ORDER BY last_signal_at DESC"""
        ).fetchall()
    return [
        {
            "iso3": r["iso3"],
            "country": r["country"],
            "points": r["points"],
            "last_signal_at": r["last_signal_at"],
            "max_cep": round(r["max_cep"] or 0, 4),
            "avg_msi": round(r["avg_msi"] or 0, 4),
        }
        for r in rows
    ]


def ingest_stats() -> dict:
    with _conn() as con:
        total = con.execute("SELECT COUNT(*) AS n FROM raw_documents").fetchone()["n"]
        pending = con.execute(
            "SELECT COUNT(*) AS n FROM raw_documents WHERE status = 'pending'"
        ).fetchone()["n"]
        analyzed = con.execute(
            "SELECT COUNT(*) AS n FROM raw_documents WHERE status = 'analyzed'"
        ).fetchone()["n"]
        last = con.execute(
            "SELECT MAX(ingested_at) AS t FROM raw_documents"
        ).fetchone()["t"]
        by_source = con.execute(
            "SELECT source, COUNT(*) AS n FROM raw_documents GROUP BY source"
        ).fetchall()
        signals = con.execute("SELECT COUNT(*) AS n FROM signal_timeseries").fetchone()["n"]
    return {
        "documents_total": total,
        "documents_pending": pending,
        "documents_analyzed": analyzed,
        "signals_total": signals,
        "last_ingest_at": last,
        "sources": {r["source"]: r["n"] for r in by_source},
    }


def country_stats_globe() -> dict:
    """Aggregate cases into CountryStatsResponse-compatible structure."""
    with _conn() as con:
        rows = con.execute(
            """SELECT case_id, title, country, year, created_at, result_json
               FROM cases WHERE country != '' ORDER BY created_at DESC"""
        ).fetchall()

    by_iso: dict[str, dict] = {}
    for row in rows:
        result = json.loads(row["result_json"])
        iso3 = country_to_iso3(row["country"])
        if not iso3:
            continue

        top_modes = result.get("top_modes") or []
        max_mu = max((m.get("mu", 0) for m in top_modes), default=0.0)
        cep = (result.get("wms") or {}).get("cep", 0.0)
        echo = (result.get("egd") or {}).get("echo_room_pressure", 0.0)
        pno = (result.get("pno") or {}).get("dominant_pno", "")
        cat = (result.get("cat") or {}).get("catastrophe_hypothesis", "CAT-000")

        if iso3 not in by_iso:
            by_iso[iso3] = {
                "iso3": iso3,
                "name": _ISO3_NAMES.get(iso3, row["country"]),
                "cases": 0,
                "mu_sum": 0.0,
                "max_cep": 0.0,
                "echo_sum": 0.0,
                "pno_counts": defaultdict(int),
                "families": defaultdict(int),
                "recent_cases": [],
            }

        agg = by_iso[iso3]
        agg["cases"] += 1
        agg["mu_sum"] += max_mu
        agg["max_cep"] = max(agg["max_cep"], cep)
        agg["echo_sum"] += echo
        if pno:
            agg["pno_counts"][pno] += 1
        for m in top_modes[:5]:
            agg["families"][_family_from_mode_id(m.get("mode_id", ""))] += 1

        if len(agg["recent_cases"]) < 5:
            agg["recent_cases"].append({
                "case_id": row["case_id"],
                "title": row["title"] or row["case_id"],
                "year": row["year"] or 0,
                "country": row["country"],
                "dominant_pno": pno,
                "max_mu": round(max_mu, 4),
                "cep": round(cep, 4),
                "cat": cat,
            })

    signal_by_iso = {s["iso3"]: s for s in signal_stream_summary()}

    countries = []
    for iso3, agg in sorted(by_iso.items(), key=lambda x: -x[1]["cases"]):
        n = agg["cases"] or 1
        dominant_pno = max(agg["pno_counts"], key=agg["pno_counts"].get) if agg["pno_counts"] else ""
        sig = signal_by_iso.get(iso3, {})
        max_cep = max(agg["max_cep"], sig.get("max_cep", 0))
        countries.append({
            "iso3": iso3,
            "name": agg["name"],
            "cases": agg["cases"],
            "avg_mu": round(agg["mu_sum"] / n, 4),
            "max_cep": round(max_cep, 4),
            "avg_echo_pressure": round(agg["echo_sum"] / n, 4),
            "dominant_pno": dominant_pno,
            "top_families": dict(agg["families"]),
            "recent_cases": agg["recent_cases"],
            "last_signal_at": sig.get("last_signal_at"),
            "signal_points": sig.get("points", 0),
        })

    return {
        "total_cases": sum(c["cases"] for c in countries),
        "countries": countries,
    }
