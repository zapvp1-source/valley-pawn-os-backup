#!/usr/bin/env python3
"""csv_rows.py — per-store row counts for a Bravo report, today and the prior good day.

WHY: 'daily-items-to-price missed' and 'jewelry missed' are both all-or-nothing suppressions caused
by ONE store coming back short (WAY 241/247, LEX wedged). The fix depends on which store and by how
much, so count rows rather than restate the symptom.
"""
import csv, glob, os, sys, datetime as dt
B = os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction/output")
rep = sys.argv[1]
print("# %s — per-store rows\n" % rep)
for back in range(0, 5):
    d = (dt.date.today() - dt.timedelta(days=back)).isoformat()
    files = sorted(glob.glob(os.path.join(B, "%s*_%s.csv" % (d, rep))))
    if not files:
        continue
    print("%s:" % d)
    for f in files:
        store = os.path.basename(f).replace(".csv", "").split("_")[-2]
        try:
            with open(f, errors="replace") as fh:
                n = max(0, sum(1 for _ in csv.reader(fh)) - 1)
            print("   %-4s %6d rows" % (store, n))
        except Exception as e:
            print("   %-4s unreadable: %s" % (store, e))
    print()
