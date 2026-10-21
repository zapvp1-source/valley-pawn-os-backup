#!/usr/bin/env python3
"""eom_gl_export.py [YYYY-MM] [--render] [--no-pull] — native `eom-bravo-gl-export` (1st of month 06:00 ET;
Mac-first wave 3, 2026-10-19). The SKILL's scripted steps, through the trigger pipeline only:
  1 post-to-accounting-post for the prior month, all 5 stores (one trigger via bin/bravo_pull.sh; stores whose cell
    errored are re-dropped, up to 3 attempts total); days_posted / skipped / errors read from the cell's .txt
  2 post-to-accounting-gl for the prior month unless <END>_<STORE>_post-to-accounting-gl.csv (written after the
    month closed) is already on disk for all 5 stores; missing stores re-dropped, 3 attempts total
  3 combine the 5 CSVs (latin-1) into output/<YYYY-MM> Consolidated GL.xlsx — one tab per store + Combined,
    the exact shape of the 2026-07 workbook
  4 copy the workbook into the Drive-for-Desktop "Accounting Exports" folder (Valley Pawn Drive) — found by name
    under ~/Library/CloudStorage; no Drive API write scope exists on the Mac and none is needed
  5 QuickBooks journal entry: NOT POSTED, BY RULE. books-tax-strategy Gate 4 (no journal entries in an open year)
    and Joshua's 2026-10-19 direction: GL export = file + DM only. The DM says the file is ready for his review.
  6 ONE plain DM to Joshua with the per-store posting results, whether the GL was reused or pulled fresh, the
    workbook + Drive location, the sales-tax note; incomplete = ledger row (the day-2 watchdog owns the alert).
State: fleet/state/eom_gl_export/<YYYY-MM>.json (read by the watchdog and the sales-tax agent).
--render: steps 3-4 (to fleet/test_output) + the DM text from whatever is on disk; no pull, no copy, no DM.
"""
import calendar
import csv
import datetime as dt
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
AGENT = "eom-bravo-gl-export"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.dirname(HERE)
PROJ = os.path.dirname(OS_DIR)
BRAVO = os.environ.get("VP_BRAVO_DIR") or os.path.join(PROJ, "Bravo Data Extraction")
OUT = os.path.join(BRAVO, "output")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
STATE_DIR = os.path.join(OS_DIR, "fleet", "state", "eom_gl_export")
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
NAMES = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke", "WAY": "Waynesboro"}
CLOUD = os.path.expanduser("~/Library/CloudStorage")


def ledger(sentence):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n"
                                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))
    except OSError:
        pass


def month_arg(args):
    if args:
        y, m = map(int, args[0].split("-"))
    else:
        d = dt.datetime.now(ET).date().replace(day=1) - dt.timedelta(days=1)
        y, m = d.year, d.month
    return dt.date(y, m, 1), dt.date(y, m, calendar.monthrange(y, m)[1])


def gl_path(s, end):
    return os.path.join(OUT, "%s_%s_post-to-accounting-gl.csv" % (end, s))


def gl_ok(s, end):
    p = gl_path(s, end)
    return os.path.exists(p) and os.path.getsize(p) > 300 and dt.datetime.fromtimestamp(os.path.getmtime(p)).date() > end


def result(tid):
    try:
        return json.load(open(os.path.join(BRAVO, "results", tid + ".result.json"), encoding="utf-8-sig"))
    except (OSError, ValueError):
        return {}


def pull(report, start, end, stores, tag):
    tid = "%s-%s-%s-%d" % (tag, start.strftime("%Y%m"), "".join(s[0] for s in stores), int(time.time()))
    subprocess.run(["/bin/bash", os.path.join(HERE, "bravo_pull.sh"), report, "%s..%s" % (start, end), ",".join(stores), tid],
                   capture_output=True, text=True, timeout=7500)
    r = result(tid)
    cells = {c.get("store"): c for c in r.get("cells", [])}
    return tid, cells


def read_post_txt(s, end):
    p = os.path.join(OUT, "%s_%s_post-to-accounting-post-v2.txt" % (end, s))   # v2 cell (2026-10-20)
    if not os.path.exists(p):
        p = os.path.join(OUT, "%s_%s_post-to-accounting-post.txt" % (end, s))
    d = {"posted": None, "skipped": None, "errors": None}
    try:
        t = open(p, encoding="utf-8-sig", errors="replace").read()
        m = re.search(r"posted \((\d+)\)", t); d["posted"] = int(m.group(1)) if m else None
        m = re.search(r"skipped[^(]*\((\d+)\)", t); d["skipped"] = int(m.group(1)) if m else (len([x for x in re.findall(r"skipped-serials:\s*(\S*)", t)[0].split(",") if x]) if "skipped-serials" in t else None)
        m = re.search(r"errors \((\d+)\)", t); d["errors"] = int(m.group(1)) if m else None
        em = re.search(r"errors \(\d+\):\s*(.*)", t); d["error_text"] = em.group(1).strip() if em else ""
    except OSError:
        pass
    return d


def combine(ym, end, dest_dir):
    from openpyxl import Workbook
    wb = Workbook()
    wb.remove(wb.active)
    comb = []
    for s in STORES:
        rows = list(csv.reader(open(gl_path(s, end), encoding="latin-1", newline="")))
        ws = wb.create_sheet(s)
        for r in rows:
            ws.append(r)
        comb += [[s] + r for r in rows]
    ws = wb.create_sheet("Combined")
    ws.append(["Store", "Col1", "Col2", "Col3", "Col4"])
    for r in comb:
        ws.append((r + [None] * 5)[:5])
    os.makedirs(dest_dir, exist_ok=True)
    p = os.path.join(dest_dir, "%s Consolidated GL.xlsx" % ym)
    wb.save(p)
    return p


def drive_folder(max_depth=6):
    """The 'Accounting Exports' folder (Drive id 1FzXIRPNZHaECOwfaKpQDMUTPRY3-d12_) as streamed by Drive for Desktop.
    2026-10-19 probe: NOT at Shared drives/Valley Pawn Drive/Accounting Exports, so walk every GoogleDrive-* root
    (My Drive + Shared drives) up to max_depth for a directory of that name."""
    for root in glob.glob(os.path.join(CLOUD, "GoogleDrive-*")):
        for base in ("Shared drives", "My Drive"):
            top = os.path.join(root, base)
            if not os.path.isdir(top):
                continue
            for cur, dirs, _files in os.walk(top):
                depth = cur[len(top):].count(os.sep)
                if "Accounting Exports" in dirs:
                    return os.path.join(cur, "Accounting Exports")
                if depth >= max_depth:
                    dirs[:] = []
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render, no_pull = "--render" in sys.argv, "--no-pull" in sys.argv
    start, end = month_arg(args)
    ym, month = start.strftime("%Y-%m"), start.strftime("%B %Y")
    os.makedirs(STATE_DIR, exist_ok=True)
    st = {"month": ym, "run": dt.datetime.now(ET).isoformat(), "mode": "render" if render else "live", "posting": {}, "gl": {}, "triggers": []}
    # STEP 1 — post unposted days
    if not (render or no_pull):
        todo = list(STORES)
        for attempt in range(3):
            if not todo:
                break
            tid, cells = pull("post-to-accounting-post-v2", start, end, todo, "eom-gl-post" if attempt == 0 else "eom-gl-post-retry%d" % attempt)
            st["triggers"].append(tid)
            for s in list(todo):
                c = cells.get(s, {})
                st["posting"][s] = {"status": c.get("status", "no-result"), "error": c.get("error", ""), **read_post_txt(s, end)}
                if c.get("status") == "success":
                    todo.remove(s)
    else:
        for s in STORES:
            st["posting"][s] = {"status": "render", **read_post_txt(s, end)}
    # STEP 2 — GL export (reuse if present)
    missing = [s for s in STORES if not gl_ok(s, end)]
    st["gl"]["reused"] = [s for s in STORES if s not in missing]
    if missing and not (render or no_pull):
        for attempt in range(3):
            if not missing:
                break
            tid, cells = pull("post-to-accounting-gl", start, end, missing, "eom-gl-export" if attempt == 0 else "eom-gl-export-retry%d" % attempt)
            st["triggers"].append(tid)
            missing = [s for s in STORES if not gl_ok(s, end)]
    st["gl"]["missing"] = missing
    st["gl"]["complete"] = not missing
    wb = drive = None
    if not missing:
        # STEP 3 + 4
        wb = combine(ym, end, os.path.join(OS_DIR, "fleet", "test_output", "eom_gl_render") if render else OUT)
        st["workbook"] = wb
        if not render:
            d = drive_folder()
            if d:
                try:
                    shutil.copy2(wb, os.path.join(d, os.path.basename(wb)))
                    drive = os.path.join(d, os.path.basename(wb))
                except OSError as e:
                    st["drive_error"] = str(e)
            else:
                st["drive_error"] = "Accounting Exports folder not found under ~/Library/CloudStorage"
            st["drive"] = drive
    # STEP 6 — DM text
    lines = ["Month-end books for %s:" % month]
    for s in STORES:
        p = st["posting"].get(s, {})
        bits = []
        if p.get("posted") is not None: bits.append("%d day%s posted" % (p["posted"], "" if p["posted"] == 1 else "s"))
        if p.get("skipped") is not None: bits.append("%d skipped" % p["skipped"])
        if p.get("errors"): bits.append("%d day%s would not post%s" % (p["errors"], "" if p["errors"] == 1 else "s", (" (" + p.get("error_text", "").split(":")[0] + ")") if p.get("error_text") else ""))
        if p.get("status") not in ("success", "render") and not bits: bits.append("posting did not finish")
        lines.append("• %s — %s" % (NAMES[s], ", ".join(bits) or "nothing to post"))
    if missing:
        lines.append("The general ledger export is still missing %s, so the combined file is not ready yet. The sales tax sheet will wait for it." % ", ".join(NAMES[s] for s in missing))
    else:
        lines.append("General ledger for all 5 stores %s. Combined file: %s%s." % (
            "re-used from this morning's pull" if len(st["gl"]["reused"]) == 5 else "pulled fresh", os.path.basename(wb),
            (" — in the Accounting Exports folder on the shared drive" if drive else " — saved locally (the shared-drive folder was not reachable)") if not render else ""))
        lines.append("Not posted to QuickBooks — the file is ready for your review and entry. The sales tax sheet picks up these same numbers this morning.")
    dm = "\n".join(lines)
    st["dm"] = dm
    json.dump(st, open(os.path.join(STATE_DIR, "%s%s.json" % (ym, "-render" if render else "")), "w"), indent=1)
    if render:
        print("=== RENDER ONLY ===\n%s\n\nworkbook: %s\nposting: %s" % (dm, wb, json.dumps(st["posting"])))
        return 0 if not missing else 2
    if missing:
        ledger("Month-end GL export for %s incomplete — %s missing after retries; posting results in fleet/state/eom_gl_export/%s.json." % (month, ", ".join(missing), ym))
        return 2
    p = subprocess.run([sys.executable, os.path.join(HERE, "vp_slack.py"), "dm", dm], capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, VP_TASK=AGENT))
    st["dm_sent"] = p.returncode == 0
    json.dump(st, open(os.path.join(STATE_DIR, "%s.json" % ym), "w"), indent=1)
    if p.returncode != 0:
        ledger("Month-end GL export for %s completed but the summary DM did not send." % month)
        return 1
    print("done", month)
    return 0


if __name__ == "__main__":
    sys.exit(main())
