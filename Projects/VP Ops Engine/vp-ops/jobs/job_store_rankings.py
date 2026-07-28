#!/usr/bin/env python3
"""
job_store_rankings.py — VP Ops Engine Job A (BUILD_SPEC.md §4).

Reads the 5 per-store End-of-Month XLSX files already produced by the Bravo
Data Extraction pipeline, computes the 8-category store rankings, and posts
the locked two-message "Full Category Rankings" format to #store-performance.

Shadow mode (BUILD_SPEC.md §8): pass --dry-run to render without posting, or
--shadow to post to #vp-ops-shadow instead of production. Defaults to
--dry-run for safety — cutover to production requires an explicit --live.
"""

from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vpops import bravo, common, formats, store

JOB_NAME = "job_store_rankings"
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

    enddate = bravo.latest_complete_date("end-of-month.xlsx")
    if not enddate:
        common.log.error("No end-of-month.xlsx files found in output/ at all.")
        write_heartbeat("fail", "no end-of-month files found")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"), dry_run=(mode != "live"))
        return 2

    files = bravo.locate_store_files(enddate, "end-of-month.xlsx")
    missing = bravo.missing_stores(files)
    if missing:
        common.log.error(f"Missing/undersized EOM files for {enddate}: {missing}")
        write_heartbeat("fail", f"missing stores for {enddate}: {','.join(missing)}")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"), dry_run=(mode != "live"))
        return 2

    data = {}
    for store_code, path in files.items():
        try:
            data[store_code] = formats.extract_store_eom_metrics(path)
        except Exception as e:
            common.log.error(f"Failed to parse {path}: {e}")
            write_heartbeat("fail", f"parse error on {store_code}: {e}")
            common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"), dry_run=(mode != "live"))
            return 2

    kpi_rows = [
        (store_code, metric, value, enddate, "MTD", "job_store_rankings")
        for store_code, metrics in data.items()
        for metric, value in metrics.items()
    ]
    store.write_kpis_bulk(kpi_rows)
    store.build_latest_json()

    msg1, msg2 = formats.render_store_rankings(data, enddate)

    if mode == "dry-run":
        print("=== MSG1 (parent) ===")
        print(msg1)
        print("\n=== MSG2 (thread reply) ===")
        print(msg2)
        write_heartbeat("ok", f"dry-run rendered for {enddate}")
        return 0

    channel = common.CHANNELS["vp-ops-shadow"] if mode == "shadow" else common.CHANNELS["store-performance"]
    ts = common.slack_post(channel, msg1, dry_run=False)
    if not ts:
        common.log.error("Failed to post parent message.")
        write_heartbeat("fail", "slack post (parent) failed")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"))
        return 2
    common.slack_post(channel, msg2, dry_run=False, thread_ts=ts)
    write_heartbeat("ok", f"posted for {enddate} to {channel}")
    common.log.info(f"Posted store rankings for {enddate} to {channel}.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True, help="render only, no Slack post (default)")
    parser.add_argument("--shadow", action="store_true", help="post to #vp-ops-shadow instead of production")
    parser.add_argument("--live", action="store_true", help="post to production #store-performance")
    args = parser.parse_args()

    mode = "live" if args.live else ("shadow" if args.shadow else "dry-run")
    try:
        sys.exit(run(mode))
    except Exception as e:
        common.report_crash(JOB_NAME, e, dry_run=(mode != "live"))
        sys.exit(1)
