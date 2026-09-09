#!/usr/bin/env python3
"""Estimate average rental period at 282 Bald Rock from booking subject lines.
The <=7-day test under Reg 1.469-1T(e)(3)(ii)(A) turns on this number."""
import sqlite3, os, re, datetime, collections

DB = os.path.expanduser("~/Documents/Claude/Projects/Unified Search/index.db")
con = sqlite3.connect(DB)

MON = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}

rows = con.execute(
    "SELECT ts,subject FROM mail WHERE mail MATCH ? ORDER BY ts",
    ('"Mountain Valley Luxury" OR "Vrbo #"',)).fetchall()
print("subject lines scanned:", len(rows))

# "Aug 2 – 9, 2025"  /  "Oct 10 - 24, 2025"  /  "Dec 23 – 27, 2025"
R1 = re.compile(r"([A-Z][a-z]{2})\s+(\d{1,2})\s*[–-]\s*(\d{1,2}),\s*(\d{4})")
# "Oct 10 - Nov 2, 2025"
R2 = re.compile(r"([A-Z][a-z]{2})\s+(\d{1,2})\s*[–-]\s*([A-Z][a-z]{2})\s+(\d{1,2}),\s*(\d{4})")

stays = {}   # dedupe identical (start,end)
for ts, subj in rows:
    s = subj or ""
    inquiry = s.lower().startswith("inquiry") or "special offer" in s.lower()
    m = R2.search(s)
    if m and m.group(1) in MON and m.group(3) in MON:
        y = int(m.group(5))
        a = datetime.date(y, MON[m.group(1)], int(m.group(2)))
        b = datetime.date(y, MON[m.group(3)], int(m.group(4)))
    else:
        m = R1.search(s)
        if not m or m.group(1) not in MON:
            continue
        y = int(m.group(4))
        a = datetime.date(y, MON[m.group(1)], int(m.group(2)))
        b = datetime.date(y, MON[m.group(1)], int(m.group(3)))
    n = (b - a).days
    if not (1 <= n <= 60):
        continue
    stays[(a, b)] = stays.get((a, b), False) or (not inquiry)

booked = {k: v for k, v in stays.items() if v}
print("\ndistinct date ranges seen:", len(stays), " | of which NOT inquiry-only:", len(booked))

def report(d, label):
    if not d:
        print("\n%s: none" % label); return
    nights = [(b - a).days for (a, b) in d]
    print("\n=== %s ===" % label)
    print("  stays: %d   total nights: %d   AVERAGE: %.2f nights" %
          (len(nights), sum(nights), sum(nights) / len(nights)))
    c = collections.Counter(nights)
    print("  distribution:", ", ".join("%dn x%d" % (k, c[k]) for k in sorted(c)))
    print("  <=7 nights: %d of %d (%.0f%%)" %
          (sum(1 for n in nights if n <= 7), len(nights),
           100 * sum(1 for n in nights if n <= 7) / len(nights)))

# 2025 stay year only (the placed-in-service year)
d2025 = {k: v for k, v in booked.items() if k[0].year == 2025}
report(d2025, "CONFIRMED-ish STAYS WITH 2025 START DATE")
report(booked, "ALL CONFIRMED-ish STAYS (any year)")

print("\nEarliest 2025 stay start:", min([a for a, b in d2025], default=None))
print("\nNOTE: derived from email subject lines, not the Airbnb/Vrbo transaction export.")
print("Use the platform CSV export for the filed position.")
