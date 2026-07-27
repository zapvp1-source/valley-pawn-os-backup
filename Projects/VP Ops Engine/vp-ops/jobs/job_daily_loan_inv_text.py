#!/usr/bin/env python3
"""
job_daily_loan_inv_text.py — VP Ops Engine Job F (BUILD_SPEC.md §4).

Thin wrapper, per spec: "verify + schedule, don't rewrite." The actual pull
(Bravo EOM trigger + poll), compute (compute.py), and send (send_imsg.
applescript to Joshua + Preston) all already exist and work natively at
Documents/Claude/Scheduled/daily-loan-inventory-text/. This job's only
value-add is being launchd-schedulable from this repo and writing a
heartbeat so job_watchdog.py can see it.

--dry-run (default): does NOT invoke the native script (which sends real
iMessages) — just reports whether it WOULD run and what the last known
status was.
--live: actually runs native_run.sh (real Bravo pull + real texts sent).
"""

from __future__ import annotations
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vpops import common, store

JOB_NAME = "job_daily_loan_inv_text"
HEARTBEAT_DIR = Path(__file__).resolve().parent.parent / "data" / "heartbeats"
NATIVE_DIR = Path("/Users/joshuadavis/Documents/Claude/Scheduled/daily-loan-inventory-text")
NATIVE_RUN = NATIVE_DIR / "native_run.sh"


def write_heartbeat(status: str, detail: str) -> None:
    HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().isoformat()
    payload = {"ts": ts, "status": status, "detail": detail}
    (HEARTBEAT_DIR / f"{JOB_NAME}.json").write_text(json.dumps(payload))
    store.write_run(JOB_NAME, ts, status, detail)


def run(mode: str) -> int:
    log_path = common.setup_logging(JOB_NAME)
    common.log.info(f"Starting {JOB_NAME} (mode={mode}); log at {log_path}")

    if not NATIVE_RUN.exists():
        common.log.error(f"Native script missing: {NATIVE_RUN}")
        write_heartbeat("fail", "native_run.sh not found")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"), dry_run=(mode != "live"))
        return 2

    if mode == "dry-run":
        last_status = (NATIVE_DIR / "latest_status.txt").read_text().strip() if (NATIVE_DIR / "latest_status.txt").exists() else "unknown"
        last_message = (NATIVE_DIR / "latest_message.txt").read_text() if (NATIVE_DIR / "latest_message.txt").exists() else ""
        print(f"[DRY-RUN] Would run: {NATIVE_RUN}")
        print(f"[DRY-RUN] Last known status: {last_status}")
        print(f"[DRY-RUN] Last known message:\n{last_message}")
        write_heartbeat("ok", "dry-run — did not invoke native script")
        return 0

    common.log.info(f"Invoking {NATIVE_RUN} (real Bravo pull + real iMessage send)...")
    result = subprocess.run(["/bin/bash", str(NATIVE_RUN)], capture_output=True, text=True, timeout=2400)
    common.log.info(f"native_run.sh exit code: {result.returncode}")
    if result.stdout:
        common.log.info(f"stdout: {result.stdout[-2000:]}")
    if result.stderr:
        common.log.info(f"stderr: {result.stderr[-2000:]}")

    status = (NATIVE_DIR / "latest_status.txt").read_text().strip() if (NATIVE_DIR / "latest_status.txt").exists() else "unknown"
    if status == "OK":
        write_heartbeat("ok", "native script ran, status OK")
        common.log.info("Job F completed successfully.")
        return 0
    else:
        write_heartbeat("fail", f"native script status: {status}")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"))
        return 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True, help="report only, don't invoke native script (default)")
    parser.add_argument("--live", action="store_true", help="actually run native_run.sh — real Bravo pull + real texts sent")
    args = parser.parse_args()

    mode = "live" if args.live else "dry-run"
    try:
        sys.exit(run(mode))
    except Exception as e:
        common.report_crash(JOB_NAME, e, dry_run=(mode != "live"))
        sys.exit(1)
