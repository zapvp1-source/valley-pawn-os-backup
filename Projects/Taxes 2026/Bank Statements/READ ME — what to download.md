# Drop bank statements in this folder

Anything you save here gets picked up automatically. Filenames don't matter. Just drop the PDFs in and tell me — I re-run the parser and it re-totals everything.

---

## What to pull, in priority order

### 1. DuPont Community Credit Union — statements, Feb 2022 → Dec 2025 ⭐ highest value
We already have Jan 2020 → Jan 2022. **Everything after January 2022 is missing**, and that's exactly the window when Red Rock, Royal Swimming Pools, Fundamental Siteworks, Commonwealth Tile, Weaver Irrigation, Renu Therapy and R.E. Boggs were paid — roughly $110,000 of invoices we can't currently prove were settled.

Accounts to grab (all of them):
- Full Circle Finance Inc — **Business Checking ID 0090**
- Full Circle Finance Inc — **Business Main Share Savings ID 0000**
- Any **personal** DuPont accounts — $32,117.25 of Valley Building Supply payments came from somewhere that isn't the business account
- **Dupont Line of Credit** — QuickBooks shows $4,535.08 against a bank balance of −$46,230.92, a ~$50,766 gap nobody has explained

Usually: log in → Statements or eStatements → select account → select month → download PDF. Monthly, so ~47 files per account.

### 2. DuPont check images ⭐⭐ the single biggest unlock
There are **514 cleared checks totaling $535,113.23** in 2020–2021 alone, and the statements show *only the check number* — no payee. That's where the labor money is. Most will be Valley Pawn operating checks; I can't separate the renovation ones without seeing who they were written to.

Look for: a "Check Images" or "View Check" link next to each cleared check in transaction history, or a bulk image export under Statements. If DuPont offers a **check register / transaction export with payee (CSV or QFX)**, that's even better than images — grab that instead.

If there's no bulk option, the branch can usually produce a check register for a date range on request. Waynesboro, (540) 946-3200.

### 3. Card statements — converts ~$110,673 of invoices into proven payments
These cards already paid Bald Rock vendors, per receipts we've matched:
- **MasterCard ending 0305** — paid Commonwealth Tile
- **MasterCard ending 6246** — paid Fundamental Siteworks
- **MasterCard ending 1689** — paid S.A.F.E. pressure wash
- **Lowe's Consumer Credit ending 1037** — paid the $8,757.88 appliance order
- **American Express ending 7115** — paid Signature Hardware
- Any Affirm account — a Signature Hardware refund went back to Affirm

Range: 2020 → 2025.

### 4. Wells Fargo — 2020 → 2025
QuickBooks carries WF Checking 2797, 3563, and 6507. WF 2797 alone shows a −$1,449,999.79 book balance that's never been reconciled.

---

## Why filenames don't matter

The parser reads the account number and statement period out of the PDF itself. Drop them in flat, in subfolders, however they download — it sorts itself out.

## What happens next

I re-run `_scan_statements.py`, which rebuilds `_raw/dupont_transactions.csv`, then `_match_vendors.py` re-totals every renovation vendor against the new data. Both live in the `Taxes 2026` folder and are already pointed at this directory.
