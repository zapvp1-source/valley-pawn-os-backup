#!/usr/bin/env python3
"""
job_employee_rankings.py — VP Ops Engine Job C (BUILD_SPEC.md §4).

Reads the 5 per-store employee-activity CSVs (note: filename date-stamped
by month-start but regenerated in place through the month — the real
period end lives in the CSV's own "Reporting Dates" row), aggregates each
employee's Retail Sales Excluding Fees across every store they work at,
and posts the locked ranking to #employee-performance. Excludes Preston
Peters from the ranked list (his revenue still counts in Company Total),
SYSTEM rows, and $0 employees.

Shadow mode (BUILD_SPEC.md §8): defaults to --dry-run. --shadow posts to
#vp-ops-shadow. --live posts to production.
"""

from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vpops import bravo, common, formats, store

JOB_NAME = "job_employee_rankings"
HEARTBEAT_DIR = Path(__file__).resolve().parent.parent / "data" / "heartbeats"


def write_heartbeat(status: str, detail: str) -> None:
    HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().isoformat()
    payload = {"ts": ts, "status": status, "detail": detail}
    (HEARTBEAT_DIR / f"{JOB_NAME}.json").write_text(json.dumps(payload))
    store.write_run(JOB_NAME, ts, status, detail)


def run(mode: str) -> int:
    log_path = common.setup_logging(JOB_NAME)
    common.log.info(f"Starting {JOB_NAME} (mode={mode}); log at {log_path}")

    # mtime-based, not filename-date-based: employee-activity's AHK handler
    # names its output by the raw requested date range (e.g.
    # '2026-07-01..2026-07-25_CUL_employee-activity.csv'), unlike most other
    # cells which use a single end-date prefix. See bravo.py's
    # latest_store_files_by_mtime() docstring for the full story.
    files = bravo.latest_store_files_by_mtime("employee-activity.csv")
    missing = bravo.missing_stores(files)
    if missing:
        common.log.error(f"Missing/undersized employee-activity files: {missing}")
        write_heartbeat("fail", f"missing stores: {','.join(missing)}")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"), dry_run=(mode != "live"))
        return 2
    filename_date = "current"

    store_data = {}
    for store_code, path in files.items():
        try:
            store_data[store_code] = formats.extract_employee_activity(path)
        except Exception as e:
            common.log.error(f"Failed to parse {path}: {e}")
            write_heartbeat("fail", f"parse error on {store_code}: {e}")
            common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"), dry_run=(mode != "live"))
            return 2

    message = formats.render_employee_rankings(store_data)

    if mode == "dry-run":
        print(message)
        write_heartbeat("ok", f"dry-run rendered for {filename_date}")
        return 0

    channel = common.CHANNELS["vp-ops-shadow"] if mode == "shadow" else common.CHANNELS["employee-performance"]
    ts = common.slack_post(channel, message, dry_run=False)
    if not ts:
        common.log.error("Failed to post message.")
        write_heartbeat("fail", "slack post failed")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"))
        return 2
    write_heartbeat("ok", f"posted for {filename_date} to {channel}")
    common.log.info(f"Posted employee rankings for {filename_date} to {channel}.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True, help="render only, no Slack post (default)")
    parser.add_argument("--shadow", action="store_true", help="post to #vp-ops-shadow instead of production")
    parser.add_argument("--live", action="store_true", help="post to production #employee-performance")
    args = parser.parse_args()

    mode = "live" if args.live else ("shadow" if args.shadow else "dry-run")
    try:
        sys.exit(run(mode))
    except Exception as e:
        common.report_crash(JOB_NAME, e, dry_run=(mode != "live"))
        sys.exit(1)
