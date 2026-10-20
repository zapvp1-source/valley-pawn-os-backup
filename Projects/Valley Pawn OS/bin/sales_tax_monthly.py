#!/usr/bin/env python3
"""sales_tax_monthly.py [YYYY-MM] [--render] [--no-pull] — native `sales-tax-monthly-update` (1st of month 08:00 ET,
2 h after the GL export; Mac-first wave 3, 2026-10-19). The SKILL's steps, hardened 2026-08-24 version:
  STEP 1  <END>_<STORE>_post-to-accounting-gl.csv for all 5 stores (the GL export's own pull). Missing -> re-check
          every 3 min for up to 20 min; still missing -> pull post-to-accounting-gl through bin/bravo_pull.sh, up to
          3 attempts; still missing -> STOP and send the plain-language DM (never a silent blank row).
  STEP 2  per store: Taxable Sales = sum(Credit - Debit) over accounts starting "SALES TAXABLE"; Ebay = the
          "BANK - EBAY" row (Debit - Credit), 0 when absent (Roanoke). latin-1. 2 decimals.
  STEP 3  Sales Tax/Sales Tax.xlsx Sheet1: find last month's row by column-A label in calendar position (add one
          below the last used row if absent, same formatting), already-filled row = verify and stop. Taxable ->
          col 1, Ebay -> col 2, Taxes Due -> "=(<T>-<E>)*$G$1" ($#,##0.00), cell comments naming the source. The
          workbook is backed up first (Sales Tax/_backups/). No recalc step on the Mac (LibreOffice is not a
          dependency); Taxes Due for the DM is computed here from the same rate cell.
  STEP 4  forensic check (negative / zero / >2x or <0.5x the trailing-3-month average = flagged), company total,
          ONE short DM to Joshua (per-store Taxes Due, total, data source, anomalies). Blocked = the SKILL's plain DM.
NEVER posts a journal entry or touches QuickBooks. --render: compute + print the DM, write nothing, pull nothing.
"""
import calendar
import csv
import datetime as dt
import os
import shutil
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
AGENT = "sales-tax-monthly-update"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.dirname(HERE)
PROJ = os.path.dirname(OS_DIR)
BRAVO = os.environ.get("VP_BRAVO_DIR") or os.path.join(PROJ, "Bravo Data Extraction")
OUT = os.path.join(BRAVO, "output")
WB = os.path.join(PROJ, "Sales Tax", "Sales Tax.xlsx")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
NAMES = {"CUL": "Culpeper", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke", "WAY": "Waynesboro"}
COL = {"CUL": 3, "HAR": 6, "LEX": 9, "ROA": 12, "WAY": 15}   # Taxable column; Ebay = +1, Taxes Due = +2
LABELS = {1: "JAN", 2: "FEB", 3: "MAR", 4: "APRIL", 5: "MAY", 6: "JUNE", 7: "JULY", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"}
ALIASES = {"APR": 4, "APRIL": 4, "JUN": 6, "JUNE": 6, "JUL": 7, "JULY": 7, "SEPT": 9, "SEP": 9, "JAN": 1, "FEB": 2, "MAR": 3, "MAY": 5, "AUG": 8, "OCT": 10, "NOV": 11, "DEC": 12}


def ledger(sentence):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n"
                                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))
    except OSError:
        pass


def money(s):
    s = (s or "").strip().replace("$", "").replace(",", "")
    if not s:
        return 0.0
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    try:
        v = float(s)
    except ValueError:
        return 0.0
    return -v if neg else v


def gl_path(s, end):
    return os.path.join(OUT, "%s_%s_post-to-accounting-gl.csv" % (end, s))


def have(s, end):
    p = gl_path(s, end)
    return os.path.exists(p) and os.path.getsize(p) > 300


def figures(s, end):
    taxable = ebay = 0.0
    for r in csv.reader(open(gl_path(s, end), encoding="latin-1", newline="")):
        if len(r) < 4:
            continue
        acct = r[0].strip()
        if acct.startswith("SALES TAXABLE"):
            taxable += money(r[3]) - money(r[2])
        elif acct == "BANK - EBAY":
            ebay += money(r[2]) - money(r[3])
    return round(taxable, 2), round(ebay, 2)


FIRST_ROW, FIRST_YM = 5, (2025, 9)   # the 2026-07-08 layout: row 5 = SEP 2025, one row per month after it


def find_row(ws, y, m):
    """Row for (y, m) by calendar position (labels repeat yearly, so position decides). Verifies the label.
    Returns (row, already_filled); row beyond the sheet = append (caller writes the label)."""
    r = FIRST_ROW + (y - FIRST_YM[0]) * 12 + (m - FIRST_YM[1])
    lab = ws.cell(r, 1).value
    if r > ws.max_row or lab is None:
        return r, False
    if not (isinstance(lab, str) and ALIASES.get(lab.strip().upper()) == m):
        raise SystemExit("sheet layout drift: row %d label %r is not %s" % (r, lab, LABELS[m]))
    return r, ws.cell(r, 3).value is not None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render, no_pull = "--render" in sys.argv, "--no-pull" in sys.argv
    if args:
        y, m = map(int, args[0].split("-"))
    else:
        d = dt.datetime.now(ET).date().replace(day=1) - dt.timedelta(days=1)
        y, m = d.year, d.month
    start, end = dt.date(y, m, 1), dt.date(y, m, calendar.monthrange(y, m)[1])
    month = start.strftime("%B %Y")
    source = "fed by this morning's month-end export"
    missing = [s for s in STORES if not have(s, end)]
    if missing and not (render or no_pull):
        for _ in range(7):
            time.sleep(180)
            missing = [s for s in STORES if not have(s, end)]
            if not missing:
                source = "fed by this morning's month-end export (after a short wait)"; break
        attempts = 0
        while missing and attempts < 3:
            attempts += 1
            subprocess.run(["/bin/bash", os.path.join(HERE, "bravo_pull.sh"), "post-to-accounting-gl", "%s..%s" % (start, end), ",".join(missing),
                            "sales-tax-monthly-%s-%d" % (start.strftime("%Y%m"), int(time.time()))], capture_output=True, text=True, timeout=7500)
            missing = [s for s in STORES if not have(s, end)]
            source = "pulled by the sales tax run itself"
    if missing:
        dm = ("The %s sales tax figures couldn't be pulled from the store system yet — %s still missing. The row is being left blank until the data is available; "
              "this needs a re-run once the month-end numbers catch up." % (month, ", ".join(NAMES[s] for s in missing)))
        if render:
            print("=== RENDER ONLY (blocked) ===\n" + dm); return 2
        subprocess.run([sys.executable, os.path.join(HERE, "vp_slack.py"), "dm", dm], capture_output=True, text=True, timeout=60, env=dict(os.environ, VP_TASK=AGENT))
        ledger("Sales tax row for %s left blank — GL data missing for %s after the wait and retries." % (month, ", ".join(missing)))
        return 2
    figs = {s: figures(s, end) for s in STORES}
    import openpyxl
    from openpyxl.comments import Comment
    from openpyxl.styles import Font
    wb = openpyxl.load_workbook(WB)
    ws = wb["Sheet1"] if "Sheet1" in wb.sheetnames else wb.active
    rate = ws["G1"].value or 0.053
    row, existing = find_row(ws, y, m)
    if ws.cell(row, 1).value is None and not render:
        ws.cell(row, 1, LABELS[m]); ws.cell(row, 1).font = Font(name="Aptos Narrow", size=12)
    # trailing-3-month averages from the sheet (rows above with values)
    hist = {s: [] for s in STORES}
    for r in range(row - 1, 4, -1):
        for s in STORES:
            t, e = ws.cell(r, COL[s]).value, ws.cell(r, COL[s] + 1).value
            if isinstance(t, (int, float)) and len(hist[s]) < 3:
                hist[s].append((t - (e or 0)) * rate)
    due = {s: round((figs[s][0] - figs[s][1]) * rate, 2) for s in STORES}
    flags = []
    for s in STORES:
        avg = sum(hist[s]) / len(hist[s]) if hist[s] else None
        if due[s] <= 0:
            flags.append("%s taxes due is %s" % (NAMES[s], "negative" if due[s] < 0 else "zero"))
        elif avg and (due[s] > 2 * avg or due[s] < 0.5 * avg):
            flags.append("%s is %s its recent average ($%s vs $%s)" % (NAMES[s], "well above" if due[s] > avg else "well below", format(due[s], ",.2f"), format(avg, ",.2f")))
    total = round(sum(due.values()), 2)
    dm = ["%s sales tax (from the store system's month-end ledger, %s):" % (month, source)]
    dm += ["• %s — $%s due (taxable $%s, eBay $%s)" % (NAMES[s], format(due[s], ",.2f"), format(figs[s][0], ",.2f"), format(figs[s][1], ",.2f")) for s in STORES]
    dm.append("Company total: $%s. %s" % (format(total, ",.2f"), ("Worth a look before filing: " + "; ".join(flags) + ".") if flags else "Nothing out of line versus recent months."))
    text = "\n".join(dm)
    if render:
        print("=== RENDER ONLY ===\nrow %s (%s)\n%s" % (row, "already filled" if existing else "empty", text)); return 0
    if existing:
        print("row %d for %s already filled — nothing written" % (row, month)); return 0
    bk = os.path.join(os.path.dirname(WB), "_backups"); os.makedirs(bk, exist_ok=True)
    shutil.copy2(WB, os.path.join(bk, "Sales Tax.xlsx.bak-pre-%s-%s" % (start.strftime("%Y%m"), dt.datetime.now(ET).strftime("%Y%m%d-%H%M%S"))))
    note = "Source: Bravo POS Consolidated GL (post-to-accounting-gl), %s, %s %s." % (month, source, dt.datetime.now(ET).strftime("%Y-%m-%d"))
    for s in STORES:
        c = COL[s]
        ws.cell(row, c, figs[s][0]); ws.cell(row, c + 1, figs[s][1])
        ws.cell(row, c + 2, "=(%s%d-%s%d)*$G$1" % (openpyxl.utils.get_column_letter(c), row, openpyxl.utils.get_column_letter(c + 1), row))
        ws.cell(row, c + 2).number_format = '"$"#,##0.00'
        for cc in (c, c + 1):
            ws.cell(row, cc).comment = Comment(note, "sales-tax-monthly-update")
            ws.cell(row, cc).font = Font(name="Aptos Narrow", size=12)
        ws.cell(row, c + 2).font = Font(name="Aptos Narrow", size=12)
    wb.save(WB)
    p = subprocess.run([sys.executable, os.path.join(HERE, "vp_slack.py"), "dm", text], capture_output=True, text=True, timeout=60, env=dict(os.environ, VP_TASK=AGENT))
    if p.returncode != 0:
        ledger("Sales tax row for %s was filled but the summary DM did not send." % month); return 1
    print("filled row %d for %s; total $%s" % (row, month, format(total, ",.2f")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
