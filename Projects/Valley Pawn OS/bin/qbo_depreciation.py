#!/usr/bin/env python3
"""qbo_depreciation.py [--render] [--through YYYY-MM] — monthly 2026 book depreciation + amortization from the fixed-asset
register (books-tax-strategy Gate 4 permitted class 2). Built 2026-10-21. Called after every bravo-daily-gl run.

SOURCE: Quickbooks Set UP/FY2025-Return-Conformance/FIXED-ASSET-REGISTER.xlsx, sheet "Register 12-31-2025", column
"2026 projected (return NEXT YEAR report)" — the filed 2025 return's own next-year depreciation report.
EXCLUDED (not owned / not company assets in 2026 — books follow the facts; listed for the preparer via Joshua):
  16 2024 Rivian R1S — lender documents a LEASE; settled decision "Rivian = lease expense" (lease payments already
     expensed in Automotive Lease), so depreciating it too would double-count
  17 2020 Porsche Taycan — sold 2024-06-04 (Crown CDJR via DCCU payoff, OPEN_ITEMS 2026-09-04)
  18 2023 Fisker Ocean — bought back by the lender 2025-04-28
Leasehold Improvements (FL store build-out) are not in service until the store opens; the Sch L "unitemized" 35,723.17
has no asset detail — neither is depreciated until itemized/placed in service.
One JE per month, dated the last day, DocNumber DEP-2026-MM:
  Dr Depreciation expenses / Cr Accumulated Depreciation ; Dr Amortization expenses / Cr Amortized Goodwill
Annual /12 rounded to the cent; December carries the rounding so the year equals the register exactly.
Guard: QBO query by DocNumber before posting. No Slack."""
import calendar, datetime as dt, os, sys
QBO_DIR = os.path.expanduser("~/Documents/Claude/Projects/Quickbooks Set UP")
sys.path.insert(0, QBO_DIR)
REG = os.path.join(QBO_DIR, "FY2025-Return-Conformance", "FIXED-ASSET-REGISTER.xlsx")
YEAR, EXCLUDE, AMORT = 2026, {16, 17, 18}, {4, 11}
RENDER = "--render" in sys.argv


def schedule():
    import openpyxl
    ws = openpyxl.load_workbook(REG, data_only=True)["Register 12-31-2025"]
    dep = amort = 0.0; used = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not isinstance(r[0], int) or r[0] in EXCLUDE:
            continue
        v = float(r[11] or 0)
        if v:
            used.append("%d %s %.0f" % (r[0], r[1], v))
            if r[0] in AMORT: amort += v
            else: dep += v
    return round(dep, 2), round(amort, 2), used


def month_amt(annual, m):
    base = round(annual / 12, 2)
    return round(annual - base * 11, 2) if m == 12 else base


def main():
    dep, amort, used = schedule()
    print("2026 annual: depreciation %.2f, amortization %.2f from assets: %s" % (dep, amort, "; ".join(used)))
    today = dt.date.today()
    last = (today.replace(day=1) - dt.timedelta(days=1))
    if "--through" in sys.argv:
        y, mm = map(int, sys.argv[sys.argv.index("--through") + 1].split("-")); last = dt.date(y, mm, calendar.monthrange(y, mm)[1])
    import qbo_api as q
    for m in range(1, 13):
        d = dt.date(YEAR, m, calendar.monthrange(YEAR, m)[1])
        if d > last:
            break
        doc = "DEP-%d-%02d" % (YEAR, m)
        if [j for j in q.query("SELECT * FROM JournalEntry WHERE TxnDate = '%s'" % d) if (j.get("DocNumber") or "") == doc]:
            print(doc, "already posted"); continue
        a, b = month_amt(dep, m), month_amt(amort, m)
        spec = {"date": d.isoformat(), "docnum": doc, "allow_long": True,
                "memo": ("2026 book depreciation %s, 1/12 of the fixed-asset register's 2026 column (Quickbooks Set UP/FY2025-Return-"
                         "Conformance/FIXED-ASSET-REGISTER.xlsx, Register 12-31-2025, rows for assets %s). Excludes Rivian (lease, "
                         "expensed as lease), Porsche (sold 6/4/2024), Fisker (bought back 4/28/2025). Gate 4 class 2.")
                        % (d.strftime("%B %Y"), ", ".join(u.split()[0] for u in used)),
                "lines": [{"account": "Depreciation expenses", "debit": a, "desc": "Depreciation %s" % d.strftime("%b %Y")},
                          {"account": "Accumulated Depreciation", "credit": a, "desc": "Depreciation %s" % d.strftime("%b %Y")},
                          {"account": "Amortization expenses", "debit": b, "desc": "Goodwill amortization %s" % d.strftime("%b %Y")},
                          {"account": "Amortized Goodwill", "credit": b, "desc": "Goodwill amortization %s" % d.strftime("%b %Y")}]}
        if RENDER:
            print("RENDER", doc, d, "dep", a, "amort", b); continue
        je = q.je_create(spec); print("posted", doc, je["Id"], "dep", a, "amort", b)


if __name__ == "__main__":
    main()
