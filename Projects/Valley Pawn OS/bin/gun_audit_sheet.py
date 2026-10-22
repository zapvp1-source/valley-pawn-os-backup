#!/usr/bin/env python3
"""gun_audit_sheet.py — the "Valley Pawn Trends" sheet step of native monthly-gun-audit-report.

2026-10-21 rewrite (the 3 problems the first write test found, CHANGELOG "Trends sheet moved to jdavis@fcfpawn.com"):
  * LABEL = the SUBMISSION month (the cycle month = the month of the 15th deadline): the September audit, submitted
    in October, is "October 2026". That is the sheet's own convention — the Submission Tracker's history (its
    "Apr 2026" column is the all-on-time March audit the Key Takeaways "April 2026" note describes), the 10/16 cycle
    ("October 2026" / "Oct 2026") and the Key Takeaways headings all name the cycle month. Both tabs share one
    set of month keys, so Audit Metrics uses the same month. Existing labels are never changed.
  * Month labels are compared as DATES (serials, "Jul 2026", "July 2026", "2026-07" all normalise to (2026, 7)),
    never as text.
  * Location Summary only touches the five store rows (never "On-Time Rate", totals or blanks); it keeps the
    sheet's own Responsible names and only changes cells whose value actually changes.
  * Rolling 12: after adding a month, the ONE oldest month is dropped only when the tab then holds more than 12
    months AND that month is outside the 12-month window ending at the new month. Never more than one per run.
  * Additive cell-level writes (one batchUpdate: insert/append + delete + changed cells). No tab is cleared or
    rewritten; new cells copy the number format of their neighbour (mmmm yyyy / mmm yyyy / 0.00% / m/d).
  * Re-running a cycle the sheet already has = "already recorded, no change" and no write at all.

update(sheet_id, period, inp, render) -> list of plain lines describing what was (or would be) written.
Writes only when fleet/state/gun_audit/SHEET_WRITE_OK exists and render is False.

CLI (render-only, never writes):
  gun_audit_sheet.py --test <format_input.json> [--offline]
      plans against the live sheet (or, --offline, against fleet/state/trends_migration/source_typed.json),
      simulates the writes on a copy and prints the result. Exit 0 = plan is consistent.
"""
import copy
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OS_DIR = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(OS_DIR), "Website", "analytics", "bin"))
WRITE_OK = os.path.join(OS_DIR, "fleet", "state", "gun_audit", "SHEET_WRITE_OK")
TYPED = os.path.join(OS_DIR, "fleet", "state", "trends_migration", "source_typed.json")
TRENDS = "16Tzy6C-JlmJ-XIo-IrVwUOqSmOekIQ46K1b3t2nggWo"
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
API = "https://sheets.googleapis.com/v4/spreadsheets"
TABS = ("Submission Tracker", "Audit Metrics", "Location Summary")
STORES = ("Waynesboro", "Harrisonburg", "Culpeper", "Roanoke", "Lexington")
WINDOW = 12
EPOCH = dt.date(1899, 12, 30)
MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


# ---------------------------------------------------------------- month handling (dates, never text)
def serial(d):
    return float((d - EPOCH).days)


def from_serial(n):
    return EPOCH + dt.timedelta(days=int(n))


def month_key(v):
    """(year, month) for a month label in any of the sheet's forms, or None. 45901 / 'Sep 2025' / 'September 2025' /
    'Sept 2025' / '2025-09' / '9/2025' -> (2025, 9)."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        if 20000 < v < 80000:
            d = from_serial(v)
            return (d.year, d.month)
        return None
    s = str(v).strip().lower()
    m = re.fullmatch(r"(\d{4})-(\d{1,2})(?:-\d{1,2})?", s)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    m = re.fullmatch(r"(\d{1,2})/(\d{4})", s)
    if m:
        return (int(m.group(2)), int(m.group(1)))
    m = re.fullmatch(r"([a-z]{3,9})\.?,?\s+(\d{4})", s)
    if m and m.group(1)[:3] in MONTHS:
        return (int(m.group(2)), MONTHS[m.group(1)[:3]])
    return None


def add_months(k, n):
    i = k[0] * 12 + (k[1] - 1) + n
    return (i // 12, i % 12 + 1)


def mname(k, long=True):
    return dt.date(k[0], k[1], 1).strftime("%B %Y" if long else "%b %Y")


# ---------------------------------------------------------------- snapshot: {tab: {"id", "rows", "cols", "grid": [[cell]]}}
# cell = {"v": str | float | None, "fmt": userEnteredFormat dict}
def _cell(v=None, fmt=None):
    return {"v": v, "fmt": copy.deepcopy(fmt) if fmt else {}}


def _get(c):
    return c["v"] if c else None


def _text(c):
    v = _get(c)
    return "" if v is None else (v.strip() if isinstance(v, str) else v)


def snapshot_offline():
    typed = json.load(open(TYPED, encoding="utf-8"))
    F = typed["F"]
    snap = {}
    for i, t in enumerate(TABS):
        grid = []
        for ri, r in enumerate(typed["T"][t]):
            row = []
            for c in r:
                fmt = {"textFormat": {"bold": True}} if ri == 0 else {}
                if isinstance(c, list):
                    p = F[c[1]]
                    fmt["numberFormat"] = {"type": "PERCENT" if "%" in p else "DATE", "pattern": p}
                    row.append(_cell(float(c[0]), fmt))
                else:
                    row.append(_cell(float(c) if isinstance(c, (int, float)) and not isinstance(c, bool) else c, fmt))
            grid.append(row)
        snap[t] = {"id": 1000 + i, "rows": max(len(grid), 1000), "cols": 26, "grid": grid}
    return snap


def _call(method, url, tok, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        if e.code == 403:
            raise PermissionError("the Trends sheet is not shared with jdavis@fcfpawn.com (Sheets API 403) — share it as Editor")
        raise RuntimeError("Sheets API %s %s -> HTTP %s %s" % (method, url.split("?")[0], e.code, e.read().decode()[:300]))


def snapshot_live(sid, tok):
    q = urllib.parse.urlencode([("ranges", "'%s'!A1:Z300" % t) for t in TABS] + [
        ("includeGridData", "true"),
        ("fields", "sheets(properties(sheetId,title,gridProperties(rowCount,columnCount)),"
                   "data(rowData(values(effectiveValue,userEnteredFormat))))")])
    res = _call("GET", "%s/%s?%s" % (API, sid, q), tok)
    snap = {}
    for sh in res.get("sheets", []):
        p = sh["properties"]
        if p["title"] not in TABS:
            continue
        grid = []
        for rd in (sh.get("data") or [{}])[0].get("rowData", []) or []:
            row = []
            for c in rd.get("values", []) or []:
                ev = c.get("effectiveValue") or {}
                v = ev.get("numberValue", ev.get("stringValue", ev.get("boolValue")))
                row.append(_cell(float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v,
                                 c.get("userEnteredFormat")))
            grid.append(row)
        while grid and all(_get(c) in (None, "") for c in grid[-1]):
            grid.pop()
        snap[p["title"]] = {"id": p["sheetId"], "rows": p["gridProperties"]["rowCount"],
                            "cols": p["gridProperties"]["columnCount"], "grid": grid}
    return snap


# ---------------------------------------------------------------- plan
def rating(pct, old_pct=None, old=None):
    """The sheet's own scale (Location Summary + Key Takeaways): 100/92/83% Good, 67% Needs Improvement, 58% Poor.
    No 'Excellent' has ever been used. An unchanged percentage keeps the rating already on the sheet."""
    if old and old_pct is not None and round(old_pct * 100) == round(pct * 100):
        return old
    return "Good" if pct >= 0.75 else "Needs Improvement" if pct >= 0.60 else "Poor"


def _uc(sheet, r, c, cells, fields="userEnteredValue,userEnteredFormat"):
    rows = [{"values": [_api_cell(x, fields) for x in row]} for row in cells]
    return {"updateCells": {"start": {"sheetId": sheet, "rowIndex": r, "columnIndex": c}, "rows": rows, "fields": fields}}


def _api_cell(x, fields):
    d = {}
    v = x["v"]
    if v is None or v == "":
        d["userEnteredValue"] = {}
    elif isinstance(v, str):
        d["userEnteredValue"] = {"stringValue": v}
    else:
        d["userEnteredValue"] = {"numberValue": v}
    if "userEnteredFormat" in fields:
        d["userEnteredFormat"] = x["fmt"] or {}
    return d


def plan(snap, inp):
    """-> (lines, requests). requests is [] when nothing changes. Raises nothing for layout problems: it returns a
    line and no requests."""
    lines, reqs = [], []
    for t in TABS:
        if t not in snap or not snap[t]["grid"]:
            return ["%s tab missing or empty — nothing written" % t], []
    tr, am, ls = snap["Submission Tracker"], snap["Audit Metrics"], snap["Location Summary"]
    trg, amg, lsg = tr["grid"], am["grid"], ls["grid"]
    if [_text(c) for c in trg[0][:2]] != ["Location", "Responsible"]:
        return ["Submission Tracker layout is not Location | Responsible | months — nothing written"], []
    if [_text(c) for c in amg[0][:6]] != ["Location", "Month", "Forms Checked", "Errors Found", "Errors Corrected", "Error Rate"]:
        return ["Audit Metrics layout is not Location | Month | Forms Checked | Errors Found | Errors Corrected | Error Rate — nothing written"], []
    if [_text(c) for c in lsg[0][:8]] != ["Location", "Responsible", "Total Submitted", "On-Time", "Late", "Missing", "Submission %", "Compliance Rating"]:
        return ["Location Summary layout is not the expected 8 columns — nothing written"], []

    deadline = dt.date.fromisoformat(inp["deadline"])
    new = (deadline.year, deadline.month)            # the cycle / submission month
    win_start = add_months(new, -(WINDOW - 1))
    by = {s["store"]: s for s in inp["stores"]}

    def mark(store):
        s = by.get(store)
        if not s or not s.get("submitted"):
            return "—"
        return "✓" if dt.date.fromisoformat(s["submitted"]) <= deadline else "Late"

    # ---- Submission Tracker (column per month)
    hdr = trg[0]
    tcols = [(i, month_key(_get(c))) for i, c in enumerate(hdr) if i >= 2 and month_key(_get(c))]
    bad = [i for i, c in enumerate(hdr) if i >= 2 and _text(c) != "" and not month_key(_get(c))]
    if bad:
        return ["Submission Tracker has a header that is not a month (column %d) — nothing written" % (bad[0] + 1)], []
    tmonths = [k for _, k in tcols]
    if len(set(tmonths)) != len(tmonths):
        return ["Submission Tracker has the same month twice — nothing written"], []
    store_rows = [ri for ri, r in enumerate(trg) if ri > 0 and r and _text(r[0]) in STORES]
    other_rows = [ri for ri, r in enumerate(trg) if ri > 0 and r and _text(r[0]) and _text(r[0]) not in STORES]
    rate_row = next((ri for ri in other_rows if str(_text(trg[ri][0])).lower().startswith("on-time")), None)
    if tmonths and new < max(tmonths) and new not in tmonths:
        return ["%s is older than the newest month on the sheet (%s) — nothing written" % (mname(new), mname(max(tmonths)))], []
    tr_after = {ri: [_text(trg[ri][i]) if i < len(trg[ri]) else "" for i, _ in tcols] for ri in store_rows}
    tr_months_after = list(tmonths)
    if new in tmonths:
        lines.append("Submission Tracker: %s already recorded — no change" % mname(new))
        col = tcols[tmonths.index(new)][0]
        diff = ["%s sheet %s / form %s" % (_text(trg[ri][0]), _text(trg[ri][col]) if col < len(trg[ri]) else "", mark(_text(trg[ri][0])))
                for ri in store_rows if (_text(trg[ri][col]) if col < len(trg[ri]) else "") != mark(_text(trg[ri][0]))]
        if diff:
            lines.append("  note (left as is): the sheet's %s marks differ from this run: %s" % (mname(new), "; ".join(diff)))
    else:
        last = max(i for i, _ in tcols) if tcols else 1
        c_new = last + 1
        ref = lambda ri: trg[ri][last] if last < len(trg[ri]) else _cell()
        if c_new >= tr["cols"]:
            reqs.append({"appendDimension": {"sheetId": tr["id"], "dimension": "COLUMNS", "length": 1}})
        hdr_cell = _cell(serial(dt.date(new[0], new[1], 1)), ref(0)["fmt"])
        colcells = []
        for ri in range(len(trg)):
            if ri == 0:
                colcells.append(hdr_cell)
            elif ri in store_rows:
                m = mark(_text(trg[ri][0]))
                colcells.append(_cell(m, ref(ri)["fmt"]))
                tr_after[ri].append(m)
            elif ri == rate_row:
                n = sum(1 for x in store_rows if mark(_text(trg[x][0])) == "✓")
                d = len(store_rows)
                # the sheet's own "n/5" cells were typed in and Sheets stored them as dates (m/d); same here
                v = serial(dt.date(new[0], n, d)) if 1 <= n <= 12 and 1 <= d <= 28 else "%d/%d" % (n, d)
                colcells.append(_cell(v, ref(ri)["fmt"]))
            else:
                colcells.append(_cell(None, ref(ri)["fmt"]))
        reqs.append({"_tab": "tr", **_uc(tr["id"], 0, c_new, [[c] for c in colcells])})
        tr_months_after.append(new)
        lines.append("Submission Tracker: add %r (%s)" % (mname(new), ", ".join("%s %s" % (_text(trg[ri][0]), tr_after[ri][-1]) for ri in store_rows)))
        oldest = min(tr_months_after)
        if len(tr_months_after) > WINDOW and oldest < win_start:
            ci = tcols[tmonths.index(oldest)][0]
            reqs.append({"_tab": "tr", "deleteDimension": {"range": {"sheetId": tr["id"], "dimension": "COLUMNS", "startIndex": ci, "endIndex": ci + 1}}})
            idx = tr_months_after.index(oldest)
            tr_months_after.pop(idx)
            for ri in store_rows:
                tr_after[ri].pop(idx)
            shown = _text(hdr[ci]) if isinstance(_get(hdr[ci]), str) else mname(oldest, (hdr[ci]["fmt"].get("numberFormat") or {}).get("pattern", "").startswith("mmmm"))
            lines.append("Submission Tracker: drop the oldest month %r (outside the 12 months %s – %s)" % (shown, mname(win_start, False), mname(new, False)))
        else:
            lines.append("Submission Tracker: no month dropped (%d months, oldest %s inside the window)" % (len(tr_months_after), mname(oldest)))

    # ---- Audit Metrics (row per store per month)
    rows = [(ri, _text(r[0]) if r else "", month_key(_get(r[1])) if len(r) > 1 else None) for ri, r in enumerate(amg) if ri > 0]
    rows = [x for x in rows if x[1] or x[2]]
    amonths = sorted({k for _, _, k in rows if k})
    ops = []        # (row index, order, request)   order 0 = delete (runs first at equal index), 1 = insert
    have = {(s, k) for _, s, k in rows}
    added = []
    for s in inp["stores"]:
        st = s["store"]
        if (st, new) in have:
            continue
        grp = [ri for ri, n, _ in rows if n == st]
        at = (max(grp) + 1) if grp else (max([ri for ri, _, _ in rows] or [0]) + 1)
        refrow = amg[at - 1] if at - 1 < len(amg) else []
        rf = lambda i: (refrow[i]["fmt"] if i < len(refrow) else {})
        vals = [st, serial(dt.date(new[0], new[1], 1))]
        if s.get("submitted"):
            fc, ef, ec = s["forms_checked"], s["errors_found"], s["errors_corrected"]
            vals += [float(fc), float(ef), float(ec), round(ef / fc, 4) if fc else None]
        else:
            vals += [None, None, None, None]       # the sheet's convention for a store that did not submit
        cells = [_cell(v, rf(i)) for i, v in enumerate(vals)]
        if at >= am["rows"]:                          # past the grid's last row: grow it (insert needs an existing index)
            ops.append((at, 1, {"appendDimension": {"sheetId": am["id"], "dimension": "ROWS", "length": 1}}))
        else:
            ops.append((at, 1, {"insertDimension": {"range": {"sheetId": am["id"], "dimension": "ROWS", "startIndex": at, "endIndex": at + 1}, "inheritFromBefore": True}}))
        ops.append((at, 1.5, _uc(am["id"], at, 0, [cells])))
        added.append(st if s.get("submitted") else "%s (blank, no audit)" % st)
    am_months_after = sorted(set(amonths) | ({new} if added else set()))
    if not added:
        lines.append("Audit Metrics: %s already recorded for all %d stores — no change" % (mname(new, False), len(inp["stores"])))
    else:
        lines.append("Audit Metrics: add %d rows for %r: %s" % (len(added), mname(new, False), ", ".join(added)))
        oldest = min(am_months_after)
        if len(am_months_after) > WINDOW and oldest < win_start:
            dels = [ri for ri, _, k in rows if k == oldest]
            for ri in dels:
                ops.append((ri, 0, {"deleteDimension": {"range": {"sheetId": am["id"], "dimension": "ROWS", "startIndex": ri, "endIndex": ri + 1}}}))
            am_months_after.remove(oldest)
            lines.append("Audit Metrics: drop the %d rows of the oldest month %r (outside the 12-month window)" % (len(dels), mname(oldest, False)))
        else:
            lines.append("Audit Metrics: no month dropped (%d months, oldest %s inside the window)" % (len(am_months_after), mname(oldest, False)))
    # descending row index; at the same index the delete goes before the insert, the insert before its fill
    for _, _, rq in sorted(ops, key=lambda x: (-x[0], x[1])):
        reqs.append({"_tab": "am", **rq})

    # ---- Location Summary (store rows only, changed cells only)
    tr_names = {_text(trg[ri][0]): ri for ri in store_rows}
    changes = []
    seen = set()
    for ri, r in enumerate(lsg):
        if ri == 0 or not r:
            continue
        st = _text(r[0])
        if st not in STORES or st not in tr_names:
            continue                                   # On-Time Rate, totals, notes, blanks: never touched
        seen.add(st)
        marks = tr_after[tr_names[st]]
        on, late = marks.count("✓"), marks.count("Late")
        miss = len(marks) - on - late
        tot = on + late
        pct = round(tot / len(marks), 2) if marks else 0.0
        old = [_get(r[i]) if i < len(r) else None for i in range(8)]
        want = {2: float(tot), 3: float(on), 4: float(late), 5: float(miss), 6: pct,
                7: rating(pct, old[6] if isinstance(old[6], float) else None, old[7])}
        for ci, v in want.items():
            ov = old[ci]
            same = (isinstance(ov, float) and isinstance(v, float) and abs(ov - v) < 0.005) or ov == v
            if not same:
                changes.append((ri, ci, v, ov, st))
    for ri, ci, v, ov, st in changes:
        reqs.append({"_tab": "ls", **_uc(ls["id"], ri, ci, [[_cell(v)]], fields="userEnteredValue")})
    if not changes:
        lines.append("Location Summary: unchanged (%s)" % "; ".join("%s %d/%d" % (st, tr_after[tr_names[st]].count("✓") + tr_after[tr_names[st]].count("Late"), len(tr_after[tr_names[st]])) for st in STORES if st in seen))
    else:
        hd = ["", "", "Total Submitted", "On-Time", "Late", "Missing", "Submission %", "Compliance Rating"]
        lines.append("Location Summary: %d cells change: %s" % (len(changes), "; ".join("%s %s %s -> %s" % (st, hd[ci], _fmtv(ov, ci), _fmtv(v, ci)) for _, ci, v, ov, st in changes)))
    if not reqs:
        lines.insert(0, "ALREADY RECORDED — %s cycle (%s audit) is on the sheet, no change" % (mname(new), mname(add_months(new, -1))))
    return lines, reqs


def _fmtv(v, ci):
    if ci == 6 and isinstance(v, float):
        return "%.0f%%" % (v * 100)
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)


# ---------------------------------------------------------------- simulate (render self-check) and write
def simulate(snap, reqs):
    """Apply the requests to a deep copy of the snapshot (same semantics as the Sheets API for the 4 request kinds
    used here) and return it."""
    s = copy.deepcopy(snap)
    ids = {v["id"]: k for k, v in s.items()}
    for rq in reqs:
        rq = {k: v for k, v in rq.items() if k != "_tab"}
        (kind, b), = rq.items()
        if kind == "appendDimension":
            s[ids[b["sheetId"]]]["cols" if b["dimension"] == "COLUMNS" else "rows"] += b["length"]
            continue
        rng = b.get("range") or b.get("start")
        g = s[ids[rng["sheetId"]]]["grid"]
        if kind == "insertDimension":
            g.insert(rng["startIndex"], [])
        elif kind == "deleteDimension" and rng["dimension"] == "ROWS":
            del g[rng["startIndex"]]
        elif kind == "deleteDimension":
            for r in g:
                if rng["startIndex"] < len(r):
                    del r[rng["startIndex"]]
        elif kind == "updateCells":
            for dr, row in enumerate(b["rows"]):
                ri = rng["rowIndex"] + dr
                while len(g) <= ri:
                    g.append([])
                for dc, c in enumerate(row["values"]):
                    ci = rng["columnIndex"] + dc
                    while len(g[ri]) <= ci:
                        g[ri].append(_cell())
                    uv = c.get("userEnteredValue") or {}
                    v = uv.get("numberValue", uv.get("stringValue"))
                    g[ri][ci] = _cell(v, c.get("userEnteredFormat", g[ri][ci]["fmt"]))
    return s


def check(after, new):
    """Consistency of the simulated result: -> list of problems (empty = ok)."""
    p = []
    trg, amg = after["Submission Tracker"]["grid"], after["Audit Metrics"]["grid"]
    tm = [month_key(_get(c)) for c in trg[0][2:] if month_key(_get(c))]
    am = sorted({month_key(_get(r[1])) for r in amg[1:] if len(r) > 1 and month_key(_get(r[1]))})
    if len(tm) > WINDOW:
        p.append("Tracker holds %d months" % len(tm))
    if tm != sorted(tm):
        p.append("Tracker months out of order")
    if len(am) > WINDOW:
        p.append("Audit Metrics holds %d months" % len(am))
    if new not in tm or new not in am:
        p.append("%s missing after the write" % mname(new))
    if set(tm) != set(am):
        p.append("Tracker and Audit Metrics months differ: %s vs %s" % ([mname(k, False) for k in tm], [mname(k, False) for k in am]))
    for st in STORES:
        ks = [month_key(_get(r[1])) for r in amg[1:] if r and _text(r[0]) == st]
        if ks != sorted(ks) or len(set(ks)) != len(ks):
            p.append("Audit Metrics %s rows out of order or duplicated" % st)
    return p


def update(sid, period, inp, render, snap=None):
    tok = None
    if snap is None:
        import google_auth
        tok = google_auth.access_token(require=SCOPE)
        snap = snapshot_live(sid, tok)
    lines, reqs = plan(snap, inp)
    deadline = dt.date.fromisoformat(inp["deadline"])
    new = (deadline.year, deadline.month)
    if not reqs:
        return lines
    after = simulate(snap, reqs)
    probs = check(after, new)
    again, more = plan(after, inp)
    if more:
        probs.append("a second run would still change %d things" % len(more))
    tm = [month_key(_get(c)) for c in after["Submission Tracker"]["grid"][0][2:] if month_key(_get(c))]
    lines.append("after: %d months %s – %s on both tabs" % (len(tm), mname(min(tm), False), mname(max(tm), False)) if tm else "after: no months")
    if probs:
        lines.append("PLAN FAILED its self-check — nothing written: " + "; ".join(probs))
        return lines
    if render or not os.path.exists(WRITE_OK):
        lines.append("NOT WRITTEN (%s)" % ("render" if render else "SHEET_WRITE_OK not present yet"))
        return lines
    body = [{k: v for k, v in rq.items() if k != "_tab"} for rq in reqs]
    _call("POST", "%s/%s:batchUpdate" % (API, sid), tok, {"requests": body})
    post, rest = plan(snapshot_live(sid, tok), inp)
    lines.append("WRITTEN (%d requests); re-read: %s" % (len(body), "ok, already recorded" if not rest else "STILL %d CHANGES — check the sheet" % len(rest)))
    return lines


def main():
    if "--test" not in sys.argv:
        print(__doc__)
        return 2
    inp = json.load(open(sys.argv[sys.argv.index("--test") + 1], encoding="utf-8"))
    offline = "--offline" in sys.argv
    snap = snapshot_offline() if offline else None
    print("SHEET-TEST %s, deadline %s (render, nothing written)" % ("offline copy (source_typed.json)" if offline else TRENDS, inp["deadline"]))
    lines = update(TRENDS, None, inp, True, snap=snap)
    for ln in lines:
        print("SHEET", ln)
    return 1 if any("nothing written" in ln and "NOT WRITTEN" not in ln for ln in lines) else 0


if __name__ == "__main__":
    sys.exit(main())
