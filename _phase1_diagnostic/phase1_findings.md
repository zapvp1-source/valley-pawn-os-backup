# Valley Pawn — Phase 1 Diagnostic Findings

**Run date:** 2026-05-19 19:24
**Buy/forfeit window:** 2026-03-05 → 2026-04-03
**Inventory window:** 2025-05-17 → 2026-05-17

---

## ⚠ The headline finding: existing data cannot support a loan-portfolio analysis

The Bravo Data Extraction pipeline drops a feed called `buys-from-public` going back to May 2024.
After inspecting the ticket prefixes across all 5 stores, every row is either:

- **BT-** = Buy Ticket (outright purchase from a customer), or
- **FB-** = Forfeit Buy (an item pulled into inventory from a defaulted loan).

There are **zero LT-** (loan ticket) records in any monthly extract. The column literally named
"Loan Amount" is in fact the dollars paid for the buy, not a loan principal.

**Implication:** the Phase 1 deliverable as originally scoped (origination volume, LTV
distributions, redemption rate by category × store) **cannot be produced from existing data**.
Likewise Phase 2 (redemption-prediction model) and Phase 3 (lending playbook) are blocked
on data that doesn't exist yet.

The `fpd-cohort` report has the right shape for loan lifecycle (Ticket, Disposition,
Loan Amount, Customer, Last Payment) but only carries days of history, not 12 months.

**Required next step before any model work: build a new Bravo extractor** that pulls
row-level loan lifecycle for the last 12 months across all 5 stores — see Task #3 in
the project plan.

---

## What the existing data does show (this is what's in the workbook)

### Per-store activity in the window
- **Total buys (BT) across 5 stores:** 1,106 tickets, **$81,372.77**
- **Total forfeit pulls (FB) across 5 stores:** 159 tickets, **$26,591.00**
- FB-to-BT dollar ratio: **32.7%** — how much
  of monthly inventory inflow comes from defaulted loans vs. outright buys.

### Per-store breakdown (window: 2026-03-05 → 2026-04-03)
| Store | BT count | BT $ total | FB count | FB $ total |
|---|---:|---:|---:|---:|
| CUL | 303 | $16,314 | 52 | $7,450 |
| HAR | 183 | $20,074 | 40 | $10,850 |
| LEX | 113 | $9,803 | 9 | $1,347 |
| ROA | 237 | $11,987 | 41 | $4,828 |
| WAY | 270 | $23,195 | 17 | $2,116 |


### Inventory sell-through ROI (12-month)
Only HAR, LEX, ROA have `inventory-details` extracted (CUL and WAY are missing — file
this as a gap to fix in the extractor).

Across the 3 stores with data, on items that **actually sold**:
- Total cost basis: **$485,745**
- Total realized revenue: **$996,064**
- Overall gross margin: **105.1%**

### Categories losing money on resale (across HAR/LEX/ROA, ≥3 sold items)
| Store | Category | Sold | Cost | Revenue | Margin |
|---|---|---:|---:|---:|---:|
| ROA | Blu-Ray | 9 | $159 | $41 | **$-119** |
| HAR | Spinning Fishing Pole | 4 | $110 | $101 | **$-9** |


---

## Recommended next steps (in order)

1. **Build the lifecycle extractor** (Task #3). Spec: a new AHK report module in the
   Bravo Data Extraction pipeline that pulls, per store, per 12-month window:
   Ticket #, Customer ID, Loan Date, Principal, Category, Description, Term,
   Maturity Date, Final Status (redeemed/extended/forfeited), Final Disposition Date,
   Payoff Amount, Customer's prior loan count, Customer's prior redemption %.
   This single report unblocks Phases 2, 3, and 4 of the project plan.

2. **Add CUL and WAY to inventory-details extraction.** Currently only HAR/LEX/ROA
   produce the 12-month inventory-details file. Trivial fix in the trigger config.

3. **Use what we have now for one tactical win**: the inventory ROI sheet flags
   categories with negative resale margin. For HAR/LEX/ROA, this is enough to start
   tightening LTV on those categories without waiting for the lifecycle data.

4. **Once the lifecycle extractor is producing**, re-run Phase 1 with the actual
   loan-origination data, then proceed to Phase 2 (model) and Phase 3 (playbook).

---

## Files produced

- `phase1_diagnostic.xlsx` — five-sheet workbook (Summary, Buy Mix, Forfeit Pulls, Inventory ROI, Top BT Categories)
- `phase1_findings.md` — this memo
