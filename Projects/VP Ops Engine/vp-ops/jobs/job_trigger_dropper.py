#!/usr/bin/env python3
"""
job_trigger_dropper.py — VP Ops Engine Job E (BUILD_SPEC.md §4).

Drops ONE combined trigger for the 5 cells Jobs A-D need (end-of-month,
aged-inventory-summary, employee-activity, loans-75-days-past-due,
layaways) x 5 stores, then polls output/ until they land. Duplicate-pull
guard: skips any cell already fresh for today (BUILD_SPEC.md §4 "Job E
rules" — coexists with monday-bravo-combined-run, whichever runs first
produces the files, the other reuses them; NEVER edit that existing task).

Runs at 05:30 ET on Mondays in production (before combined_run's ~05:38).
Safe to run ad hoc any day/time too (e.g. to refresh stale data before a
manual golden-test or shadow-mode verification) — it just pulls whatever's
not already fresh for today.
"""

from __future__ import annotations
import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vpops import bravo, common, store

JOB_NAME = "job_trigger_dropper"
HEARTBEAT_DIR = Path(__file__).resolve().parent.parent / "data" / "heartbeats"

# (cell_suffix_without_extension, date_kind) — date_kind picks how the
# "date" field is built. "mtd" = FIRST..YESTERDAY (EOM-style cells refuse
# today/future, per the existing daily_run.sh's own comment). "today" =
# single-day snapshot cells.
CELLS = [
    ("end-of-month", "xlsx", "mtd"),
    ("aged-inventory-summary", "csv", "today"),
    ("employee-activity", "csv", "mtd"),
    ("loans-75-days-past-due", "csv", "today"),
    ("layaways", "csv", "today"),
    ("fpd-cohort", "csv", "today"),  # Job H (BUILD_SPEC_WAVE2.md §2) — our own cell to add
]


def write_heartbeat(status: str, detail: str) -> None:
    HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().isoformat()
    payload = {"ts": ts, "status": status, "detail": detail}
    (HEARTBEAT_DIR / f"{JOB_NAME}.json").write_text(json.dumps(payload))
    store.write_run(JOB_NAME, ts, status, detail)


def run(mode: str) -> int:
    log_path = common.setup_logging(JOB_NAME)
    common.log.info(f"Starting {JOB_NAME} (mode={mode}); log at {log_path}")

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    first_of_month = today.replace(day=1)
    today_s = today.strftime("%Y-%m-%d")
    yesterday_s = yesterday.strftime("%Y-%m-%d")
    first_s = first_of_month.strftime("%Y-%m-%d")

    # Duplicate-pull guard: figure out which cells are already fresh for today.
    # employee-activity is checked by mtime (file exists, modified since
    # midnight today), not date-prefix -- its AHK handler names output by
    # the raw requested range, which never matches a plain-date lookup
    # (see wait_for_cell_by_mtime's docstring; this guard had the same gap).
    midnight_today = datetime.combine(today.date(), datetime.min.time()).timestamp()
    needed = []
    already_fresh = []
    target_date_for = {}
    for cell, ext, date_kind in CELLS:
        target_date = yesterday_s if date_kind == "mtd" else today_s
        target_date_for[cell] = target_date
        if cell == "employee-activity":
            files = bravo.latest_store_files_by_mtime(f"{cell}.{ext}")
            missing = [s for s in bravo.STORES if files.get(s) is None or files[s].stat().st_mtime < midnight_today]
        else:
            files = bravo.locate_store_files(target_date, f"{cell}.{ext}")
            missing = bravo.missing_stores(files)
        if missing:
            needed.append((cell, ext, date_kind, missing))
        else:
            already_fresh.append(cell)

    if already_fresh:
        common.log.info(f"Already fresh for today, skipping: {already_fresh}")

    if not needed:
        common.log.info("All 5 cells already fresh for today — nothing to pull.")
        write_heartbeat("ok", "all cells already fresh, no trigger dropped")
        return 0

    common.log.info(f"Need to pull: {[c for c, _, _, _ in needed]}")

    if mode == "dry-run":
        for cell, ext, date_kind, missing in needed:
            date_field = f"{first_s}..{yesterday_s}" if date_kind == "mtd" else today_s
            print(f"[DRY-RUN] Would request cell={cell} stores={missing} date={date_field}")
        write_heartbeat("ok", f"dry-run — would pull {[c for c, _, _, _ in needed]}")
        return 0

    common.log.info("Running Bravo health check...")
    healthy = bravo.ensure_healthy("CUL", timeout_s=900)
    if not healthy:
        # Do NOT hard-block here. bravo_health_gate.sh has a confirmed,
        # reproducible false-negative: its own log shows successful
        # recovery ("recover result='OK CUL'", twice) immediately before
        # it still reports overall FAIL, because it treats dfsvc.exe's
        # mere presence as "ClickOnce update in flight" even when the
        # update already finished (seen 2026-07-26 19:40, 2026-07-27 05:3x
        # and 07:37 -- three times, not a fluke). job_daily_loan_inv_text's
        # native daily_run.sh already gets this right: it doesn't hard-block
        # on this verdict either, it just attempts the pull and lets the
        # per-cell result speak for itself. Matching that proven pattern
        # here instead of trusting a script known to cry wolf.
        common.log.warning("Health gate reported unhealthy, but proceeding anyway (see comment) -- letting the actual pull attempt be the real signal.")

    trigger_id = f"vpops-trigger-dropper-{today.strftime('%Y-%m-%dT%H-%M-%S')}"
    reports = []
    for cell, ext, date_kind, missing in needed:
        date_field = f"{first_s}..{yesterday_s}" if date_kind == "mtd" else today_s
        reports.append({"name": cell, "stores": missing, "date": date_field})

    drop_ts = time.time()
    path = bravo.drop_trigger(trigger_id, reports)
    common.log.info(f"Dropped trigger {path} with {len(reports)} report(s).")

    still_missing = {}
    for cell, ext, date_kind, missing in needed:
        if cell == "employee-activity":
            # This cell's AHK handler names output by the raw date RANGE, not
            # a single end-date -- date-prefix polling can never match it.
            # See wait_for_cell_by_mtime()'s docstring (found 2026-07-27:
            # this exact gap left the job stuck for the data's own 30-min
            # timeout even after the file had already landed).
            remaining = bravo.wait_for_cell_by_mtime(f"{cell}.{ext}", since_ts=drop_ts, stores=missing, timeout_s=1800, poll_s=20)
        else:
            remaining = bravo.wait_for_cell(target_date_for[cell], f"{cell}.{ext}", stores=missing, timeout_s=1800, poll_s=20)
        if remaining:
            still_missing[cell] = remaining
        else:
            common.log.info(f"Cell {cell} complete for {missing}.")

    if still_missing:
        common.log.error(f"Timed out waiting for: {still_missing}")
        write_heartbeat("partial", f"missing after timeout: {still_missing}")
        common.missed_run_dm(JOB_NAME, today_s, dry_run=False)
        return 2

    write_heartbeat("ok", f"pulled {[c for c, _, _, _ in needed]} for {today_s}")
    common.log.info("All requested cells landed successfully.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True, help="show what would be pulled, don't drop a trigger (default)")
    parser.add_argument("--live", action="store_true", help="actually run the health check, drop the trigger, and wait for results")
    args = parser.parse_args()

    mode = "live" if args.live else "dry-run"
    try:
        sys.exit(run(mode))
    except Exception as e:
        common.report_crash(JOB_NAME, e, dry_run=(mode != "live"))
        sys.exit(1)
