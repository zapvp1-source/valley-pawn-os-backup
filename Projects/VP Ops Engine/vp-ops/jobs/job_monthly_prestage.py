#!/usr/bin/env python3
"""
job_monthly_prestage.py — VP Ops Engine Job I prestage (BUILD_SPEC_WAVE2.md §3).

Runs the last day of the month (launchd fires 21:00 ET on days 28-31; exits
silently unless tomorrow is actually the 1st — same gate as the legacy
monthly-analytics-prestage/SKILL.md Step 0). Drops 6 sequential
`company-kpis` triggers, one per YoY window (same-month/YTD/T12M x
current/prior), waiting for and copying each result to a window-tagged
sidecar in data/monthly-analytics/{YYYY-MM}/ before dropping the next --
several windows share the same end-date, so the raw
output/{enddate}_ALL_company-kpis.xlsx file would otherwise be silently
overwritten before job_monthly_analytics.py ever reads it.
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

JOB_NAME = "job_monthly_prestage"
HEARTBEAT_DIR = Path(__file__).resolve().parent.parent / "data" / "heartbeats"

WINDOW_KEYS = [
    "same_month_current", "same_month_prior",
    "ytd_current", "ytd_prior",
    "t12m_current", "t12m_prior",
]


def write_heartbeat(status: str, detail: str) -> None:
    HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().isoformat()
    (HEARTBEAT_DIR / f"{JOB_NAME}.json").write_text(json.dumps({"ts": ts, "status": status, "detail": detail}))
    store.write_run(JOB_NAME, ts, status, detail)


def run(mode: str, force: bool = False) -> int:
    log_path = common.setup_logging(JOB_NAME)
    common.log.info(f"Starting {JOB_NAME} (mode={mode}); log at {log_path}")

    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    if tomorrow.day != 1 and not force:
        common.log.info("Not the last day of the month -- nothing to do (Step 0 gate).")
        write_heartbeat("ok", "skip, not last day of month")
        return 0

    report_month_start = today.replace(day=1)
    windows = bravo.compute_monthly_windows(report_month_start)
    month_key = report_month_start.strftime("%Y-%m")

    if mode == "dry-run":
        for wkey in WINDOW_KEYS:
            start, end = windows[wkey]
            print(f"[DRY-RUN] Would pull window={wkey} range={start}..{end}")
        if windows["t12m_prior_clamped"]:
            print(f"[DRY-RUN] {windows['t12m_prior_note']}")
        write_heartbeat("ok", f"dry-run for {month_key}")
        return 0

    common.log.info("Running Bravo health check...")
    healthy = bravo.ensure_healthy("CUL", timeout_s=900)
    if not healthy:
        common.log.warning("Health gate reported unhealthy, proceeding anyway (matches Job E's pattern).")

    landed, failed = [], []
    for wkey in WINDOW_KEYS:
        start, end = windows[wkey]
        date_field = f"{start}..{end}"
        ok = False
        for attempt in range(2):  # one retry, per legacy prestage Step 5
            trigger_id = f"vpops-monthly-prestage-{wkey}-{today.strftime('%Y-%m-%dT%H-%M-%S')}" + (f"-retry-{attempt}" if attempt else "")
            drop_ts = time.time()
            bravo.drop_trigger(trigger_id, [{"name": "company-kpis", "stores": ["ALL"], "date": date_field}])
            common.log.info(f"Dropped trigger for window={wkey} range={date_field} (attempt {attempt + 1}).")
            if bravo.wait_for_company_kpis(end, since_ts=drop_ts, timeout_s=720, poll_s=18):
                ok = True
                break
            common.log.warning(f"Window {wkey} did not land within timeout (attempt {attempt + 1}).")
        if not ok:
            failed.append(wkey)
            continue
        sidecar = bravo.copy_company_kpis_to_sidecar(end, wkey, month_key)
        if sidecar is None:
            failed.append(wkey)
            continue
        landed.append(wkey)
        common.log.info(f"Window {wkey} staged to {sidecar}.")

    if failed:
        common.log.error(f"Windows failed to stage: {failed}")
        write_heartbeat("partial" if landed else "fail", f"{month_key}: landed={landed} failed={failed}")
        common.missed_run_dm(JOB_NAME, month_key, dry_run=False)
        return 2 if landed else 1

    write_heartbeat("ok", f"{month_key}: all 6 windows staged")
    common.log.info(f"All 6 windows staged for {month_key}.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True, help="show what would be pulled, don't drop a trigger (default)")
    parser.add_argument("--live", action="store_true", help="actually run the health check, drop triggers, and wait for results")
    parser.add_argument("--force", action="store_true", help="run even if tomorrow isn't the 1st (for manual testing)")
    args = parser.parse_args()

    mode = "live" if args.live else "dry-run"
    try:
        sys.exit(run(mode, force=args.force))
    except Exception as e:
        common.report_crash(JOB_NAME, e, dry_run=(mode != "live"))
        sys.exit(1)
