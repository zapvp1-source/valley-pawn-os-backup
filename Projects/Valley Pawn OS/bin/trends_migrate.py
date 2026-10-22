#!/usr/bin/env python3
"""trends_migrate.py — move "Valley Pawn Trends" into jdavis@fcfpawn.com (2026-10-21).

Joshua's rule (10/21): every Valley Pawn file lives in the jdavis@fcfpawn.com Google account, nothing in the
fullcirclepawn@gmail.com Drive. The original (1sLid9zjLUkH..., owned by fullcirclepawn@gmail.com) is NOT touched
by this script — it only reads the local extract made from Chrome on 10/21:
    fleet/state/trends_migration/source_typed.json   typed cell values + number formats (from the xlsx export)
    fleet/state/trends_migration/0N_*.csv           the source's own CSV export per tab (display values)
    fleet/state/trends_migration/manifest.json      tab order, gids, row/col counts, formatting notes

Modes (one per run):
    (none)            render: print the plan, create nothing
    --live            create the new spreadsheet with the Mac's Google token (Sheets API → jdavis's My Drive),
                      write every tab, then run --verify. Refuses if new_sheet.json already exists (no second copy).
    --verify          read every tab of the new sheet back and compare cell by cell with the source CSVs
                      (FORMATTED values) and with source_typed.json (UNFORMATTED values). Writes verify.json.
    --sheet-test P    render-only call of gun_audit_sheet.update(<new id>, P, fleet/state/gun_audit/P_format_input.json)
                      — prints the planned writes; never writes (render=True).
Source had: 0 formulas, 0 frozen rows/cols, 0 merges, no bold, default Arial 10. The copy keeps that, except the
header row (row 1) is bolded as Joshua asked.
"""
import csv
import datetime as dt
import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OS_DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(OS_DIR), "Website", "analytics", "bin"))
MIG = os.path.join(OS_DIR, "fleet", "state", "trends_migration")
NEW = os.path.join(MIG, "new_sheet.json")
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
TITLE = "Valley Pawn Trends"
SOURCE_ID = "1sLid9zjLUkH-B8MOE5Fr_aemw35bxyAbtuUz4BTVA6s"
API = "https://sheets.googleapis.com/v4/spreadsheets"


def tok():
    import google_auth
    return google_auth.access_token(require=SCOPE)


def call(method, url, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": "Bearer " + tok(), "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=90))
    except urllib.error.HTTPError as e:
        raise RuntimeError("%s %s -> HTTP %s %s" % (method, url.split("?")[0], e.code, e.read().decode()[:400]))


def load():
    man = json.load(open(os.path.join(MIG, "manifest.json"), encoding="utf-8"))
    typed = json.load(open(os.path.join(MIG, "source_typed.json"), encoding="utf-8"))
    csvs = {}
    for t in man["tabs"]:
        txt = open(os.path.join(MIG, t["csv"]), encoding="utf-8", newline="").read()
        csvs[t["name"]] = [r for r in csv.reader(io.StringIO(txt))]
    return man, typed, csvs


def pattern_type(fmt):
    return "PERCENT" if "%" in fmt else "DATE"


def cell_data(c, F, bold):
    d = {}
    if c is None:
        pass
    elif isinstance(c, str):
        d["userEnteredValue"] = {"stringValue": c}
    elif isinstance(c, bool):
        d["userEnteredValue"] = {"boolValue": c}
    elif isinstance(c, list):
        fmt = F[c[1]]
        d["userEnteredValue"] = {"numberValue": c[0]}
        d["userEnteredFormat"] = {"numberFormat": {"type": pattern_type(fmt), "pattern": fmt}}
    else:
        d["userEnteredValue"] = {"numberValue": c}
    if bold:
        d.setdefault("userEnteredFormat", {})["textFormat"] = {"bold": True}
    return d


def plan(man, typed):
    lines = ["CREATE spreadsheet %r in the Google account behind the Mac token (jdavis@fcfpawn.com), locale en_US, America/New_York" % TITLE]
    for t in man["tabs"]:
        rows = typed["T"][t["name"]]
        n = sum(1 for r in rows for c in r if c is not None)
        lines.append("  tab %d %-18s %3d rows x %2d cols, %4d non-empty cells, row 1 bold, no freeze" % (t["index"], t["name"], t["rows"], t["cols"], n))
    lines.append("  formulas: %s (none to recreate); number formats kept: %s" % (man["formulas"], ", ".join(typed["F"])))
    return lines


def norm(rows):
    out = [list(r) for r in rows]
    for r in out:
        while r and r[-1] == "":
            r.pop()
    while out and not out[-1]:
        out.pop()
    return out


def verify(sid, man, typed, csvs):
    meta = call("GET", "%s/%s?fields=properties.title,sheets.properties" % (API, sid))
    titles = [s["properties"]["title"] for s in meta["sheets"]]
    want = [t["name"] for t in man["tabs"]]
    rep = {"sheet_id": sid, "title": meta["properties"]["title"], "tab_order_ok": titles == want, "tabs": {}, "mismatches": 0}
    ranges = ["'%s'!A1:Z1000" % t for t in want]
    q = "&".join("ranges=" + urllib.parse.quote(r) for r in ranges)
    fv = call("GET", "%s/%s/values:batchGet?%s&valueRenderOption=FORMATTED_VALUE" % (API, sid, q))["valueRanges"]
    uv = call("GET", "%s/%s/values:batchGet?%s&valueRenderOption=UNFORMATTED_VALUE" % (API, sid, q))["valueRanges"]
    for i, name in enumerate(want):
        got = norm(fv[i].get("values", []))
        exp = norm(csvs[name])
        mm = []
        for r in range(max(len(got), len(exp))):
            g = got[r] if r < len(got) else []
            e = exp[r] if r < len(exp) else []
            for c in range(max(len(g), len(e))):
                gv = g[c] if c < len(g) else ""
                ev = e[c] if c < len(e) else ""
                if gv != ev:
                    mm.append({"cell": "R%dC%d" % (r + 1, c + 1), "kind": "formatted", "source": ev, "new": gv})
        ug = uv[i].get("values", [])
        for r, row in enumerate(typed["T"][name]):
            for c, cv in enumerate(row):
                if cv is None:
                    continue
                want_v = cv[0] if isinstance(cv, list) else cv
                have = ug[r][c] if r < len(ug) and c < len(ug[r]) else None
                if isinstance(want_v, (int, float)) and not isinstance(want_v, bool):
                    ok = isinstance(have, (int, float)) and abs(have - want_v) < 1e-9
                else:
                    ok = have == want_v
                if not ok:
                    mm.append({"cell": "R%dC%d" % (r + 1, c + 1), "kind": "typed", "source": want_v, "new": have})
        cells = sum(len(r) for r in exp)
        rep["tabs"][name] = {"rows_source": len(exp), "rows_new": len(got), "cells_compared": cells,
                             "typed_cells_compared": sum(1 for r in typed["T"][name] for x in r if x is not None),
                             "mismatches": len(mm), "first_mismatches": mm[:10]}
        rep["mismatches"] += len(mm)
    rep["ok"] = rep["tab_order_ok"] and rep["mismatches"] == 0
    json.dump(rep, open(os.path.join(MIG, "verify.json"), "w"), indent=1, ensure_ascii=False)
    for name, t in rep["tabs"].items():
        print("VERIFY %-18s rows %d/%d  cells %d  typed %d  mismatches %d" % (name, t["rows_new"], t["rows_source"], t["cells_compared"], t["typed_cells_compared"], t["mismatches"]))
    print("VERIFY tab order ok:", rep["tab_order_ok"], "| total mismatches:", rep["mismatches"], "| RESULT:", "PASS" if rep["ok"] else "FAIL")
    return rep


def who():
    """Best-effort: which account owns the token / the new file (needs email or drive scope; silent if not)."""
    out = {}
    try:
        j = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/tokeninfo?access_token=" + tok(), timeout=30))
        out["token_email"] = j.get("email")
        out["token_scopes"] = j.get("scope")
    except Exception as e:
        out["token_email_error"] = str(e)[:120]
    return out


def owner(sid):
    try:
        j = call("GET", "https://www.googleapis.com/drive/v3/files/%s?fields=owners(emailAddress),name" % sid)
        return [o.get("emailAddress") for o in j.get("owners", [])]
    except Exception as e:
        return "unknown (%s)" % str(e)[:160]


def live(man, typed):
    if os.path.exists(NEW):
        print("REFUSED: %s exists — the new sheet was already created: %s" % (NEW, open(NEW).read().strip()))
        return None
    sheets = [{"properties": {"title": t["name"], "index": t["index"]}} for t in man["tabs"]]
    res = call("POST", API, {"properties": {"title": TITLE, "locale": "en_US", "timeZone": "America/New_York"}, "sheets": sheets})
    sid = res["spreadsheetId"]
    ids = {s["properties"]["title"]: s["properties"]["sheetId"] for s in res["sheets"]}
    rec = {"id": sid, "url": res.get("spreadsheetUrl"), "created": dt.datetime.now().isoformat(timespec="seconds"),
           "source_id": SOURCE_ID, "sheet_ids": ids}
    json.dump(rec, open(NEW, "w"), indent=1)
    print("CREATED", sid, rec["url"])
    F = typed["F"]
    reqs = []
    for t in man["tabs"]:
        rows = typed["T"][t["name"]]
        reqs.append({"updateCells": {"start": {"sheetId": ids[t["name"]], "rowIndex": 0, "columnIndex": 0},
                                     "rows": [{"values": [cell_data(c, F, r == 0) for c in row]} for r, row in enumerate(rows)],
                                     "fields": "userEnteredValue,userEnteredFormat"}})
    call("POST", "%s/%s:batchUpdate" % (API, sid), {"requests": reqs})
    print("WRITTEN", len(reqs), "tabs")
    rec.update(who())
    rec["owners"] = owner(sid)
    json.dump(rec, open(NEW, "w"), indent=1)
    print("OWNER", rec.get("owners"), "| token email", rec.get("token_email"))
    return sid


def sheet_test(period):
    import gun_audit_sheet
    sid = json.load(open(NEW))["id"]
    inp = json.load(open(os.path.join(OS_DIR, "fleet", "state", "gun_audit", "%s_format_input.json" % period)))
    print("SHEET-TEST against", sid, "period", period, "(render=True, nothing written)")
    for line in gun_audit_sheet.update(sid, period, inp, True):
        print("SHEET", line)


def main():
    man, typed, csvs = load()
    if "--sheet-test" in sys.argv:
        sheet_test(sys.argv[sys.argv.index("--sheet-test") + 1])
        return 0
    if "--verify" in sys.argv:
        return 0 if verify(json.load(open(NEW))["id"], man, typed, csvs)["ok"] else 1
    for line in plan(man, typed):
        print("PLAN", line)
    if "--live" not in sys.argv:
        print("render only — nothing created (use --live)")
        return 0
    sid = live(man, typed)
    if not sid:
        return 2
    return 0 if verify(sid, man, typed, csvs)["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
