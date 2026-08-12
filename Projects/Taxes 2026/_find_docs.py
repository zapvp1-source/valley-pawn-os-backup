#!/usr/bin/env python3
"""TY2025 tax-document hunt against the unified index (mail incl. attachments,
iCloud files, texts). Writes a findings table. Read-only."""
import sqlite3, os, datetime, re

DB = os.path.expanduser("~/Documents/Claude/Projects/Unified Search/index.db")
OUT = os.path.expanduser("~/Documents/Claude/Projects/Taxes 2026/_raw/doc_hunt.md")
con = sqlite3.connect(DB)

E2025 = int(datetime.datetime(2025, 1, 1).timestamp())
E2024 = int(datetime.datetime(2024, 1, 1).timestamp())

# (category, label, fts_query, earliest_epoch)
ITEMS = [
 # ---------- BUSINESS: payroll ----------
 ("BIZ payroll", "W-2 / W-3 2025 (Gusto)", '"W-2" OR "W-3" OR "wage and tax statement"', E2025),
 ("BIZ payroll", "Form 941 quarterly", '"941"', E2025),
 ("BIZ payroll", "Form 940 FUTA", '"940" AND (futa OR unemployment)', E2025),
 ("BIZ payroll", "VA VEC FC-20/FC-21", '"FC-20" OR "FC-21" OR VEC', E2025),
 ("BIZ payroll", "VA-5 / VA-6 withholding", '"VA-6" OR "VA-5"', E2025),
 ("BIZ payroll", "Gusto payroll register / year-end", 'gusto AND (register OR "year end" OR annual)', E2025),
 ("BIZ payroll", "Retirement plan / 401k employer contrib", '"401(k)" OR 401k OR "safe harbor" OR "profit sharing"', E2025),
 # ---------- BUSINESS: Bravo / inventory ----------
 ("BIZ inventory", "Bravo year-end inventory valuation", 'bravo AND (inventory OR valuation)', E2025),
 ("BIZ inventory", "Pawn loans receivable at year end", '"loans receivable" OR "pawn loan"', E2025),
 ("BIZ inventory", "Layaway liability report", 'layaway', E2025),
 # ---------- BUSINESS: books ----------
 ("BIZ books", "Trial balance / P&L / Balance sheet 2025", '"trial balance" OR "profit and loss" OR "balance sheet"', E2025),
 ("BIZ books", "Fixed asset additions 2025", '"fixed asset" OR "depreciation schedule"', E2025),
 # ---------- BUSINESS: banking ----------
 ("BIZ banking", "Bank statements 2025", 'statement AND (checking OR savings OR "account statement")', E2025),
 ("BIZ banking", "Merchant processor annual statement", 'merchant AND (statement OR processing)', E2025),
 ("BIZ banking", "1099-K from processors/marketplaces", '"1099-K"', E2025),
 ("BIZ banking", "1099-INT", '"1099-INT" OR "1099 INT"', E2025),
 # ---------- BUSINESS: leases / insurance / licenses ----------
 ("BIZ ops", "Store leases / renewals", 'lease AND (store OR premises OR landlord OR renewal)', E2024),
 ("BIZ ops", "Insurance declarations (GL/property/crime)", '"declarations" OR "dec page" OR "jewelers block"', E2025),
 ("BIZ ops", "Workers comp policy", '"workers comp" OR "workers\' compensation"', E2025),
 ("BIZ ops", "VA sales tax ST-9", '"ST-9" OR "sales and use tax"', E2025),
 ("BIZ ops", "BPOL / business license", 'BPOL OR "business license"', E2025),
 ("BIZ ops", "Pawnbroker license", 'pawnbroker AND licens', E2025),
 ("BIZ ops", "FFL / ATF renewal", 'FFL OR ATF OR "federal firearms"', E2025),
 ("BIZ ops", "VA SCC annual report", '"SCC" AND (annual OR registration)', E2025),
 ("BIZ ops", "Business personal property tax", '"personal property tax"', E2025),
 ("BIZ ops", "1099-NEC issued / 1096", '"1099-NEC" OR "1096"', E2025),
 ("BIZ ops", "Scrap gold refiner settlements", 'refiner OR "scrap gold" OR smelt', E2025),
 # ---------- PERSONAL: information returns ----------
 ("PERS info-return", "Schedule K-1 2025", '"K-1" OR "Schedule K-1"', E2025),
 ("PERS info-return", "Form 1095-A (marketplace)", '"1095-A" OR "1095 A" OR marketplace', E2025),
 ("PERS info-return", "Form 1099-SA (HSA distributions)", '"1099-SA"', E2025),
 ("PERS info-return", "Form 5498-SA (HSA contributions)", '"5498"', E2025),
 ("PERS info-return", "Form 1098 mortgage interest", '"1098" AND (mortgage OR interest)', E2025),
 ("PERS info-return", "Form 1099-B / brokerage (Vanguard)", '"1099-B" OR "1099-DIV" OR vanguard', E2025),
 ("PERS info-return", "Form 1099-K Zillow (Hardinberry rent)", 'zillow', E2025),
 ("PERS info-return", "Form 1099-G state refund", '"1099-G"', E2025),
 ("PERS info-return", "Form 1099-S property sale", '"1099-S"', E2025),
 # ---------- PERSONAL: Schedule E properties ----------
 ("PERS property", "282 Bald Rock — Airbnb/VRBO earnings + 1099-K", 'airbnb OR vrbo', E2025),
 ("PERS property", "282 Bald Rock — occupancy / booking calendar", '"bald rock" AND (booking OR reservation OR guest)', E2025),
 ("PERS property", "844 Cypress Crossing — records", '"cypress crossing"', E2025),
 ("PERS property", "14300 Woods Walk Lane — records", '"woods walk"', E2025),
 ("PERS property", "148 Hardinberry St — records", 'hardinberry', E2025),
 ("PERS property", "817 Richmond Rd / Farming Infinity", '"817 richmond" OR "farming infinity"', E2025),
 ("PERS property", "Property tax bills", '"real estate tax" OR "property tax bill" OR "tax bill"', E2025),
 ("PERS property", "Landlord/homeowner insurance", 'insurance AND (dwelling OR homeowner OR landlord OR "policy")', E2025),
 ("PERS property", "HOA statements", 'HOA OR "homeowners association"', E2025),
 # ---------- PERSONAL: residency / conversion ----------
 ("PERS residency", "FL homestead exemption (St Johns County)", 'homestead', E2024),
 ("PERS residency", "FL driver's license / vehicle registration", '"driver\'s license" OR "drivers license" OR registration', E2025),
 ("PERS residency", "FL voter registration", 'voter', E2024),
 ("PERS residency", "Utility start/stop (move evidence)", 'utility AND (transfer OR "start service" OR "stop service" OR final)', E2025),
 # ---------- PERSONAL: tax admin ----------
 ("PERS admin", "Estimated tax payment confirmations 2025", '"estimated tax" OR "1040-ES" OR "760ES"', E2025),
 ("PERS admin", "IRS notices / installment agreement", 'IRS AND (notice OR "installment agreement" OR CP)', E2025),
 ("PERS admin", "VA Dept Taxation notices", '"department of taxation" OR "virginia tax"', E2025),
 ("PERS admin", "Silverline / Lodestar correspondence", 'silverline OR lodestar', E2025),
 ("PERS admin", "Charitable contribution acknowledgments", 'donation OR charitable OR "thank you for your gift"', E2025),
 # ---------- Both ----------
 ("BOTH", "Vehicle purchase/sale docs", '"bill of sale" OR taycan OR fisker OR rivian', E2024),
 ("BOTH", "Cost segregation study", '"cost seg" OR "cost segregation"', E2024),
 ("BOTH", "Appraisal (Bald Rock FMV)", 'appraisal AND ("bald rock" OR verona)', E2024),
]

def q(table, expr, since=None, limit=6):
    sql = "SELECT %s FROM %s WHERE %s MATCH ?" % (
        "date(ts,'unixepoch')||' | '||substr(sender,1,32)||' | '||substr(subject,1,58)"
        if table == "mail" else
        "date(mtime,'unixepoch')||' | '||substr(replace(path,'/Users/joshuadavis/Library/Mobile Documents/com~apple~CloudDocs/',''),1,95)",
        table, table)
    args = [expr]
    if since and table == "mail":
        sql += " AND ts>=?"; args.append(since)
    elif since and table == "files":
        sql += " AND mtime>=?"; args.append(since)
    sql += " ORDER BY %s DESC LIMIT ?" % ("ts" if table == "mail" else "mtime")
    args.append(limit)
    try:
        return con.execute(sql, args).fetchall()
    except Exception as e:
        return [("ERR " + str(e)[:60],)]

def count(table, expr, since=None):
    sql = "SELECT count(*) FROM %s WHERE %s MATCH ?" % (table, table)
    args = [expr]
    if since:
        sql += " AND %s>=?" % ("ts" if table == "mail" else "mtime"); args.append(since)
    try:
        return con.execute(sql, args).fetchone()[0]
    except Exception:
        return -1

lines = ["# TY2025 Document Hunt — raw search results",
         "", "Generated by `_find_docs.py` against the unified index (Apple Mail incl. attachments, iCloud Drive, texts).",
         "`m=` mail hits, `f=` iCloud file hits, both since the stated cutoff.", ""]
summary = []
for cat, label, expr, since in ITEMS:
    mc = count("mail", expr, since)
    fc = count("files", expr, since)
    status = "FOUND" if (mc + fc) > 0 else "NOT FOUND"
    summary.append((cat, label, mc, fc, status))
    lines.append("## [%s] %s" % (cat, label))
    lines.append("query: `%s`  since %s — **m=%d  f=%d**" %
                 (expr, datetime.datetime.fromtimestamp(since).strftime("%Y-%m-%d"), mc, fc))
    for r in q("mail", expr, since):
        lines.append("  - MAIL  %s" % r[0])
    for r in q("files", expr, since):
        lines.append("  - FILE  %s" % r[0])
    lines.append("")

open(OUT, "w").write("\n".join(lines))
print("wrote", OUT)
print()
print("%-16s %-52s %6s %6s  %s" % ("CATEGORY", "ITEM", "MAIL", "FILES", "STATUS"))
for cat, label, mc, fc, st in summary:
    print("%-16s %-52s %6d %6d  %s" % (cat, label[:52], mc, fc, st))
nf = [s for s in summary if s[4] == "NOT FOUND"]
print("\nTOTAL ITEMS: %d   FOUND: %d   NOT FOUND: %d" % (len(summary), len(summary) - len(nf), len(nf)))
