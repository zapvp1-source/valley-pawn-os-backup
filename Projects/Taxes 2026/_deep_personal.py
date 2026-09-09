#!/usr/bin/env python3
"""Deep hunt for TY2025 PERSONAL return documents. Real hits, correct 2025 windows."""
import sqlite3, os, datetime

DB = os.path.expanduser("~/Documents/Claude/Projects/Unified Search/index.db")
OUT = os.path.expanduser("~/Documents/Claude/Projects/Taxes 2026/_raw/personal_deep.md")
con = sqlite3.connect(DB)

def ep(y, m=1, d=1):
    return int(datetime.datetime(y, m, d).timestamp())

Y25, AUG25, Y26, MID26 = ep(2025), ep(2025, 8), ep(2026), ep(2026, 7)

# label, mailquery, filequery, since, until
C = [
 ("STR-1 Airbnb reservations/bookings Aug-Dec 2025 (AVG STAY)",
  'airbnb AND (reservation OR "booking confirmed" OR "is arriving" OR checkout)', 'airbnb', AUG25, Y26),
 ("STR-2 Airbnb payouts Aug-Dec 2025", 'airbnb AND payout', 'airbnb AND payout', AUG25, Y26),
 ("STR-3 VRBO/HomeAway bookings 2025", 'vrbo OR homeaway OR "instant booking"', 'vrbo', AUG25, Y26),
 ("STR-4 Airbnb/VRBO 2025 tax document or 1099", 'airbnb OR vrbo', 'airbnb OR vrbo', Y26, MID26),
 ("STR-5 Cleaning / turnover vendor (Green Nest etc.)",
  '"green nest" OR (cleaning AND (invoice OR service))', '"green nest" OR cleaning', Y25, Y26),
 ("STR-6 Property manager / co-host", '"co-host" OR cohost OR "property manage"', 'manage', Y25, Y26),
 ("STR-7 Bald Rock furnishings/supplies purchases", '"bald rock" AND (order OR delivered OR shipped)', None, Y25, Y26),
 ("STR-8 Guesty / PMS / channel manager", 'guesty OR hospitable OR ownerrez OR lodgify', None, Y25, Y26),
 # information returns arriving in 2026 for TY2025
 ("IR-1 W-2 2025", '"W-2" OR "wage and tax"', None, Y26, MID26),
 ("IR-2 1095-A 2025", '"1095-A"', None, Y26, MID26),
 ("IR-3 Fidelity HSA tax forms", 'fidelity AND ("tax form" OR 1099 OR 5498)', None, Y26, MID26),
 ("IR-4 Vanguard tax forms", 'vanguard AND ("tax form" OR 1099)', None, Y26, MID26),
 ("IR-5 1098 mortgage interest 2025", '"1098" OR "mortgage interest statement" OR servicemac', None, Y26, MID26),
 ("IR-6 Zillow/rent platform 1099-K", 'zillow OR avail OR "1099-K"', None, Y26, MID26),
 ("IR-7 K-1 2025", '"K-1"', None, Y26, MID26),
 # property records 2025
 ("PR-1 Property tax bills 2025", '"tax bill" OR "real estate tax" OR "property tax"', 'tax AND bill', Y25, MID26),
 ("PR-2 Insurance declarations 2025 (properties)",
  'insurance AND (declaration OR renewal OR policy) AND (steadily OR kin OR homesite OR dwelling)',
  'declaration OR "dec page"', Y25, MID26),
 ("PR-3 HOA — Palencia / others", 'palencia OR HOA OR "homeowners association"', 'HOA', Y25, MID26),
 ("PR-4 Woods Walk rent (Avail)", 'avail AND (rent OR payment OR tenant)', '"woods walk"', Y25, MID26),
 ("PR-5 Hardinberry rent / tenant", 'hardinberry', 'hardinberry', Y25, MID26),
 ("PR-6 817 Richmond / FirstCash rent", '"817 richmond" OR firstcash', '"817 richmond"', Y25, MID26),
 ("PR-7 844 Cypress closing statement / basis", '"cypress crossing" AND (closing OR settlement OR deed)',
  '"cypress crossing"', ep(2024, 9), MID26),
 # residency
 ("RES-1 FL homestead application", 'homestead AND (exemption OR apply OR filed OR sjcpa)', 'homestead', Y25, MID26),
 ("RES-2 FL driver license / DMV", 'FLHSMV OR ("driver license" AND florida) OR "surrender"', None, Y25, MID26),
 ("RES-3 FL voter registration", 'voter AND (registration OR registered)', None, Y25, MID26),
 ("RES-4 Moving / relocation evidence", '"change of address" OR moving OR relocat', None, Y25, MID26),
 # tax admin
 ("TA-1 2025 estimated tax payments", '"1040-ES" OR "760ES" OR ("estimated" AND (voucher OR payment))', None, Y25, MID26),
 ("TA-2 IRS notices 2025-2026", '"internal revenue" AND (notice OR balance OR CP)', None, Y25, MID26),
 ("TA-3 VA Taxation notices", '"department of taxation"', None, Y25, MID26),
 ("TA-4 Silverline / Lodestar 2025 work", 'silverline OR lodestar', None, Y25, MID26),
]

lines = ["# TY2025 PERSONAL — deep document hunt", ""]
found, missing = [], []
for label, mq, fq, since, until in C:
    lines.append("## " + label)
    hits = 0
    if mq:
        try:
            for r in con.execute(
                "SELECT date(ts,'unixepoch'),substr(sender,1,30),substr(subject,1,66) "
                "FROM mail WHERE mail MATCH ? AND ts>=? AND ts<? ORDER BY ts LIMIT 10",
                (mq, since, until)):
                lines.append("  MAIL %s | %s | %s" % r); hits += 1
        except Exception as e:
            lines.append("  mail err " + str(e)[:60])
    if fq:
        try:
            for r in con.execute(
                "SELECT date(mtime,'unixepoch'),substr(replace(path,"
                "'/Users/joshuadavis/Library/Mobile Documents/com~apple~CloudDocs/',''),1,86) "
                "FROM files WHERE files MATCH ? AND mtime>=? ORDER BY mtime DESC LIMIT 6",
                (fq, since)):
                if "/Library/Mail/" in r[1]:
                    continue
                lines.append("  FILE %s | %s" % r); hits += 1
        except Exception as e:
            lines.append("  file err " + str(e)[:60])
    if hits == 0:
        lines.append("  *** NOTHING FOUND ***")
        missing.append(label)
    else:
        found.append((label, hits))
    lines.append("")

lines.append("---\n## SUMMARY")
lines.append("FOUND (%d):" % len(found))
for l, h in found:
    lines.append("  - %s  [%d hits]" % (l, h))
lines.append("\nNOTHING FOUND (%d):" % len(missing))
for l in missing:
    lines.append("  - %s" % l)
open(OUT, "w").write("\n".join(lines))
print("\n".join(lines[-(len(found) + len(missing) + 6):]))
print("\nfull detail:", OUT)
