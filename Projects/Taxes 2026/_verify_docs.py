#!/usr/bin/env python3
"""Precise verification of the TY2025 documents that actually decide the returns.
Prints real hits, not counts. Read-only."""
import sqlite3, os, datetime

DB = os.path.expanduser("~/Documents/Claude/Projects/Unified Search/index.db")
con = sqlite3.connect(DB)
E = lambda y, m=1, d=1: int(datetime.datetime(y, m, d).timestamp())

# label, mail-FTS, file-FTS, since
CHECKS = [
 ("2025 W-2 (Gusto, both entities)",
  '"W-2" AND (2025 OR gusto)', 'W2 OR "W-2"', E(2025, 12)),
 ("2025 Form 1095-A marketplace",
  '"1095-A"', '"1095"', E(2025)),
 ("2025 Form 1099-SA / 5498-SA (HSA)",
  '"1099-SA" OR "5498-SA"', '"1099-SA" OR "5498"', E(2025)),
 ("2025 Form 1098 mortgage interest",
  '"Form 1098" OR "1098 mortgage" OR "mortgage interest statement"', '"1098"', E(2025)),
 ("2025 Form 1099 consolidated (Vanguard)",
  'vanguard AND (1099 OR "tax form" OR "tax document")', 'vanguard AND 1099', E(2025)),
 ("2025 Airbnb earnings summary / 1099-K",
  'airbnb AND (1099 OR earnings OR payout OR "tax document")', 'airbnb', E(2025)),
 ("2025 VRBO earnings / 1099-K",
  'vrbo AND (1099 OR earnings OR payout OR tax)', 'vrbo', E(2025)),
 ("2025 Zillow 1099-K (Hardinberry rent)",
  'zillow AND (1099 OR "tax form" OR earnings)', 'zillow AND 1099', E(2025)),
 ("FL homestead exemption — 844 Cypress / St Johns",
  'homestead AND (exemption OR "st johns" OR florida)', 'homestead', E(2024, 6)),
 ("FL driver license issued",
  '"florida" AND ("driver license" OR "driver\'s license" OR FLHSMV)', 'FLHSMV OR "florida driver"', E(2025)),
 ("Bald Rock retrospective FMV appraisal",
  'appraisal AND ("bald rock" OR verona OR retrospective)', 'appraisal AND "bald rock"', E(2024, 6)),
 ("Cost segregation study / engagement",
  '"cost segregation" OR "cost seg smart"', '"cost seg"', E(2024, 6)),
 ("2025 estimated tax payments made",
  '("1040-ES" OR "760ES" OR "estimated tax") AND (confirmation OR payment OR receipt)',
  '"1040-ES" OR "760ES"', E(2025)),
 ("IRS installment agreement / balance",
  '("installment agreement" OR "payment plan") AND IRS', '"installment"', E(2025)),
 ("Silverline engagement / 2025 organizer",
  'silverline AND (organizer OR engagement OR "tax return" OR documents)', 'silverline', E(2025)),
 ("The J Davis Group Inc — still active?",
  '"J Davis Group"', '"J Davis Group"', E(2025)),
 ("VA PTET election 2025",
  'PTET OR "pass-through entity tax"', 'PTET', E(2025)),
 ("2025 Bravo year-end inventory valuation",
  'bravo AND inventory AND (valuation OR "year end" OR december)', '"inventory" AND bravo', E(2025, 11)),
]

for label, mq, fq, since in CHECKS:
    print("=" * 78)
    print(label, " | since", datetime.datetime.fromtimestamp(since).strftime("%Y-%m-%d"))
    got = False
    try:
        rows = con.execute(
            "SELECT date(ts,'unixepoch'),substr(sender,1,34),substr(subject,1,62) "
            "FROM mail WHERE mail MATCH ? AND ts>=? ORDER BY ts DESC LIMIT 6",
            (mq, since)).fetchall()
        for r in rows:
            print("   MAIL %s | %s | %s" % r); got = True
    except Exception as e:
        print("   mail query error:", str(e)[:70])
    try:
        rows = con.execute(
            "SELECT date(mtime,'unixepoch'),substr(replace(path,"
            "'/Users/joshuadavis/Library/Mobile Documents/com~apple~CloudDocs/',''),1,88) "
            "FROM files WHERE files MATCH ? AND mtime>=? ORDER BY mtime DESC LIMIT 6",
            (fq, since)).fetchall()
        for r in rows:
            print("   FILE %s | %s" % r); got = True
    except Exception as e:
        print("   file query error:", str(e)[:70])
    if not got:
        print("   *** NOTHING FOUND ***")
    print()
