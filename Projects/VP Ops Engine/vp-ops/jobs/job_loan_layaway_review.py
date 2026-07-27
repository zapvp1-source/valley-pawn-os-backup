#!/usr/bin/env python3
"""
job_loan_layaway_review.py — VP Ops Engine Job D (BUILD_SPEC.md §4).

Posts two independent reports:
  - Past-Due Loan Review -> #loan-review (75-day rule, 5% cap)
  - Layaway Review -> #layaway-review (overdue/past-due/contacted/30d/locate)

Loan-balance denominators always use the freshest available EOM data (not
whatever date the past-due CSV happens to be, which can lag it slightly).

Shadow mode (BUILD_SPEC.md §8): defaults to --dry-run. --shadow posts both
to #vp-ops-shadow. --live posts to their real production channels.
"""

from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vpops import bravo, common, formats, store

JOB_NAME = "job_loan_layaway_review"
HEARTBEAT_DIR = Path(__file__).resolve().parent.parent / "data" / "heartbeats"


def write_heartbeat(status: str, detail: str) -> None:
    HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().isoformat()
    payload = {"ts": ts, "status": status, "detail": detail}
    (HEARTBEAT_DIR / f"{JOB_NAME}.json").write_text(json.dumps(payload))
    store.write_run(JOB_NAME, ts, status, detail)


def build_loan_review():
    """Returns (rendered_message, date_str, past_due, loan_balances) or None."""
    date_str = bravo.latest_enddate("loans-75-days-past-due.csv")
    if not date_str:
        return None
    past_due_files = bravo.locate_store_files(date_str, "loans-75-days-past-due.csv")
    if bravo.missing_stores(past_due_files):
        return None

    eom_date = bravo.latest_enddate("end-of-month.xlsx")
    if not eom_date:
        return None
    eom_files = bravo.locate_store_files(eom_date, "end-of-month.xlsx")
    if bravo.missing_stores(eom_files):
        return None

    past_due = {s: formats.extract_loan_past_due(p) for s, p in past_due_files.items()}
    eom_data = {s: formats.extract_store_eom_metrics(p) for s, p in eom_files.items()}
    loan_balances = {s: eom_data[s]["Loan Balance"] for s in eom_data}
    msg = formats.render_past_due_loan_review(past_due, loan_balances, date_str)
    return msg, date_str, past_due, loan_balances


def build_layaway_review():
    """Returns (rendered_message, date_str, data) or None."""
    date_str = bravo.latest_enddate("layaways.csv")
    if not date_str:
        return None
    files = bravo.locate_store_files(date_str, "layaways.csv")
    if bravo.missing_stores(files):
        return None
    data = {s: formats.extract_layaways(p) for s, p in files.items()}
    y, m, d = date_str.split("-")
    display_date = f"{int(m)}/{int(d)}/{y}"
    msg = formats.render_layaway_review(data, display_date)
    return msg, date_str, data


def write_loan_layaway_kpis(loan_result, layaway_result) -> None:
    rows = []
    if loan_result:
        _, date_str, past_due, loan_balances = loan_result
        for s, pd in past_due.items():
            pct = (pd["dollar_sum"] / loan_balances[s] * 100) if loan_balances.get(s) else 0.0
            rows.extend([
                (s, "PastDue75 Items", pd["count"], date_str, "as-of", "job_loan_layaway_review"),
                (s, "PastDue75 Dollars", pd["dollar_sum"], date_str, "as-of", "job_loan_layaway_review"),
                (s, "PastDue75 Pct", pct, date_str, "as-of", "job_loan_layaway_review"),
            ])
    if layaway_result:
        _, date_str, data = layaway_result
        for s, d in data.items():
            for key in ("overdue", "past_pmt_due", "contacted_no_activity", "no_pmt_30d", "locate"):
                rows.append((s, f"Layaway {key}", d[key], date_str, "as-of", "job_loan_layaway_review"))
    if rows:
        store.write_kpis_bulk(rows)


def run(mode: str) -> int:
    log_path = common.setup_logging(JOB_NAME)
    common.log.info(f"Starting {JOB_NAME} (mode={mode}); log at {log_path}")

    loan_result = build_loan_review()
    layaway_result = build_layaway_review()

    if loan_result is None and layaway_result is None:
        common.log.error("Both loan and layaway data unavailable/incomplete.")
        write_heartbeat("fail", "no usable loan or layaway data")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"), dry_run=(mode != "live"))
        return 2

    write_loan_layaway_kpis(loan_result, layaway_result)

    if mode == "dry-run":
        if loan_result:
            print("=== LOAN REVIEW ===")
            print(loan_result[0])
        else:
            print("=== LOAN REVIEW: unavailable ===")
        print()
        if layaway_result:
            print("=== LAYAWAY REVIEW ===")
            print(layaway_result[0])
        else:
            print("=== LAYAWAY REVIEW: unavailable ===")
        write_heartbeat("ok" if (loan_result and layaway_result) else "partial", "dry-run rendered")
        return 0

    ok = True
    if loan_result:
        channel = common.CHANNELS["vp-ops-shadow"] if mode == "shadow" else common.CHANNELS["loan-review"]
        if not common.slack_post(channel, loan_result[0], dry_run=False):
            common.log.error("Failed to post loan review.")
            ok = False
    else:
        common.log.error("Loan review data unavailable — skipped (never post partial).")
        ok = False

    if layaway_result:
        channel = common.CHANNELS["vp-ops-shadow"] if mode == "shadow" else common.CHANNELS["layaway-review"]
        if not common.slack_post(channel, layaway_result[0], dry_run=False):
            common.log.error("Failed to post layaway review.")
            ok = False
    else:
        common.log.error("Layaway review data unavailable — skipped (never post partial).")
        ok = False

    if not ok:
        write_heartbeat("partial" if (loan_result or layaway_result) else "fail", "one or both reports failed/unavailable")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"))
        return 2

    write_heartbeat("ok", f"posted loan review ({loan_result[1]}) and layaway review ({layaway_result[1]})")
    common.log.info("Posted both loan and layaway reviews.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True, help="render only, no Slack post (default)")
    parser.add_argument("--shadow", action="store_true", help="post both to #vp-ops-shadow instead of production")
    parser.add_argument("--live", action="store_true", help="post to production #loan-review and #layaway-review")
    args = parser.parse_args()

    mode = "live" if args.live else ("shadow" if args.shadow else "dry-run")
    try:
        sys.exit(run(mode))
    except Exception as e:
        common.report_crash(JOB_NAME, e, dry_run=(mode != "live"))
        sys.exit(1)
