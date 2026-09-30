#!/usr/bin/env python3
"""build_text_lists.py <YYYY-MM> — per-store Chekkit upload lists for the monthly text.

Source: Bravo "Chekkit Invites" range exports (Bravo Data Extraction/output/*_<ST>_chekkit-invites-range.csv),
(phones by store and first-visit month). Rules:
  - Text opt-in / opt-out is managed IN CHEKKIT (Joshua 2026-09-29: "the text opt in and out is through
    chekkit, do not filter in bravo"). Bravo's dnt column is deliberately IGNORED; Chekkit suppresses
    anyone who replied STOP.
  - Customers first seen within the last 18 months (handbook §07.06 relationship window).
  - Staff phones excluded (Valley Pawn OS/hr/ROSTER.json).
  - Valid 10-digit US numbers only; one row per phone; a phone is assigned to the store it was most
    recently seen at so nobody gets the same text from two stores.
Output: packs/<m>/chekkit_<Store>.csv  (First Name,Last Name,Phone,Email — Joshua appended as confirmation row)  + packs/<m>/text_lists.json summary.
"""
import csv, datetime as dt, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
OUTDIR_SRC = os.path.join(PROJ, "Bravo Data Extraction", "output")
ROSTER = os.path.join(PROJ, "Valley Pawn OS", "hr", "ROSTER.json")
STORES = {"CUL": "Culpeper", "WAY": "Waynesboro", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke"}
WINDOW_MONTHS = 18


def norm(p):
    d = re.sub(r"\D", "", p or "")
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    return d if len(d) == 10 and d[0] not in "01" else None


def main():
    m = sys.argv[1]
    y, mo = map(int, m.split("-"))
    cut_y, cut_m = y, mo - WINDOW_MONTHS
    while cut_m <= 0:
        cut_m += 12; cut_y -= 1
    cutoff = f"{cut_y:04d}-{cut_m:02d}-01"

    staff = set()
    try:
        r = json.load(open(ROSTER))
        for e in r.get("employees", []):
            p = norm(str(e.get("phone") or ""))
            if p: staff.add(p)
    except Exception:
        pass

    dnt, best = set(), {}
    files = sorted(glob.glob(os.path.join(OUTDIR_SRC, "*_chekkit-invites-range.csv")))
    for f in files:
        base = os.path.basename(f)
        mm = re.match(r"(\d{4}-\d{2}-\d{2})_([A-Z]{3})_chekkit-invites-range\.csv$", base)
        if not mm or mm.group(2) not in STORES:
            continue
        fdate, st = mm.group(1), mm.group(2)
        with open(f, newline="", encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                p = norm(row.get("phone"))
                if not p:
                    continue
                if fdate < cutoff:
                    continue
                if p not in best or fdate > best[p]["date"]:
                    best[p] = {"date": fdate, "store": st,
                               "first_name": (row.get("first_name") or "").strip().title(),
                               "last_name": (row.get("last_name") or "").strip().title()}
    out = os.path.join(HERE, "packs", m)
    os.makedirs(out, exist_ok=True)
    summary = {"month": m, "cutoff_first_seen": cutoff, "consent_source": "Chekkit (opt-in/opt-out managed there)", "staff_excluded": 0,
               "source_files": len(files), "stores": {}}
    for st, name in STORES.items():
        rows = []
        for p, v in best.items():
            if v["store"] != st:
                continue
            if p in staff:
                summary["staff_excluded"] += 1; continue
            rows.append({"First Name": (v["first_name"] + " " + v["last_name"]).strip(), "Last Name": "",
                         "Phone": p, "Email": ""})
        rows.sort(key=lambda r: r["Phone"])
        # Proven Chekkit upload format (chekkit-weekly-review-requests runbook, 2026-07-22): Joshua is the
        # last row of every store's file so he receives each campaign as its confirmation copy.
        rows.append({"First Name": "JOSHUA DAVIS", "Last Name": "", "Phone": "8049304221", "Email": "jdavis@fcfpawn.com"})
        path = os.path.join(out, f"chekkit_{name}.csv")
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["First Name", "Last Name", "Phone", "Email"])
            w.writeheader(); w.writerows(rows)
        summary["stores"][name] = len(rows) - 1
    json.dump(summary, open(os.path.join(out, "text_lists.json"), "w"), indent=1)
    print(json.dumps(summary))
    if min(summary["stores"].values()) == 0:
        sys.exit("FAIL: a store list came out empty — Bravo export missing; do not send partial")


if __name__ == "__main__":
    main()
