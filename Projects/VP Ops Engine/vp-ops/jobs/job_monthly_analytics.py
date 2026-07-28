#!/usr/bin/env python3
"""
job_monthly_analytics.py — VP Ops Engine Job I (BUILD_SPEC_WAVE2.md §3).

Runs the 1st of the month, 08:00 ET, reading the 6 window sidecars
job_monthly_prestage.py staged the night before (data/monthly-analytics/
{YYYY-MM}/{window_key}.xlsx). Computes 3 YoY views (Same Month / YTD / T12M)
and posts to #company-performance (Grand Total only) and #store-performance
(5 stores, no GT).

I-0 finding (see STATE.md): the canonical Jul 3 2026 format's source is the
Bravo "Company Performance (KPI)" report (company-kpis cell), NOT the
end-of-month cell the legacy monthly-analytics-report/SKILL.md's
parse_eom.py assumed — Net Revenue = Retail GP + Scrap GP + PSC. No
byte-exact historical Slack post was recoverable (Slack strips table bodies
from old posts, and no Google Sheet exists for June) — this renderer is
verified against real Bravo numbers two independent ways (Bravo's own Net
Revenue MTD dashboard card, and parse_eom.py's own penny-verified CUL/HAR
figures), not against an exact historical post. Shadow-test before live.

Google Sheet upload is explicitly optional per spec (no new OAuth plumbing)
-- this job publishes to the existing SQLite/dashboard path only.
"""

from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vpops import bravo, common, formats, store

JOB_NAME = "job_monthly_analytics"
HEARTBEAT_DIR = Path(__file__).resolve().parent.parent / "data" / "heartbeats"

WINDOW_KEYS = [
    "same_month_current", "same_month_prior",
    "ytd_current", "ytd_prior",
    "t12m_current", "t12m_prior",
]

_MONTH_ABBREV = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
_MONTH_FULL = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September",
               "October", "November", "December"]


def write_heartbeat(status: str, detail: str) -> None:
    HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().isoformat()
    (HEARTBEAT_DIR / f"{JOB_NAME}.json").write_text(json.dumps({"ts": ts, "status": status, "detail": detail}))
    store.write_run(JOB_NAME, ts, status, detail)


def _month_abbrev_label(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{_MONTH_ABBREV[d.month]} {d.year}"


def _month_full_label(date_str: str) -> str:
    """Real 2026-07-03 post uses full month names for the title + View 1
    ("June 2026 vs June 2025") but abbreviated names for YTD/T12M ranges
    ("Jan-Jun 2026", "Jul 2025-Jun 2026") -- verified against the actual
    live post text, not assumed."""
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{_MONTH_FULL[d.month]} {d.year}"


def already_posted_today(channel: str, title_fragment: str) -> bool:
    midnight = datetime.combine(datetime.now().date(), datetime.min.time()).timestamp()
    messages = common.slack_read_history(channel, midnight)
    return any(title_fragment in m.get("text", "") for m in messages)


def run(mode: str, report_month_key: str | None = None) -> int:
    log_path = common.setup_logging(JOB_NAME)
    common.log.info(f"Starting {JOB_NAME} (mode={mode}); log at {log_path}")

    if report_month_key is None:
        today = datetime.now()
        last_month_end = today.replace(day=1) - timedelta(days=1)
        report_month_key = last_month_end.strftime("%Y-%m")

    sidecar_dir = bravo.MONTHLY_SIDECAR_DIR / report_month_key
    missing = [wkey for wkey in WINDOW_KEYS if not (sidecar_dir / f"{wkey}.xlsx").exists()]
    if missing:
        common.log.error(f"Missing staged windows for {report_month_key}: {missing} (looked in {sidecar_dir})")
        write_heartbeat("fail", f"missing windows: {missing}")
        common.missed_run_dm(JOB_NAME, report_month_key, dry_run=(mode != "live"))
        return 2

    parsed = {wkey: formats.extract_company_kpis(sidecar_dir / f"{wkey}.xlsx") for wkey in WINDOW_KEYS}
    windows_meta = bravo.compute_monthly_windows(datetime.strptime(report_month_key + "-01", "%Y-%m-%d"))

    windows = {
        "same_month": {"current": parsed["same_month_current"], "prior": parsed["same_month_prior"]},
        "ytd": {"current": parsed["ytd_current"], "prior": parsed["ytd_prior"]},
        "t12m": {"current": parsed["t12m_current"], "prior": parsed["t12m_prior"]},
    }

    month_label = _month_full_label(windows_meta["same_month_current"][0])
    prior_month_label = _month_full_label(windows_meta["same_month_prior"][0])
    month_abbrev = _month_abbrev_label(windows_meta["same_month_current"][0])
    prior_month_abbrev = _month_abbrev_label(windows_meta["same_month_prior"][0])
    ytd_start = "Jan"  # YTD always starts Jan 1, regardless of report month
    view_ranges = {
        "ytd": f"{ytd_start}-{month_abbrev} vs {ytd_start}-{prior_month_abbrev}",
        "t12m": f"{_month_abbrev_label(windows_meta['t12m_current'][0])}-{month_abbrev} vs "
                f"{_month_abbrev_label(windows_meta['t12m_prior'][0])}-{prior_month_abbrev}",
    }
    t12m_note = windows_meta["t12m_prior_note"] if windows_meta["t12m_prior_clamped"] else ""

    company_msg = formats.render_monthly_analytics_company(windows, month_label, prior_month_label, view_ranges, t12m_note)
    store_msg = formats.render_monthly_analytics_store(windows, month_label, prior_month_label, view_ranges)

    same_month_current = parsed["same_month_current"]
    as_of = windows_meta["same_month_current"][1]
    kpi_rows = []
    for key, metrics in same_month_current.items():
        for metric, value in metrics.items():
            kpi_rows.append((key, f"Monthly {metric}", value, as_of, "monthly", "job_monthly_analytics"))
    store.write_kpis_bulk(kpi_rows)

    if mode == "dry-run":
        print("=== #company-performance ===")
        print(company_msg)
        print()
        print("=== #store-performance ===")
        print(store_msg)
        write_heartbeat("ok", f"dry-run rendered for {report_month_key}")
        return 0

    company_channel = common.CHANNELS["vp-ops-shadow"] if mode == "shadow" else common.CHANNELS["company-performance"]
    store_channel = common.CHANNELS["vp-ops-shadow"] if mode == "shadow" else common.CHANNELS["store-performance"]
    title_fragment = f"Monthly Analytics - {month_label}"

    if mode == "live" and already_posted_today(company_channel, title_fragment):
        common.log.info(f"Already posted {title_fragment} to {company_channel} today -- skipping (dup-guard).")
        write_heartbeat("ok", f"skipped, already posted for {report_month_key}")
        return 0

    ts1 = common.slack_post(company_channel, company_msg, dry_run=False)
    ts2 = common.slack_post(store_channel, store_msg, dry_run=False)
    if not ts1 or not ts2:
        common.log.error("Failed to post one or both Monthly Analytics messages.")
        write_heartbeat("fail", "slack post failed")
        common.missed_run_dm(JOB_NAME, report_month_key)
        return 2

    write_heartbeat("ok", f"posted for {report_month_key} to {company_channel} and {store_channel}")
    common.log.info(f"Posted Monthly Analytics for {report_month_key}.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True, help="render only, no Slack post (default)")
    parser.add_argument("--shadow", action="store_true", help="post to #vp-ops-shadow instead of production")
    parser.add_argument("--live", action="store_true", help="post to production #company-performance and #store-performance")
    parser.add_argument("--month", help="override report month key, e.g. 2026-06 (for manual testing)")
    args = parser.parse_args()

    mode = "live" if args.live else ("shadow" if args.shadow else "dry-run")
    try:
        sys.exit(run(mode, report_month_key=args.month))
    except Exception as e:
        common.report_crash(JOB_NAME, e, dry_run=(mode != "live"))
        sys.exit(1)
