#!/usr/bin/env python3
"""
publish_dashboard.py — VP Ops Engine Phase 2 (BUILD_SPEC.md §5.3).

Post-job step: renders vp-ops' data/latest.json into the EXISTING
Business Dashboard Website/site/data/kpis.json schema (never changes the
schema itself — the dashboard's render code depends on it exactly as-is),
then deploys via wrangler per REFRESH_RUNBOOK.md.

Only overwrites the fields vp-ops actually sources (pastDue, pastDueTotal,
companyLoanBalance, layaway, layawayTotal, dates.loans, dates.layaway, and
the "Last Run" column for the 3 feeds vp-ops covers). Every other field
(funds, watch, daily.*, bravoDaily, other feeds) is preserved byte-for-byte
from the existing file — those come from other sources this project
doesn't touch.

--dry-run (default): shows the diff, writes nothing, deploys nothing.
--live: writes kpis.json and deploys to Cloudflare Pages.
"""

from __future__ import annotations
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vpops import bravo, common, store

JOB_NAME = "publish_dashboard"
HEARTBEAT_DIR = Path(__file__).resolve().parent.parent / "data" / "heartbeats"

SITE_DIR = Path("/Users/joshuadavis/Documents/Claude/Projects/Business Dashboard Website")
KPIS_JSON_PATH = SITE_DIR / "site" / "data" / "kpis.json"
CLOUDFLARE_DIR = SITE_DIR / ".cloudflare"
NODE_BIN = Path.home() / "Documents" / "Claude" / "tools" / "node" / "bin"


def write_heartbeat(status: str, detail: str) -> None:
    HEARTBEAT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().isoformat()
    payload = {"ts": ts, "status": status, "detail": detail}
    (HEARTBEAT_DIR / f"{JOB_NAME}.json").write_text(json.dumps(payload))
    store.write_run(JOB_NAME, ts, status, detail)


def _human_date(date_str: str) -> str:
    """Full month name, e.g. 'July 26, 2026' — matches the existing
    kpis.json's own 'asOf' field convention."""
    y, m, d = date_str.split("-")
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    return f"{months[int(m) - 1]} {int(d)}, {y}"


def _abbrev_date(date_str: str) -> str:
    """Abbreviated month, e.g. 'Jul 26, 2026' — matches the existing
    kpis.json's own 'dates' and 'feeds' field convention (different from
    'asOf' — confirmed by reading the file, not a guess)."""
    y, m, d = date_str.split("-")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul",
              "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{months[int(m) - 1]} {int(d)}, {y}"


def build_updates() -> dict | None:
    """Reads vp-ops' SQLite store directly (richer than latest.json's flat
    view) and returns the subset of kpis.json fields vp-ops can populate.
    Returns None if none of the source data is available yet."""
    kpis = store.latest_kpis()
    if not kpis:
        return None

    updates: dict = {}

    # --- Past-Due Loan Review ---
    pastdue_stores = [s for s in bravo.STORES if s in kpis and "PastDue75 Items" in kpis[s]]
    if pastdue_stores:
        as_of = kpis[pastdue_stores[0]]["PastDue75 Items"]["as_of"]
        pastdue_rows = []
        total_items, total_dollars = 0, 0.0
        total_loan_balance = 0.0
        for s in pastdue_stores:
            items = kpis[s]["PastDue75 Items"]["value"]
            dollars = kpis[s]["PastDue75 Dollars"]["value"]
            pct = kpis[s]["PastDue75 Pct"]["value"]
            pastdue_rows.append([bravo.STORE_NAMES[s], int(items), dollars, round(pct, 2)])
            total_items += int(items)
            total_dollars += dollars
            if "Loan Balance" in kpis.get(s, {}):
                total_loan_balance += kpis[s]["Loan Balance"]["value"]
        updates["pastDue"] = pastdue_rows
        updates["pastDueTotal"] = {
            "items": total_items, "dollars": round(total_dollars, 2),
            "pct": round(total_dollars / total_loan_balance * 100, 2) if total_loan_balance else 0.0,
        }
        if total_loan_balance:
            updates["companyLoanBalance"] = round(total_loan_balance, 2)
        updates.setdefault("dates", {})["loans"] = _abbrev_date(as_of)

    # --- Layaway Review ---
    layaway_stores = [s for s in bravo.STORES if s in kpis and "Layaway overdue" in kpis[s]]
    if layaway_stores:
        as_of = kpis[layaway_stores[0]]["Layaway overdue"]["as_of"]
        totals = {k: 0 for k in ("overdue", "past_pmt_due", "contacted_no_activity", "no_pmt_30d", "locate")}
        for s in layaway_stores:
            for k in totals:
                totals[k] += int(kpis[s][f"Layaway {k}"]["value"])
        layaway_rows = []
        for s in layaway_stores:
            def cell(key):
                v = int(kpis[s][f"Layaway {key}"]["value"])
                if key == "locate":
                    return v
                pct = round(v / totals[key] * 100) if totals[key] else 0
                return f"{v} ({pct}%)"
            layaway_rows.append([bravo.STORE_NAMES[s], cell("overdue"), cell("past_pmt_due"),
                                  cell("contacted_no_activity"), cell("no_pmt_30d"), cell("locate")])
        updates["layaway"] = layaway_rows
        updates["layawayTotal"] = ["Company", totals["overdue"], totals["past_pmt_due"],
                                    totals["contacted_no_activity"], totals["no_pmt_30d"], totals["locate"]]
        updates.setdefault("dates", {})["layaway"] = _abbrev_date(as_of)

    # --- Feed "Last Run" dates ---
    feed_updates = {}
    if pastdue_stores:
        feed_updates["Past-Due Loan Review (75-day rule)"] = _abbrev_date(kpis[pastdue_stores[0]]["PastDue75 Items"]["as_of"])
    if layaway_stores:
        feed_updates["Layaway Review"] = _abbrev_date(kpis[layaway_stores[0]]["Layaway overdue"]["as_of"])
    aged_stores = [s for s in bravo.STORES if s in kpis and "Aged Total" in kpis[s]]
    if aged_stores:
        feed_updates["Aged Inventory Review"] = _abbrev_date(kpis[aged_stores[0]]["Aged Total"]["as_of"])
    if feed_updates:
        updates["_feed_updates"] = feed_updates

    return updates or None


def apply_updates(existing: dict, updates: dict) -> dict:
    merged = json.loads(json.dumps(existing))  # deep copy
    feed_updates = updates.pop("_feed_updates", {})
    for key in ("pastDue", "pastDueTotal", "companyLoanBalance", "layaway", "layawayTotal"):
        if key in updates:
            merged[key] = updates[key]
    if "dates" in updates:
        merged.setdefault("dates", {}).update(updates["dates"])
    if feed_updates:
        for row in merged.get("feeds", []):
            if row and row[0] in feed_updates:
                row[-1] = feed_updates[row[0]]
    merged["asOf"] = _human_date(datetime.now().strftime("%Y-%m-%d"))
    return merged


def deploy() -> tuple[bool, str]:
    env_extra = {
        "PATH": f"{NODE_BIN}:{Path.home()}/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "CLOUDFLARE_API_TOKEN": (CLOUDFLARE_DIR / "api_token").read_text().strip(),
        "CLOUDFLARE_ACCOUNT_ID": (CLOUDFLARE_DIR / "account_id").read_text().strip(),
    }
    import os
    env = {**os.environ, **env_extra}
    result = subprocess.run(
        ["npx", "wrangler", "pages", "deploy", "site", "--project-name=vp-dashboard", "--commit-dirty=true"],
        cwd=str(SITE_DIR), env=env, capture_output=True, text=True, timeout=120,
    )
    ok = result.returncode == 0
    tail = (result.stdout + result.stderr).strip().splitlines()
    return ok, "\n".join(tail[-5:])


def run(mode: str) -> int:
    log_path = common.setup_logging(JOB_NAME)
    common.log.info(f"Starting {JOB_NAME} (mode={mode}); log at {log_path}")

    updates = build_updates()
    if not updates:
        common.log.info("No vp-ops KPI data available yet — nothing to publish.")
        write_heartbeat("ok", "no data yet, skipped")
        return 0

    if not KPIS_JSON_PATH.exists():
        common.log.error(f"{KPIS_JSON_PATH} not found.")
        write_heartbeat("fail", "kpis.json not found")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"), dry_run=(mode != "live"))
        return 2

    existing = json.loads(KPIS_JSON_PATH.read_text())
    merged = apply_updates(existing, dict(updates))

    if mode == "dry-run":
        print("=== Fields that would change ===")
        for key in ("pastDue", "pastDueTotal", "companyLoanBalance", "layaway", "layawayTotal", "dates", "feeds"):
            if merged.get(key) != existing.get(key):
                print(f"\n--- {key} ---")
                print(json.dumps(merged.get(key), indent=2))
        write_heartbeat("ok", "dry-run — kpis.json not written, not deployed")
        return 0

    KPIS_JSON_PATH.write_text(json.dumps(merged, indent=2))
    common.log.info(f"Wrote {KPIS_JSON_PATH}")

    ok, tail = deploy()
    if not ok:
        common.log.error(f"wrangler deploy failed:\n{tail}")
        write_heartbeat("fail", f"deploy failed: {tail[-200:]}")
        common.missed_run_dm(JOB_NAME, datetime.now().strftime("%Y-%m-%d"))
        return 2

    common.log.info(f"Deployed: {tail}")
    write_heartbeat("ok", "kpis.json updated and deployed")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True, help="show diff only, write/deploy nothing (default)")
    parser.add_argument("--live", action="store_true", help="write kpis.json and deploy to Cloudflare Pages")
    args = parser.parse_args()

    mode = "live" if args.live else "dry-run"
    try:
        sys.exit(run(mode))
    except Exception as e:
        common.report_crash(JOB_NAME, e, dry_run=(mode != "live"))
        sys.exit(1)
