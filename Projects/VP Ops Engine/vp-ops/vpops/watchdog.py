"""
watchdog.py — Job G (BUILD_SPEC.md §4). Heartbeat-based miss detection.

Each Phase-1 job writes data/heartbeats/<job>.json on every run (success or
fail) via its own write_heartbeat() call. This module defines the expected
cadence per job and flags one that hasn't reported within its window.

Per Hard Rule #3: exactly ONE plain-language DM to Joshua per missed job,
no technical detail in the DM (that goes to the log only).
"""

from __future__ import annotations
import json
from datetime import datetime, timedelta
from pathlib import Path

HEARTBEAT_DIR = Path(__file__).resolve().parent.parent / "data" / "heartbeats"

# Expected max age before a job's heartbeat is considered "missed".
# Generous windows (job's own cadence + slack) to avoid false alarms from
# normal run-time variance; tightened once real schedules are proven.
EXPECTED_JOBS = {
    "job_store_rankings": timedelta(days=8),       # weekly Monday
    "job_aged_inventory": timedelta(days=8),
    "job_employee_rankings": timedelta(days=8),
    "job_loan_layaway_review": timedelta(days=8),
}


def check_heartbeats(now: datetime | None = None) -> list[dict]:
    """Returns a list of {job, reason, last_seen} for any job that's missing
    a heartbeat entirely, stale beyond its window, or whose last run failed."""
    now = now or datetime.now()
    problems = []
    for job, window in EXPECTED_JOBS.items():
        path = HEARTBEAT_DIR / f"{job}.json"
        if not path.exists():
            problems.append({"job": job, "reason": "no heartbeat file found (never run?)", "last_seen": None})
            continue
        try:
            data = json.loads(path.read_text())
            ts = datetime.fromisoformat(data["ts"])
            status = data.get("status")
        except Exception as e:
            problems.append({"job": job, "reason": f"heartbeat file unreadable: {e}", "last_seen": None})
            continue

        age = now - ts
        if age > window:
            problems.append({"job": job, "reason": f"last heartbeat {age.days}d old (expected within {window.days}d)", "last_seen": ts.isoformat()})
        elif status == "fail":
            problems.append({"job": job, "reason": f"last run reported failure at {ts.isoformat()}", "last_seen": ts.isoformat()})
        # "partial" status (Job D, one of two sub-reports failed) also warrants a look,
        # but isn't a full miss — surfaced in the log, not a separate DM category.
    return problems
