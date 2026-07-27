"""
store.py — Phase 2 (BUILD_SPEC.md §5). SQLite writer/reader + latest.json
export, so vp-dashboard.pages.dev and the Command Center KPI page can show
current state with zero Claude and zero Slack-parsing.

Schema (exactly as specified):
  kpis(store, metric, value, as_of, period, source)
  runs(job, ts, status, detail)

kpis is upserted (one row per store+metric+as_of — reruns for the same
as_of date overwrite rather than duplicate). runs is append-only (a real
run history, unlike the heartbeat JSON files which only ever hold the
latest state).
"""

from __future__ import annotations
import json
import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "vpops.db"
LATEST_JSON_PATH = DATA_DIR / "latest.json"

SCHEMA = """
CREATE TABLE IF NOT EXISTS kpis (
    store TEXT NOT NULL,
    metric TEXT NOT NULL,
    value REAL NOT NULL,
    as_of TEXT NOT NULL,
    period TEXT,
    source TEXT,
    PRIMARY KEY (store, metric, as_of)
);
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job TEXT NOT NULL,
    ts TEXT NOT NULL,
    status TEXT NOT NULL,
    detail TEXT
);
CREATE INDEX IF NOT EXISTS idx_runs_job_ts ON runs(job, ts);
"""


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript(SCHEMA)
    return conn


def write_kpi(store: str, metric: str, value: float, as_of: str, period: str = "", source: str = "") -> None:
    conn = _connect()
    with conn:
        conn.execute(
            "INSERT INTO kpis (store, metric, value, as_of, period, source) VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(store, metric, as_of) DO UPDATE SET value=excluded.value, period=excluded.period, source=excluded.source",
            (store, metric, value, as_of, period, source),
        )
    conn.close()


def write_kpis_bulk(rows: list[tuple]) -> None:
    """rows: [(store, metric, value, as_of, period, source), ...]."""
    conn = _connect()
    with conn:
        conn.executemany(
            "INSERT INTO kpis (store, metric, value, as_of, period, source) VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(store, metric, as_of) DO UPDATE SET value=excluded.value, period=excluded.period, source=excluded.source",
            rows,
        )
    conn.close()


def write_run(job: str, ts: str, status: str, detail: str = "") -> None:
    conn = _connect()
    with conn:
        conn.execute("INSERT INTO runs (job, ts, status, detail) VALUES (?, ?, ?, ?)", (job, ts, status, detail))
    conn.close()
    # Every job calls write_run() via its write_heartbeat(), so this is the
    # one place that guarantees latest.json reflects ALL jobs' current
    # state, not just whichever job last called build_latest_json()
    # explicitly for its own KPI write (found 2026-07-26: the dashboard
    # only showed job_store_rankings in Job Health because job_aged_inventory
    # was the last to regenerate the export, and it doesn't know about the
    # other 5 jobs' runs at the moment it writes).
    build_latest_json()


def latest_kpis() -> dict:
    """Returns {store: {metric: {'value', 'as_of', 'period', 'source'}}} using
    each store+metric's most recent as_of row."""
    conn = _connect()
    rows = conn.execute(
        "SELECT k.store, k.metric, k.value, k.as_of, k.period, k.source FROM kpis k "
        "INNER JOIN (SELECT store, metric, MAX(as_of) AS max_as_of FROM kpis GROUP BY store, metric) latest "
        "ON k.store = latest.store AND k.metric = latest.metric AND k.as_of = latest.max_as_of"
    ).fetchall()
    conn.close()
    out: dict = {}
    for store, metric, value, as_of, period, source in rows:
        out.setdefault(store, {})[metric] = {"value": value, "as_of": as_of, "period": period, "source": source}
    return out


def latest_run_per_job() -> dict:
    """Returns {job: {'ts', 'status', 'detail'}} — the most recent run row per job."""
    conn = _connect()
    rows = conn.execute(
        "SELECT r.job, r.ts, r.status, r.detail FROM runs r "
        "INNER JOIN (SELECT job, MAX(ts) AS max_ts FROM runs GROUP BY job) latest "
        "ON r.job = latest.job AND r.ts = latest.max_ts"
    ).fetchall()
    conn.close()
    return {job: {"ts": ts, "status": status, "detail": detail} for job, ts, status, detail in rows}


def build_latest_json() -> dict:
    """Assembles and writes data/latest.json — the single artifact the
    Command Center KPI page and publish_dashboard.py both read, so neither
    needs direct DB access."""
    from datetime import datetime

    payload = {
        "generated_at": datetime.now().isoformat(),
        "kpis": latest_kpis(),
        "runs": latest_run_per_job(),
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_JSON_PATH.write_text(json.dumps(payload, indent=2))
    return payload
