#!/usr/bin/env python3
"""
job_watchdog.py — VP Ops Engine Job G (BUILD_SPEC.md §4).

Checks every Phase-1 job's heartbeat file. DMs Joshua ONE plain-language
line per missed/failed job (Hard Rule #3) — never posts to any channel,
never includes technical detail in the DM.

--dry-run (default): print what would be sent, don't actually DM.
--live: send the real DM(s) to Joshua.
"""

from __future__ import annotations
import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vpops import common, watchdog, store

JOB_NAME = "job_watchdog"


def run(mode: str) -> int:
    log_path = common.setup_logging(JOB_NAME)
    common.log.info(f"Starting {JOB_NAME} (mode={mode}); log at {log_path}")

    problems = watchdog.check_heartbeats()
    if not problems:
        common.log.info("All jobs healthy — no DM sent (silent on success, per design).")
        store.write_run(JOB_NAME, datetime.now().isoformat(), "ok", "all jobs healthy")
        return 0

    for p in problems:
        common.log.warning(f"Watchdog flag: {p['job']} — {p['reason']}")
        if mode == "dry-run":
            print(f'[DRY-RUN] Would DM Joshua: ⚠️ VP Ops job "{p["job"]}" did not complete — (diagnostic in log only: {p["reason"]})')
        else:
            common.missed_run_dm(p["job"], datetime.now().strftime("%Y-%m-%d"), dry_run=False)

    store.write_run(JOB_NAME, datetime.now().isoformat(), "flagged", f"{len(problems)} job(s) flagged: {[p['job'] for p in problems]}")
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True, help="print only, no real DM (default)")
    parser.add_argument("--live", action="store_true", help="send real DM(s) to Joshua for any missed job")
    args = parser.parse_args()

    mode = "live" if args.live else "dry-run"
    try:
        sys.exit(run(mode))
    except Exception as e:
        common.report_crash(JOB_NAME, e, dry_run=(mode != "live"))
        sys.exit(1)
