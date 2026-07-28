#!/usr/bin/env python3
"""
job_gold_trend.py — VP Ops Engine Job J-1 (BUILD_SPEC_WAVE2.md §4).

Runs 1st of the month, 08:30 ET. Pulls the PRIOR month's gold dwt per store
via the `scrap-refining-gold` cell (an EXISTING, already-registered pipeline
handler — J-0's infrastructure was already built 2026-07-18..23, before
BUILD_SPEC_WAVE2.md was written; see STATE.md for the full correction),
appends to the shared history file, computes YoY (same month, prior year)
plus YTD and best-T12M-month, and posts to #gold-trend-.

No prior canon exists for this channel's format — the spec's proposed format
becomes canon on the first real post (BUILD_SPEC_WAVE2.md §4).

Open-buckets caveat: current-month dwt accumulates until refining close, so
this job always reports the PRIOR month. If a store shows a zero/near-zero
bucket for the target month (buckets not yet closed), that's flagged in the
post rather than silently shown as a real decline.
"""

from __future__ import annotations
import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vpops import bravo, common, formats, store

JOB_NAME = "job_gold_trend"
HEARTBEAT_DIR = Path(__file__).resolve().parent.parent / "data" / "heartbeats"
STORES = bravo.STORES

_MONTH_FULL = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September",
               "October", "November", "December"]


def write_heartbeat(status: str, detail: str) -> None:
    HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().isoformat()
    (HEARTBEAT_DIR / f"{JOB_NAME}.json").write_text(json.dumps({"ts": ts, "status": status, "detail": detail}))
    store.write_run(JOB_NAME, ts, status, detail)


def _month_label(year_month: str) -> str:
    y, m = year_month.split("-")
    return f"{_MONTH_FULL[int(m)]} {y}"


def _prior_year_month(year_month: str) -> str:
    y, m = year_month.split("-")
    return f"{int(y) - 1}-{m}"


def _shift_month(year_month: str, delta: int) -> str:
    y, m = (int(x) for x in year_month.split("-"))
    total = y * 12 + (m - 1) + delta
    ny, nm = divmod(total, 12)
    return f"{ny}-{nm + 1:02d}"


def already_posted_today(channel: str, title_fragment: str) -> bool:
    midnight = datetime.combine(datetime.now().date(), datetime.min.time()).timestamp()
    messages = common.slack_read_history(channel, midnight)
    return any(title_fragment in m.get("text", "") for m in messages)


def run(mode: str, report_month: str | None = None) -> int:
    log_path = common.setup_logging(JOB_NAME)
    common.log.info(f"Starting {JOB_NAME} (mode={mode}); log at {log_path}")

    if report_month is None:
        today = datetime.now()
        last_month_end = today.replace(day=1) - timedelta(days=1)
        report_month = last_month_end.strftime("%Y-%m")
    year = int(report_month.split("-")[0])

    if mode != "dry-run":
        common.log.info("Running Bravo health check...")
        healthy = bravo.ensure_healthy("CUL", timeout_s=900)
        if not healthy:
            common.log.warning("Health gate reported unhealthy, proceeding anyway (matches Job E's pattern).")

        trigger_id = f"vpops-gold-trend-{report_month}-{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}"
        date_field = f"{report_month}..{report_month}"
        drop_ts = time.time()
        bravo.drop_trigger(trigger_id, [{"name": "scrap-refining-gold", "stores": STORES, "date": date_field}])
        common.log.info(f"Dropped trigger for {date_field}, all 5 stores.")
        missing = bravo.wait_for_scrap_refining_gold(STORES, year, since_ts=drop_ts, timeout_s=900, poll_s=20)
        if missing:
            common.log.warning(f"Stores did not refresh within timeout: {missing} — will still try to read whatever's on disk.")

        new_rows = []
        for s in STORES:
            p = bravo.locate_scrap_refining_gold_file(s, year)
            if p is None:
                continue
            months = formats.extract_scrap_refining_gold(p)
            if report_month in months:
                new_rows.append({"store": s, "year_month": report_month, "dwt": round(months[report_month], 4), "source": JOB_NAME})
        appended = bravo.append_gold_dwt_history(new_rows)
        common.log.info(f"Appended {appended} new history row(s) for {report_month}.")

    history = bravo.read_gold_dwt_history()
    by_key = {}
    for r in history:
        by_key[(r["store"], r["year_month"])] = float(r["dwt"])

    prior_month = _prior_year_month(report_month)
    current_month_data = {s: by_key.get((s, report_month), 0.0) for s in STORES}
    prior_month_data = {s: by_key.get((s, prior_month), 0.0) for s in STORES}

    empty_stores = [s for s in STORES if current_month_data[s] == 0.0]

    # YTD compares the SAME set of available current-year months against
    # their prior-year equivalents -- not a fixed Jan..report_month range.
    # Early on, 2026 only has whatever months have actually been backfilled
    # or pulled so far (e.g. just June) -- comparing that single month
    # against a full Jan-June 2025 cumulative would be apples-to-oranges
    # (confirmed 2026-07-27: produced a nonsensical -76% before this fix).
    # This naturally grows into a true YTD as job_gold_trend runs monthly.
    report_year = report_month.split("-")[0]
    current_year_months = sorted({ym for (_s, ym) in by_key if ym.startswith(report_year) and ym <= report_month})
    ytd_current = sum(by_key.get((s, ym), 0.0) for s in STORES for ym in current_year_months)
    ytd_prior = sum(by_key.get((s, _prior_year_month(ym)), 0.0) for s in STORES for ym in current_year_months)

    t12m_months = [_shift_month(report_month, -i) for i in range(12)]
    t12m_company_by_month = {}
    for ym in t12m_months:
        total = sum(v for (st_, y_m), v in by_key.items() if y_m == ym)
        t12m_company_by_month[ym] = total
    best_ym = max(t12m_company_by_month, key=lambda k: t12m_company_by_month[k]) if t12m_company_by_month else report_month
    best_month_t12m = (_month_label(best_ym), t12m_company_by_month.get(best_ym, 0.0))

    message = formats.render_gold_trend(
        current_month_data, prior_month_data, ytd_current, ytd_prior, best_month_t12m,
        _month_label(report_month), _month_label(prior_month),
    )
    if empty_stores:
        names = ", ".join(bravo.STORE_NAMES[s] for s in empty_stores)
        message += f"\n_Note: {names} showed no closed refining buckets for {_month_label(report_month)} — may still be open._"

    kpi_rows = [(s, "Gold Dwt Purchased", current_month_data[s], report_month, "monthly", JOB_NAME) for s in STORES]
    store.write_kpis_bulk(kpi_rows)

    if mode == "dry-run":
        print(message)
        write_heartbeat("ok", f"dry-run rendered for {report_month}")
        return 0

    channel = common.CHANNELS["vp-ops-shadow"] if mode == "shadow" else common.CHANNELS["gold-trend"]
    title_fragment = f"Gold Trend — {_month_label(report_month)}"

    if mode == "live" and already_posted_today(channel, title_fragment):
        common.log.info(f"Already posted {title_fragment} to {channel} today -- skipping (dup-guard).")
        write_heartbeat("ok", f"skipped, already posted for {report_month}")
        return 0

    ts = common.slack_post(channel, message, dry_run=False)
    if not ts:
        common.log.error("Failed to post Gold Trend message.")
        write_heartbeat("fail", "slack post failed")
        common.missed_run_dm(JOB_NAME, report_month)
        return 2

    write_heartbeat("ok", f"posted for {report_month} to {channel}")
    common.log.info(f"Posted Gold Trend for {report_month}.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True, help="render only, no Bravo pull, no Slack post (default)")
    parser.add_argument("--shadow", action="store_true", help="pull real data, post to #vp-ops-shadow instead of production")
    parser.add_argument("--live", action="store_true", help="pull real data, post to production #gold-trend-")
    parser.add_argument("--month", help="override report month, e.g. 2026-06 (for manual testing)")
    args = parser.parse_args()

    mode = "live" if args.live else ("shadow" if args.shadow else "dry-run")
    try:
        sys.exit(run(mode, report_month=args.month))
    except Exception as e:
        common.report_crash(JOB_NAME, e, dry_run=(mode != "live"))
        sys.exit(1)
