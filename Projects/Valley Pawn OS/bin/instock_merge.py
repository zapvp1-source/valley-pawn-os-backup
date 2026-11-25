#!/usr/bin/env python3
"""instock_merge.py <YYYY-MM-DD> -- built 2026-11-24 (Joshua: know every piece of inventory, one update a night).
Combines the five per-store on-shelf lists (Bravo cell instock-all) into ONE company list and publishes it to
Google Drive. All-or-nothing: every store must be present, each file must match Bravo's own row total, and no
store may swing more than 20% from the last published night. Otherwise nothing is published and the last good
list stays in place. Read-only on Bravo data; never posts to Slack."""
import csv, io, json, os, sys, shutil, datetime, re
HOME = os.path.expanduser("~")
BR = os.path.join(HOME, "Documents/Claude/Projects/Bravo Data Extraction")
OUT = os.path.join(BR, "output")
STATE = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS/fleet/state/instock")
DRIVE = os.path.join(HOME, "Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive/01 Business/"
                           "Full Circle Finance (Valley Pawn)/08 Reports & Analysis/Inventory - Item Level")
STORES = [("CUL", "Culpeper"), ("HAR", "Harrisonburg"), ("LEX", "Lexington"), ("ROA", "Roanoke"), ("WAY", "Waynesboro")]

def money(s):
    s = (s or "").replace("$", "").replace(",", "").strip()
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    try:
        v = float(s)
    except ValueError:
        return ""
    return -v if neg else v

def main():
    d = sys.argv[1]
    day = datetime.date.fromisoformat(d)
    os.makedirs(STATE, exist_ok=True)
    status = {"date": d, "published": False, "stores": {}, "problems": []}
    rows = []
    for code, name in STORES:
        p = os.path.join(OUT, f"{d}_{code}_instock-all.tsv")
        if not os.path.isfile(p):
            status["problems"].append(f"{code}: list missing"); continue
        meta = {}
        try:
            for ln in open(p + ".meta", encoding="utf-8-sig"):
                if "=" in ln:
                    k, v = ln.strip().split("=", 1); meta[k] = v
        except OSError:
            pass
        txt = open(p, encoding="utf-8-sig", newline="").read()
        rd = list(csv.reader(io.StringIO(txt), delimiter="\t"))
        rd = [r for r in rd if any(c.strip() for c in r)]
        if not rd:
            status["problems"].append(f"{code}: empty file"); continue
        hdr = [h.strip() for h in rd[0]]
        need = ["Number", "Status", "Category", "Description", "Cost", "Price", "Date"]
        if any(h not in hdr for h in need):
            status["problems"].append(f"{code}: unexpected columns {hdr}"); continue
        ix = {h: hdr.index(h) for h in need}
        body = rd[1:]
        exp = int(meta.get("expected", "-1") or -1)
        if exp != len(body):
            status["problems"].append(f"{code}: {len(body)} rows but Bravo reported {exp}"); continue
        for r in body:
            r = r + [""] * (len(hdr) - len(r))
            dt = r[ix["Date"]].strip(); age = ""; iso = dt
            m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", dt)
            if m:
                dd = datetime.date(int(m[3]), int(m[1]), int(m[2])); iso = dd.isoformat(); age = (day - dd).days
            rows.append([name, code, r[ix["Number"]].strip(), r[ix["Category"]].strip(), r[ix["Description"]].strip(),
                         money(r[ix["Cost"]]), money(r[ix["Price"]]), iso, age, r[ix["Status"]].strip()])
        status["stores"][code] = len(body)
    prev = {}
    try:
        prev = json.load(open(os.path.join(STATE, "last_published.json"))).get("stores", {})
    except (OSError, ValueError):
        pass
    for code, n in status["stores"].items():
        if prev.get(code) and abs(n - prev[code]) > 0.20 * prev[code]:
            status["problems"].append(f"{code}: {n} items vs {prev[code]} last published (over 20% change)")
    if len(status["stores"]) == len(STORES) and not status["problems"]:
        head = ["Store", "Store Code", "Item Number", "Category", "Description", "Cost", "Price", "In Inventory Since", "Days On Shelf", "Status"]
        local = os.path.join(OUT, f"{d}_ALL_instock.csv")
        with open(local, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f); w.writerow(head); w.writerows(rows)
        os.makedirs(os.path.join(DRIVE, "History"), exist_ok=True)
        shutil.copyfile(local, os.path.join(DRIVE, "History", f"Valley Pawn In-Stock Inventory {d}.csv"))
        tmp = os.path.join(DRIVE, ".latest.tmp")
        shutil.copyfile(local, tmp)
        os.replace(tmp, os.path.join(DRIVE, "Valley Pawn In-Stock Inventory (latest).csv"))
        with open(os.path.join(DRIVE, "As Of.txt"), "w") as f:
            f.write(f"In-stock list as of close of business {d}. {len(rows)} items. "
                    + ", ".join(f"{c} {n}" for c, n in status["stores"].items()) + "\n")
        status["published"] = True; status["total"] = len(rows)
        json.dump(status, open(os.path.join(STATE, "last_published.json"), "w"), indent=1)
    json.dump(status, open(os.path.join(STATE, f"status_{d}.json"), "w"), indent=1)
    json.dump(status, open(os.path.join(STATE, "status_latest.json"), "w"), indent=1)
    print(json.dumps(status))
    return 0 if status["published"] else 1

if __name__ == "__main__":
    sys.exit(main())
