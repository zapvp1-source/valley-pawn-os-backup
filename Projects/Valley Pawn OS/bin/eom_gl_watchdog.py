#!/usr/bin/env python3
"""eom_gl_watchdog.py [YYYY-MM] [--render] — native `eom-bravo-gl-export-watchdog` (2nd of month 08:00 ET; Mac-first
wave 3, 2026-10-19). Verifies the 1st's GL export by its OUTPUT (Rule 12), never a run record:
  (a) fleet/state/eom_gl_export/<ym>.json says gl complete + DM sent, and
  (b) output/<ym> Consolidated GL.xlsx exists, written after the month closed, and
  (c) that workbook opens and has every store sheet + the Combined sheet with rows (complete).
  The shared-drive "Accounting Exports" copy is NOT a pass condition (2026-10-21: that folder is not synced on this
  Mac, so drive_folder() is None and the export saves locally by design). It is mentioned — one plain line, "not
  synced on this Mac" — only inside a DM that is already going out because the export itself failed.
All good = silent. Otherwise ONE plain DM to Joshua (once per month; fleet/state/eom_gl_watchdog_<ym>) saying what
is still missing and whether it is still catching up (posting errors in the state file) or genuinely stuck. Never
re-drives Bravo or re-triggers the export. QuickBooks is not checked: the export posts no journal entry by rule.
"""
import calendar
import datetime as dt
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = "eom-bravo-gl-export-watchdog"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.dirname(HERE)
PROJ = os.path.dirname(OS_DIR)
BRAVO = os.environ.get("VP_BRAVO_DIR") or os.path.join(PROJ, "Bravo Data Extraction")
OUT = os.path.join(BRAVO, "output")
NAMES = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke", "WAY": "Waynesboro"}


def workbook_complete(path):
    """True when the combined workbook has a non-empty sheet per store and a Combined sheet with data rows."""
    try:
        from openpyxl import load_workbook
        wb = load_workbook(path, read_only=True)
        try:
            for name in list(NAMES) + ["Combined"]:
                if name not in wb.sheetnames:
                    return False
                rows = sum(1 for _ in wb[name].iter_rows(max_col=1, values_only=True))
                if rows < (2 if name == "Combined" else 1):
                    return False
        finally:
            wb.close()
        return True
    except Exception:   # noqa: BLE001  unreadable = not complete
        return False


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render = "--render" in sys.argv
    now = dt.datetime.now(ET)
    if args:
        y, m = map(int, args[0].split("-"))
    else:
        d = now.date().replace(day=1) - dt.timedelta(days=1)
        y, m = d.year, d.month
    ym, month = "%04d-%02d" % (y, m), dt.date(y, m, 1).strftime("%B %Y")
    end = dt.date(y, m, calendar.monthrange(y, m)[1])
    st = {}
    sp = os.path.join(OS_DIR, "fleet", "state", "eom_gl_export", ym + ".json")
    for a in sys.argv[1:]:
        if render and a.startswith("--state="):   # test hook, render only: read a given state file instead
            sp = a.split("=", 1)[1]
    try:
        st = json.load(open(sp))
    except (OSError, ValueError):
        pass
    wb = os.path.join(OUT, "%s Consolidated GL.xlsx" % ym)
    wb_ok = os.path.exists(wb) and dt.datetime.fromtimestamp(os.path.getmtime(wb)).date() > end
    wb_full = wb_ok and workbook_complete(wb)
    drive_ok = bool(st.get("drive")) and os.path.exists(st["drive"])
    problems = []
    if not st:
        problems.append("the export never ran (no state file)")
    else:
        if not st.get("gl", {}).get("complete"):
            problems.append("ledger export incomplete for %s" % ", ".join(NAMES.get(s, s) for s in st.get("gl", {}).get("missing", [])))
        bad = [s for s, p in st.get("posting", {}).items() if p.get("errors") or p.get("status") not in ("success", "render")]
        if bad:
            problems.append("some days would not post at %s" % ", ".join(NAMES.get(s, s) for s in bad))
        if not st.get("dm_sent"):
            problems.append("the summary never reached you")
    if not wb_ok:
        problems.append("no combined ledger file for %s" % month)
    elif not wb_full:
        problems.append("the combined ledger file for %s is missing a store or is empty" % month)
    if not problems:
        print("ok — %s export verified by output (local workbook + state file%s)" % (
            month, "" if drive_ok else "; shared-drive copy not synced on this Mac, not checked"))
        return 0
    stuck = any("would not post" in p or "incomplete" in p for p in problems)
    dm = ("The %s month-end ledger export didn't finish: %s. %s" % (
        month, "; ".join(problems),
        "The store system wouldn't post one or more days, so it's stuck until that day posts — it won't fix itself." if stuck
        else "It may still be catching up; if nothing arrives by tomorrow it needs a manual run."))
    if not drive_ok:
        dm += "\nThe shared-drive copy isn't checked here — that folder isn't synced on this Mac."
    if render:
        print("WOULD DM: " + dm)
        return 0
    marker = os.path.join(OS_DIR, "fleet", "state", "eom_gl_watchdog_%s" % ym)
    if os.path.exists(marker):
        print("problems found but already reported this month"); return 0
    p = subprocess.run([sys.executable, os.path.join(HERE, "vp_slack.py"), "dm", dm], capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, VP_TASK=AGENT))
    real = p.returncode == 0 and "DRY RUN" not in p.stdout   # a guard-diverted DM must not set the once-a-month marker
    if real:
        os.makedirs(os.path.dirname(marker), exist_ok=True)
        open(marker, "w").write(now.isoformat())
    print("DM %s: %s" % ("sent" if real else ("DRY RUN — diverted, not sent" if p.returncode == 0 else "failed"), dm))
    return 0


if __name__ == "__main__":
    sys.exit(main())
