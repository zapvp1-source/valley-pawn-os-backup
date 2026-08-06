#!/usr/bin/env python3
import csv, re, os, collections
P = os.path.join(os.path.expanduser("~"),
                 "Documents/Claude/Projects/Taxes 2026/_raw/dupont_transactions.csv")
rows = list(csv.DictReader(open(P)))
for r in rows:
    r["amount"] = float(r["amount"])

VENDORS = {
    "Valley Building Supply": r"valley b",
    "Lowe's": r"lowes|lowe's",
    "Prestige Plumbing": r"prestige plumb",
    "Red Rock Concrete": r"red rock",
    "Signature Hardware": r"signature h",
    "LL Flooring / Lumber Liq": r"ll floor|lumber liq",
    "Burns Builders": r"burns",
    "Weaver Irrigation": r"weaver",
    "Commonwealth Tile": r"commonwealth til",
    "Shreckhise": r"shreckhise|shreckise",
    "Enlit": r"enlit",
    "Fundamental Siteworks": r"fundamental",
    "Royal Swimming Pools": r"royal swim|royalswim",
    "Renu Therapy": r"renu",
    "R.E. Boggs": r"boggs",
    "Home Depot": r"home depot|homedepot",
    "Ferguson / Build.com": r"ferguson|build\.com",
    "— concrete (any)": r"concrete",
    "— electric (any)": r"electric",
    "— plumbing (any)": r"plumb",
    "— roofing (any)": r"roof",
    "— landscape (any)": r"landscap|nursery|shrub",
    "— tile / flooring (any)": r"\btile\b|floor",
    "— lumber / building (any)": r"lumber|building supply|hardware",
    "— pool / spa (any)": r"\bpool\b|\bspa\b",
    "— excavat / grading": r"excavat|grading|siteworks|septic|well drill",
    "— HVAC": r"hvac|heating|air cond|mechanical",
    "— paint": r"paint",
    "— window / door": r"window|\bdoor\b",
}

print("STATEMENT COVERAGE")
per = sorted({r["period"] for r in rows if r["period"]})
print("  periods:", len(per), "|", per[0] if per else "", "->", per[-1] if per else "")
yrs = collections.Counter(r["date"][-4:] for r in rows if len(r["date"]) == 10)
print("  txns by year:", dict(sorted(yrs.items())))
print()

grand = 0.0
for label, pat in VENDORS.items():
    rx = re.compile(pat, re.I)
    hits = [r for r in rows if rx.search(r["desc"]) and r["amount"] < 0]
    if not hits:
        print("%-28s  --" % label)
        continue
    tot = sum(-r["amount"] for r in hits)
    if not label.startswith("—"):
        grand += tot
    print("%-28s  %3d txns  $%12s" % (label, len(hits), format(round(tot, 2), ",.2f")))
    for r in sorted(hits, key=lambda x: x["amount"])[:4]:
        print("        %s  %10.2f  %s" % (r["date"], r["amount"], r["desc"][:62]))
print("\nNAMED-VENDOR TOTAL (excludes generic '—' rows): $%s" % format(round(grand, 2), ",.2f"))
