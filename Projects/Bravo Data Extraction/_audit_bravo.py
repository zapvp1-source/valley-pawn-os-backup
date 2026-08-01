import json, os, glob, datetime, collections

RES = "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results"
CUTOFF = datetime.datetime(2026, 7, 19)

runs = []
for p in glob.glob(os.path.join(RES, "*.json")):
    mt = datetime.datetime.fromtimestamp(os.path.getmtime(p))
    if mt < CUTOFF:
        continue
    try:
        d = json.load(open(p, encoding="utf-8-sig"))
    except Exception as e:
        runs.append({"file": os.path.basename(p), "when": mt, "id": os.path.basename(p),
                     "status": "UNREADABLE", "cells": []})
        continue
    runs.append({
        "file": os.path.basename(p),
        "when": mt,
        "id": d.get("trigger_id", "?"),
        "status": (d.get("status") or "?").lower(),
        "cells": d.get("cells") or [],
        "errors": d.get("errors") or [],
    })

runs.sort(key=lambda r: r["when"])

print("=" * 78)
print("BRAVO PIPELINE AUDIT  —  runs since Sun 2026-07-19  (through %s)" % datetime.datetime.now().strftime("%a %Y-%m-%d %H:%M"))
print("=" * 78)
print("TOTAL RUNS: %d" % len(runs))
print()

# ---- run-level tally
rt = collections.Counter(r["status"] for r in runs)
print("RUN-LEVEL OUTCOMES")
for k, v in rt.most_common():
    print("   %-12s %3d   (%4.1f%%)" % (k, v, 100.0 * v / max(1, len(runs))))
print()

# ---- cell-level tally
cells = [(r, c) for r in runs for c in r["cells"]]
ct = collections.Counter((c.get("status") or "?").lower() for _, c in cells)
tot_cells = len(cells)
print("CELL-LEVEL OUTCOMES  (a 'cell' = one report for one store)")
print("   TOTAL CELLS: %d" % tot_cells)
for k, v in ct.most_common():
    print("   %-12s %3d   (%4.1f%%)" % (k, v, 100.0 * v / max(1, tot_cells)))
ok = ct.get("success", 0)
print("   >>> CELL SUCCESS RATE: %.1f%%" % (100.0 * ok / max(1, tot_cells)))
print()

# ---- per report cell
print("BY REPORT CELL  (success / total)")
by = collections.defaultdict(lambda: [0, 0])
for _, c in cells:
    n = c.get("report", "?")
    by[n][1] += 1
    if (c.get("status") or "").lower() == "success":
        by[n][0] += 1
for n in sorted(by, key=lambda x: (by[x][0] / max(1, by[x][1]))):
    s, t = by[n]
    print("   %-28s %3d/%-3d  %5.1f%%" % (n, s, t, 100.0 * s / max(1, t)))
print()

# ---- per store
print("BY STORE  (success / total)")
bs = collections.defaultdict(lambda: [0, 0])
for _, c in cells:
    st = c.get("store", "?")
    bs[st][1] += 1
    if (c.get("status") or "").lower() == "success":
        bs[st][0] += 1
for st in sorted(bs):
    s, t = bs[st]
    print("   %-6s %3d/%-3d  %5.1f%%" % (st, s, t, 100.0 * s / max(1, t)))
print()

# ---- failure reasons
print("FAILURE REASONS  (top)")
er = collections.Counter()
for _, c in cells:
    if (c.get("status") or "").lower() != "success":
        e = (c.get("error") or "").strip()
        if not e:
            e = "(no error text — status=%s)" % c.get("status")
        e = e.split(" — ")[0].split(" - ")[0]
        for pat in ["EnsureStore failed", "BackToDashboard", "grid did not render",
                    "Grid never rendered", "not found", "timeout", "did not close"]:
            if pat.lower() in e.lower():
                e = pat
                break
        er[e[:70]] += 1
for k, v in er.most_common(10):
    print("   %3d  %s" % (v, k))
print()

# ---- chronological
print("EVERY RUN, OLDEST FIRST")
print("   %-11s %-42s %-9s %s" % ("WHEN", "TRIGGER", "OVERALL", "CELLS ok/total"))
for r in runs:
    c = r["cells"]
    o = sum(1 for x in c if (x.get("status") or "").lower() == "success")
    flag = "" if (r["status"] == "success" and o == len(c)) else "   <<<"
    print("   %-11s %-42s %-9s %d/%d%s" % (
        r["when"].strftime("%m-%d %H:%M"), r["id"][:42], r["status"], o, len(c), flag))
