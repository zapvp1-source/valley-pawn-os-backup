#!/usr/bin/env python3
"""
job_fpd_ranking.py — VP Ops Engine Job H (BUILD_SPEC_WAVE2.md §2).

Reads the 5 per-store fpd-cohort CSVs, appends new tickets to the shared
archive (dedupe by ticket_number, Wave2 Hard Rule #9), computes the store
ranking + this-week/chronic category breakdowns, and posts to
#first-payment-default.

Unlike Jobs A-D, this job posts PARTIAL results if some stores' pipeline
cells failed (per spec: "DATA ONLY in the channel... if a store's cell
failed, exactly one trailing line") -- only skips entirely if ALL 5 failed.

Dup-guard: scans the last ~20 channel messages for today's report title
before posting, matching the legacy monday-bravo-combined-compile's own
guard (added there 2026-07-22 after real duplicate posts) -- belt and
suspenders even though the legacy path is confirmed dormant.

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

JOB_NAME = "job_fpd_ranking"
HEARTBEAT_DIR = Path(__file__).resolve().parent.parent / "data" / "heartbeats"


def write_heartbeat(status: str, detail: str) -> None:
    HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().isoformat()
    payload = {"ts": ts, "status": status, "detail": detail}
    (HEARTBEAT_DIR / f"{JOB_NAME}.json").write_text(json.dumps(payload))
    store.write_run(JOB_NAME, ts, status, detail)


def already_posted_today(channel: str, date_str: str) -> bool:
    """Dup-guard matching the legacy path's own (2026-07-22-added) behavior:
    scan recent channel history for today's report title before posting."""
    midnight = datetime.combine(datetime.now().date(), datetime.min.time()).timestamp()
    messages = common.slack_read_history(channel, midnight)
    title = f"Weekly First-Payment-Default Ranking — {date_str}"
    return any(title in m.get("text", "") for m in messages)


def run(mode: str) -> int:
    log_path = common.setup_logging(JOB_NAME)
    common.log.info(f"Starting {JOB_NAME} (mode={mode}); log at {log_path}")

    date_str = bravo.latest_complete_date("fpd-cohort.csv")
    if not date_str:
        # latest_complete_date requires ALL 5; fall back to whatever's
        # partially there today, since this job allows partial posting.
        any_date = bravo.latest_enddate("fpd-cohort.csv")
        if not any_date:
            common.log.error("No fpd-cohort.csv files found in output/ at all.")
            write_heartbeat("fail", "no fpd-cohort files found")
            common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"), dry_run=(mode != "live"))
            return 2
        date_str = any_date

    files = bravo.locate_store_files(date_str, "fpd-cohort.csv")
    failed_stores = bravo.missing_stores(files)
    succeeded_stores = [s for s in bravo.STORES if s not in failed_stores]

    if not succeeded_stores:
        common.log.error(f"All 5 stores' fpd-cohort cells failed for {date_str}.")
        write_heartbeat("fail", f"all stores missing for {date_str}")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"), dry_run=(mode != "live"))
        return 2

    cohorts = {}
    for s in succeeded_stores:
        try:
            cohorts[s] = formats.extract_fpd_cohort(files[s])
        except Exception as e:
            common.log.error(f"Failed to parse {files[s]}: {e}")
            failed_stores.append(s)
            succeeded_stores.remove(s)

    if not succeeded_stores:
        write_heartbeat("fail", "all stores failed to parse")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"), dry_run=(mode != "live"))
        return 2

    appended = bravo.append_fpd_archive(date_str, cohorts)
    common.log.info(f"Archive: appended {appended} new ticket(s) (deduped by ticket_number).")

    archive = bravo.read_fpd_archive()
    message = formats.render_fpd_ranking(cohorts, date_str, archive, failed_stores=failed_stores)

    kpi_rows = []
    for s in succeeded_stores:
        count = len(cohorts[s])
        dollars = sum(t["loan_amount"] for t in cohorts[s])
        kpi_rows.append((s, "FPD Count", count, date_str, "weekly", "job_fpd_ranking"))
        kpi_rows.append((s, "FPD Exposure", dollars, date_str, "weekly", "job_fpd_ranking"))
    store.write_kpis_bulk(kpi_rows)

    if mode == "dry-run":
        print(message)
        write_heartbeat("ok" if not failed_stores else "partial", f"dry-run rendered for {date_str}")
        return 0

    channel = common.CHANNELS["vp-ops-shadow"] if mode == "shadow" else common.CHANNELS["first-payment-default"]

    if mode == "live" and already_posted_today(channel, date_str):
        common.log.info(f"Already posted today's report to {channel} -- skipping (dup-guard).")
        write_heartbeat("ok", f"skipped, already posted for {date_str}")
        return 0

    ts = common.slack_post(channel, message, dry_run=False)
    if not ts:
        common.log.error("Failed to post message.")
        write_heartbeat("fail", "slack post failed")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"))
        return 2

    status = "ok" if not failed_stores else "partial"
    write_heartbeat(status, f"posted for {date_str} to {channel}" + (f" (missing: {failed_stores})" if failed_stores else ""))
    common.log.info(f"Posted FPD ranking for {date_str} to {channel}.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True, help="render only, no Slack post (default)")
    parser.add_argument("--shadow", action="store_true", help="post to #vp-ops-shadow instead of production")
    parser.add_argument("--live", action="store_true", help="post to production #first-payment-default")
    args = parser.parse_args()

    mode = "live" if args.live else ("shadow" if args.shadow else "dry-run")
    try:
        sys.exit(run(mode))
    except Exception as e:
        common.report_crash(JOB_NAME, e, dry_run=(mode != "live"))
        sys.exit(1)
