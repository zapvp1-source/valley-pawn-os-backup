#!/usr/bin/env python3
"""gun_audit_sheet.py — the "Valley Pawn Trends" sheet step of native monthly-gun-audit-report (2026-10-20).

update(sheet_id, period, inp, render) -> list of plain lines describing what was (or would be) written.
Rolling 12-month window, the SKILL's four tabs:
  Submission Tracker  Location | Responsible | 12 month columns (✓ / Late / —): drop the oldest month column, add <Mon YYYY>
  Audit Metrics       Location | Month | Forms Checked | Errors Found | Errors Corrected | Error Rate: drop the oldest
                      month's 5 rows, add 5 rows for this month (a store that did not submit gets no row)
  Location Summary    recomputed from the tracker: Total Submitted, On-Time, Late, Missing, Submission %, Compliance Rating
  Key Takeaways       left as it is (a judgment tab — the model-written findings stay a human/Cowork edit)
SAFETY:
  * reads every tab first and checks the header row is the expected one; any other layout = no write, a plain line.
  * writes only when fleet/state/gun_audit/SHEET_WRITE_OK exists. That file is created by a person after one --render
    has shown the planned writes are right. Until then every run behaves like --render for the sheet.
  * 2026-10-20 probe: the Sheets API answered 403 for this sheet — the Google account behind the Mac token
    (jdavis@fcfpawn.com) cannot open it. A 403 raises PermissionError with the one fix: share the sheet with
    jdavis@fcfpawn.com as Editor.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OS_DIR = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(OS_DIR), "Website", "analytics", "bin"))
WRITE_OK = os.path.join(OS_DIR, "fleet", "state", "gun_audit", "SHEET_WRITE_OK")
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
TABS = ("Submission Tracker", "Audit Metrics", "Location Summary", "Key Takeaways")


def _call(method, url, tok, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        if e.code == 403:
            raise PermissionError("the Trends sheet is not shared with jdavis@fcfpawn.com (Sheets API 403) — share it as Editor")
        raise


def _values(sid, tab, tok):
    rng = urllib.parse.quote("'%s'!A1:Z200" % tab)
    return _call("GET", "https://sheets.googleapis.com/v4/spreadsheets/%s/values/%s" % (sid, rng), tok).get("values", [])


def rating(pct):
    return "Excellent" if pct >= 90 else "Good" if pct >= 75 else "Needs Improvement" if pct >= 50 else "Poor"


def update(sid, period, inp, render):
    import google_auth
    tok = google_auth.access_token(require=SCOPE)
    lines = []
    tabs = {t: _values(sid, t, tok) for t in TABS}
    tr, am = tabs["Submission Tracker"], tabs["Audit Metrics"]
    if not tr or [c.strip() for c in tr[0][:2]] != ["Location", "Responsible"]:
        return ["Submission Tracker layout is not Location | Responsible | months — nothing written"]
    if not am or [c.strip() for c in am[0][:3]] != ["Location", "Month", "Forms Checked"]:
        return ["Audit Metrics layout is not Location | Month | Forms Checked ... — nothing written"]
    y, m = map(int, period.split("-"))
    import datetime as dt
    col = dt.date(y, m, 1).strftime("%b %Y")
    by = {s["store"]: s for s in inp["stores"]}
    deadline = dt.date.fromisoformat(inp["deadline"])
    hdr = tr[0]
    if col in hdr:
        lines.append("Submission Tracker already has %s — tracker unchanged" % col)
        new_tr = tr
    else:
        new_hdr = hdr[:2] + hdr[3:] + [col]
        new_tr = [new_hdr]
        for row in tr[1:]:
            row = row + [""] * (len(hdr) - len(row))
            s = by.get(row[0].strip())
            mark = "—" if not s or not s.get("submitted") else ("✓" if dt.date.fromisoformat(s["submitted"]) <= deadline else "Late")
            new_tr.append(row[:2] + row[3:] + [mark])
        lines.append("Submission Tracker: drop %r, add %r (%s)" % (hdr[2], col, ", ".join("%s %s" % (r[0], r[-1]) for r in new_tr[1:])))
    months_kept = new_tr[0][2:]
    if any(len(r) > 1 and r[1].strip() == col for r in am[1:]):
        new_am = am
        lines.append("Audit Metrics already has %s rows — unchanged" % col)
    else:
        keep = [r for r in am[1:] if len(r) > 1 and r[1].strip() in months_kept]
        add = []
        for s in inp["stores"]:
            if s.get("submitted"):
                rate = "%.2f%%" % (s["errors_found"] * 100.0 / s["forms_checked"])
                add.append([s["store"], col, str(s["forms_checked"]), str(s["errors_found"]), str(s["errors_corrected"]), rate])
        new_am = [am[0]] + keep + add
        lines.append("Audit Metrics: %d rows dropped (older than the 12-month window), %d added for %s" % (len(am) - 1 - len(keep), len(add), col))
    summ = [["Location", "Responsible", "Total Submitted", "On-Time", "Late", "Missing", "Submission %", "Compliance Rating"]]
    for r in new_tr[1:]:
        marks = r[2:]
        on, late, miss = marks.count("✓"), marks.count("Late"), sum(1 for x in marks if x.strip() in ("—", "-", ""))
        tot = on + late
        p = 100.0 * tot / len(marks) if marks else 0
        summ.append([r[0], r[1], str(tot), str(on), str(late), str(miss), "%.0f%%" % p, rating(p)])
    lines.append("Location Summary recomputed: " + "; ".join("%s %s/%s" % (r[0], r[2], len(months_kept)) for r in summ[1:]))
    if render or not os.path.exists(WRITE_OK):
        lines.append("NOT WRITTEN (%s)" % ("render" if render else "SHEET_WRITE_OK not present yet"))
        return lines
    data = [{"range": "'Submission Tracker'!A1", "values": new_tr}, {"range": "'Audit Metrics'!A1", "values": new_am},
            {"range": "'Location Summary'!A1", "values": summ}]
    for t, rows in (("Audit Metrics", new_am), ("Submission Tracker", new_tr)):
        _call("POST", "https://sheets.googleapis.com/v4/spreadsheets/%s/values/%s:clear" % (sid, urllib.parse.quote("'%s'!A1:Z200" % t)), tok, {})
    _call("POST", "https://sheets.googleapis.com/v4/spreadsheets/%s/values:batchUpdate" % sid, tok,
          {"valueInputOption": "USER_ENTERED", "data": data})
    lines.append("WRITTEN")
    return lines
