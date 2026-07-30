# Discount Outlier Review — Data Schema Notes

## Data source (confirmed 2026-07-28/29, real CSVs read, not assumed)

Point-of-sale discount data was **not** a new Bravo report. It already exists in Joshua's
own saved Bravo report **"Claude Sold Inv Details"** (Inventory module, Custom Reports),
which is already pulled daily by the additive `jewelry-margin-sold` pipeline cell
(handler `reports/JewelrySoldMargin.ahk`), originally built 2026-07-28 for an unrelated
12-vs-18-month jewelry-scrap decision project. That cell's AHK handler does **not** filter
by category — it exports every SOLD item across all categories. This build reuses that
existing CSV output read-only; no new Bravo saved report, no new AHK handler, no watcher
restart, and no new pipeline cell were needed.

## Column schema (as exported)

```
Number,Status,Category,Description,Cost,Price,Last Sold Price,Date
```

- `Number` — inventory/item number (or a reused generic SKU — see below)
- `Status` — filtered to `SOLD` rows only
- `Category` — Bravo category (Firearm Scope, Pistol, Coin, Miscellaneous Manufactured Good, etc.)
- `Description` — free-text item description
- `Cost` — Bravo's cost basis for the item
- `Price` — the ticketed/asking price at time of sale (i.e. what it was priced to sell at)
- `Last Sold Price` — what it actually sold for (the real transaction price)
- `Date` — sale date

**Discount = Price − Last Sold Price.** This is a *different* signal from Sold Margin
Review's realized-margin math (Cost vs Sale Price) — a high-margin item can still carry a
heavy discount (leakage the margin math never surfaces), and a thin-margin item can carry
zero discount (a pricing problem, not a discounting-behavior problem). Both projects are
kept separate on purpose.

## Data-quality issues found and handled

### 1. Generic/bulk SKUs (excluded from ranking)
Rows with a purely numeric `Number` (e.g. `1000`, `5000`, `8000`, `8009`) are reused
across many unrelated physical items (bullion, coins, misc tools) — `Price` on these rows
is not a meaningful per-item asking price. Detected via `GENERIC_SKU_RE = ^\d+$` and
excluded from all ranking/flagging (still counted in a data-quality footnote).

### 2. Firearm-paperwork placeholder rows (excluded from ranking)
Firearms awaiting FFL paperwork/pricing show `Cost=$0.00, Price=$0.01, Last Sold
Price=$0.00` in Bravo — a data-entry placeholder, not a real transaction. Without
filtering, this falsely triggers "100% discount, sold into a loss" flags. Confirmed via a
live 40-row CUL sample (2026-07-28/29): 5 of 40 rows showed this exact pattern, all
firearms. Detected via `PLACEHOLDER_PRICE_MAX = 0.01` (Price <= $0.01) and excluded the
same way as generic SKUs.

## Verification

Both fixes were proven against the real 40-row CUL sample before shipping: without the
placeholder-price fix, the demo produced 12 flags including 5 false firearm "100% off"
flags; with the fix, 7 legitimate flags remained (e.g. a 22" S925 chain 26.9% off, a Marc
Ecko watch 62.0% off, a Smith & Wesson M&P 15-22 rifle 21.4% off at $74.99).

## Known limitation — filename pattern dependency

The script looks for `{date}_to_{date}_{store}_jewelry-margin-sold.csv` in the Bravo
Data Extraction `output/` folder (falls back to a couple of alternate naming patterns).
This is the exact naming convention the `jewelry-margin-sold` cell currently uses for a
single-day range. If that cell's output naming ever changes, this script's
`_FILENAME_CANDIDATES` list needs a new pattern added — it is additive-safe to edit
(this script only, never the AHK handler or pipeline cell itself).
