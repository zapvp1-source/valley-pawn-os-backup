#!/usr/bin/env python3
"""
job_aged_inventory.py — VP Ops Engine Job B (BUILD_SPEC.md §4).

Reads the 5 per-store aged-inventory-summary CSVs, computes Jewelry vs Gen
Merch aged-over-1-year at cost, and posts the locked format (per Joshua's
global CLAUDE.md standing rules) to #aged-inventory-review.

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

JOB_NAME = "job_aged_inventory"
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

    date_str = bravo.latest_complete_date("aged-inventory-summary.csv")
    if not date_str:
        common.log.error("No aged-inventory-summary.csv files found in output/ at all.")
        write_heartbeat("fail", "no aged-inventory-summary files found")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"), dry_run=(mode != "live"))
        return 2

    files = bravo.locate_store_files(date_str, "aged-inventory-summary.csv")
    missing = bravo.missing_stores(files)
    if missing:
        common.log.error(f"Missing/undersized aged-inventory files for {date_str}: {missing}")
        write_heartbeat("fail", f"missing stores for {date_str}: {','.join(missing)}")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"), dry_run=(mode != "live"))
        return 2

    data = {}
    for store_code, path in files.items():
        try:
            data[store_code] = formats.extract_aged_inventory_metrics(path)
        except Exception as e:
            common.log.error(f"Failed to parse {path}: {e}")
            write_heartbeat("fail", f"parse error on {store_code}: {e}")
            common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"), dry_run=(mode != "live"))
            return 2

    kpi_rows = []
    for store_code, d in data.items():
        total_aged = d["jewelry_aged"] + d["genmerch_aged"]
        kpi_rows.extend([
            (store_code, "Aged Jewelry", d["jewelry_aged"], date_str, "as-of", "job_aged_inventory"),
            (store_code, "Aged Gen Merch", d["genmerch_aged"], date_str, "as-of", "job_aged_inventory"),
            (store_code, "Aged Total", total_aged, date_str, "as-of", "job_aged_inventory"),
            (store_code, "Serialized Subtotal Cost", d["subtotal_cost"], date_str, "as-of", "job_aged_inventory"),
        ])
    store.write_kpis_bulk(kpi_rows)
    store.build_latest_json()

    message = formats.render_aged_inventory(data, date_str)

    if mode == "dry-run":
        print(message)
        write_heartbeat("ok", f"dry-run rendered for {date_str}")
        return 0

    channel = common.CHANNELS["vp-ops-shadow"] if mode == "shadow" else common.CHANNELS["aged-inventory-review"]
    ts = common.slack_post(channel, message, dry_run=False)
    if not ts:
        common.log.error("Failed to post message.")
        write_heartbeat("fail", "slack post failed")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"))
        return 2
    write_heartbeat("ok", f"posted for {date_str} to {channel}")
    common.log.info(f"Posted aged inventory review for {date_str} to {channel}.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True, help="render only, no Slack post (default)")
    parser.add_argument("--shadow", action="store_true", help="post to #vp-ops-shadow instead of production")
    parser.add_argument("--live", action="store_true", help="post to production #aged-inventory-review")
    args = parser.parse_args()

    mode = "live" if args.live else ("shadow" if args.shadow else "dry-run")
    try:
        sys.exit(run(mode))
    except Exception as e:
        common.report_crash(JOB_NAME, e, dry_run=(mode != "live"))
        sys.exit(1)
