# Yield by Asset Class — methodology & STATUS

Built 2026-09-07. Hardened same day. **Read this before extending or debugging asset-class yield.**

> Additive-only. Reads existing End-of-Month exports. Touches no Bravo handler, saved report,
> pipeline cell, or existing scheduled task. Pulls nothing live from Bravo, ever.

---

## What this is
Joshua asked for yield by store, by company, **and by asset class** — his definition: revenue ÷
asset balance, e.g. $10k interest on a $100k loan book = 10%/mo = 120%/yr.

That instinct already matches the company's established metric. `monthly-bonus-targets` has used
`Yield = Net Revenue ÷ prior-month Ending Assets` since 2026, verified to the penny against Preston's
commission basis. This work **decomposes that existing number**; it redefines nothing.

## The definitions (an exact split, not new metrics)

| Metric | Numerator | Denominator |
|---|---|---|
| **Loan Yield** | PSC = In-Store Subtotal Interest + Fees + Misc Charges (MTD) | Ending Loan Base, prior month |
| **Inventory Yield** | Sales Revenue (Profit) = Total Sales − COGS (MTD) | Ending Inventory Base, prior month |
| **Blended** *(unchanged — the bonus-program "Yield")* | Net Revenue = PSC + Sales Profit | Loan Base + Inventory Base, prior month |

The split is exact: `Blended = (loan share × Loan Yield) + (inventory share × Inventory Yield)`.
Company 2026 YTD: 50.3% × 12.24 + 49.7% × 21.92 = **17.05%**. Asserted on every row by the harness.

**Denominator convention:** prior-month ENDING balance, matching `monthly-bonus-targets` exactly.
**Annualization:** monthly × 12 (simple, not compounded) — this is cash thrown off by a roughly
constant asset base, not a reinvested balance.

---

## LAYAWAY — deliberately NOT a third asset class

**It doesn't have a yield, and giving it one double-counts.** Layaway is a payment plan attached to
the inventory asset class: the merchandise stays in the **Inventory Base** until pickup (capital
already counted), and the gross profit lands in **Sales Revenue (Profit)** (return already counted).

**Proven, not asserted.** Bravo's EOM Sales summary satisfies, to the penny across **260 of 260
store-months, 0 mismatches**:

```
Taxable Sales + Taxable Layaway + Taxable Fees
+ Nontaxable Sales + Nontaxable Layaway + Nontaxable Fees  ==  Total Sales
```

and `Sales Revenue (Profit) = Total Sales − COGS`. Layaway is a median **9.0%** of Total Sales
(range 0–29.7%). This identity is re-asserted on every monthly run; if it ever breaks, the report is
withheld and the layaway reasoning gets revisited.

**Report instead — Layaway Collection Velocity** (a sub-metric of inventory):
`(Down Payments + Payments, full month) ÷ prior-month Layaway Balance`.
Company 40.9% (2025) → 37.4% (2026 YTD), while the balance grew 21%.

---

## SCRAP / REFINING — also NOT a separate asset class, but it is a quarter of the business

Joshua asked 2026-09-07 whether scrap yield can be measured. Findings:

**Scrap is a channel on the inventory asset, like layaway — but far bigger.**
- Metal sent to the refiner leaves the Inventory Base via **`Refined (Cost of Sales)`**, exactly the
  way retail COGS does. So the capital is already inside the inventory denominator.
- Refinery **proceeds are already inside Total Sales** too. Verified empirically rather than assumed:
  if the payout were missing from sales, heavy-refining months would show collapsed gross margin.
  Across 100 store-months, months with refining **under 10%** of COGS averaged **50.6%** gross margin;
  months **over 35%** averaged **53.7%**. Correlation of refining share vs gross margin is **+0.28**
  (mildly POSITIVE). Scrap is at least as profitable as the retail floor.
- Therefore a separate "scrap yield" added to inventory yield would double-count, same as layaway.

**Scale — this is the finding worth acting on.** Refining is **24.7% of all cost of goods**
($526,657 of $2,134,886 over 20 months) and rising: 22.3% of COGS in 2025 → **27.6% in 2026**.
It now consumes **5.1% of the inventory balance every month** (was 4.3%). Culpeper is the most
scrap-intensive at **34.9%** of its COGS; Waynesboro the least at 21.7%.

**What IS now reported** (real data, in the CSV and on the page — intensity, never a yield):
`refined_cost` · `scrap_share_of_cogs` · `scrap_burn_of_inventory`.

### What a TRUE scrap yield would need, and why it is not computable today
| Needed | Status |
|---|---|
| Refinery **payout per lot** (numerator) | **Not available.** Commingled into Total Sales in Bravo; no line item separates it. |
| **Dollar value of scrap on hand** (denominator) | **Does not exist.** The `scrap-refining-gold` pipeline captures **pennyweight only** — `Store, Month, BucketName, CreatedOn, Status, StatusDate, CombinedMetalWeightDwt`. No cost, no payout, anywhere. 186 rows in `output/scrap_history.csv`. |

### RESOLVED 2026-09-07 — the settlements exist; refiner is ELEMETAL
Joshua confirmed Elemetal is the current refiner. There is already a
`precious-metals-settlement-handler` scheduled task (daily 9 AM, sonnet) and a
`Projects/Precious Metals Settlements/` project that finds Elemetal settlement emails,
allocates dollars across stores by Bravo scrap weight, and writes a REVIEW workbook.

**The one settlement processed so far (4 Aug 2026, Elemetal Norfolk, INV-20260804-285462):**
- **$66,160.08 net** (gross $66,197.78 less $37.70 shipping/processing/wire), paid by wire
- **608.127 dwt** across all 10 open buckets (2 per store) → **$108.79 per dwt**
- Blended lot (stones + no-stones melted together, one net payment)
- Elemetal pre-melt weight 624.900 dwt vs Bravo 608.127 — **2.7% delta**, worth watching as a
  recurring reconciliation check
- Store split: CUL 26.8% · ROA 27.4% · HAR 24.3% · WAY 13.1% · LEX 8.4%

**Economics derived from it:** cost basis ≈ $27–29k (monthly `Refined (Cost of Sales)`), so
≈ **$37k gross profit at ~57% margin** on one monthly cheque, against company net revenue of
**$224k/month**. Across 2026 volume (4,738 dwt YTD, +31% YoY) the melt channel produces roughly
**$250–340k of gross profit = 14–19% of ALL company net revenue**, and ~22–30% of retail gross
profit. Elemetal also emails a **daily price sheet** (indexed in `unified-search`) — that is the
payout basis behind the "predicted payout" shown on the buckets.

**Open, logged in the Open Items Register:** the Aug 2026 REVIEW file has been unapproved since
Aug 5 (approve by renaming `_REVIEW.csv` → `_CLOSED.csv`); `state.json` shows only ONE settlement
ever processed, so this pipeline is barely exercised.

**MELT vs RETAIL — the decision this data cannot yet make.** Every dwt melted is a dwt not cased.
Directional signal: retail realises ~**$146/dwt** vs melt **$108.79/dwt** (~1.3x). **Sample is
32 sold items out of 17,025** — only 1,859 of 24,306 descriptions carry any DWT and just 101 carry
a gold word, because Bravo descriptions are free text. **Do not publish that ratio as a finding.**
The fix is a store-procedure change: make intake descriptions always carry karat + pennyweight.

**HISTORICAL — the earlier Geib trail (kept for context).** They carry payout per lot and can be joined to the
dwt buckets already tracked per store per month, which would give both a real scrap yield and
payout-per-dwt by store. Searched Joshua's full mail + iCloud index (`unified-search`):
- **Geib Refining** (Peter Spector, peter@geibrefining.com) settlements exist **2019–2022** — the
  format has Lot #, Settlement #, Gross Contents (ozt), Accountability %, Refining Charges.
- **Nothing for 2025 or 2026 in Joshua's mailbox or iCloud.** They are going to a store inbox
  (see `store-credentials`) or to Lainie/Preston — not to him.
- **LGS Refining** (Tim Smith, TimS@LGSrefining.com) was being evaluated Jan–Apr 2026: quoted
  payout tiers (.925 silver and above 90%, below .925 80%), free assay, free containers, 20-business-day
  turnaround, plus a "gold lock" option. **Unconfirmed whether Valley Pawn switched refiners.**
  Payout % directly drives scrap yield, so this matters before any scrap-yield build.

**DO NOT** estimate scrap proceeds from spot gold × an assumed payout %. That is a plug, and
`books-tax-strategy` forbids plugs. Get the settlements.

---

## THE ROOT CAUSE — EOM filename collision (the important part of this document)

Bravo's EOM handler names its output by **END DATE ONLY**:

    output/<END_DATE>_<STORE>_end-of-month.xlsx

`monthly-analytics-prestage` (day 28–31, 8 PM) pulls **six windows per store per month** —
same-month / YTD / trailing-12, for the current AND prior year. **Every one of them ends on the same
day.** Six pulls, one filename. The last one written silently replaces the canonical month file.

Confirmed damage 2026-09-07: `2025-08-31_*` held 9/1/2024–8/31/2025 and `2026-08-31_*` held
9/1/2025–8/31/2026, all 5 stores. **Balances survive** (point-in-time); every **flow** figure — PSC,
Sales Profit, layaway collections — comes back ~11× too large. 10 of 265 files affected.

**This is a RACE, not a deterministic bug — any month can lose.** Independently hit by the Bonus
Program engine, which gates on the same thing (`Bonus Program/RUN_LOG.md`).

### Why it was NOT fixed at the source
Fixing the filename means changing `OutputFilename()`, which every handler shares and ~20 tasks
depend on. Rule #4 forbids that, and the expert board rejected it. Patching `EndOfMonth.ahk` wouldn't
have helped either — the dates *did* take; the file was clobbered afterward. **The collision is made
harmless instead of prevented.**

### The hardening (all additive)

1. **`eom_validate.py`** — the shared trust layer. Every consumer should import this rather than
   globbing for a filename and trusting it.
   - `read_range(path)` → the file's OWN reporting range. **Fast path reads the xlsx zip's
     `sharedStrings.xml` directly** (~1 ms vs ~400 ms through openpyxl — the difference between a
     3-second and a 2-minute run over 300 files).
   - `resolve(store, ym)` → best trustworthy file, trying in order: the canonical pipeline file →
     `monthly-analytics/<ym>/same-month-current_<STORE>.xlsx` →
     `monthly-analytics/<ym+1y>/same-month-prior_<STORE>.xlsx` → `eom_archive/`.
     **A candidate whose range is wrong is rejected outright, never used with a caveat.**
   - `archive_all()` → maintains `eom_archive/<START>_<END>_<STORE>.xlsx`.
   - CLI: `audit` lists every month-end file whose range lies; `resolve LO HI` shows coverage.
2. **`eom_archive/`** — range-stamped, collision-proof by construction. Two windows can no longer
   share a name, so a later pull cannot destroy an earlier one's data. Backfilled 221 files,
   0 unreadable. `archive_all()` runs at the top of every extractor run.
3. **`test_yield_by_asset_class.py`** — 6 checks, hard gate before any publish (see below).
4. **`render_yield_artifact.py`** — regenerates the published page's entire data blob from the CSV.
   No figure on that page is hand-typed, so none can go stale.

> **GOTCHA if you ever re-implement the range read:** the `Reporting Dates:` label sits around
> column T/20 and its VALUE around column AY/51, drifting per store. A truncated column scan finds
> nothing and every file then looks unreadable rather than invalid. Scan the full row width.

---

## Both Augusts were recovered — with zero Bravo contact
`monthly-analytics-prestage` already stages each window under a range-stamped name, so the true
August files were on disk the whole time: `monthly-analytics/2026-08/same-month-current_*` (Aug 2026)
and `.../same-month-prior_*` (Aug 2025). The resolver picks them up automatically. No re-pull was
needed and none should be attempted.

---

## Validation — six checks gate every publish

`python3 test_yield_by_asset_class.py` — exit 0 = safe to publish, exit 1 = **publish nothing**
(Rule 18: withhold, don't caveat). ~90 seconds.

1. **Preston penny match** — June 2026 net revenue per store == his actual commission basis
   (CUL $66,649.27 · HAR $61,666.31 · ROA $36,906.77 · WAY $43,416.44 · LEX $21,455.49).
2. **Bonus-engine cross-check** — Aug 2026 net revenue per store == the figures the Bonus Program
   derived on a completely separate path (CUL 61,998.28 · HAR 54,413.07 · LEX 27,754.28 ·
   ROA 48,167.81 · WAY 40,705.46). Two pipelines, same answer.
3. **Sales-component identity** (sampled ~45 store-months) — what makes the layaway call correct.
4. **Range integrity** — every published month resolves to a true full-month file.
5. **Decomposition** — the two class yields weight-average back to blended on every row.
6. **No partial months** — all 5 stores + COMPANY present.

Checks 1 and 2 are anchored to facts established OUTSIDE this codebase. **Never edit them to make a
test pass** — if they fail, the data changed, not the expectation.

---

## Coverage & headline results

**20 clean months, Jan 2025 – Aug 2026**, all 5 stores. (Dec 2024 exists but has no prior month for
denominators, so it is correctly skipped.)

Company, % per month (annualized ×12 in parentheses):

| Period | Loan | Inventory | Blended |
|---|---|---|---|
| FY2025 (12 mo) | 12.55 (151%) | 20.04 (240%) | 16.05 (193%) |
| 2026 YTD (Jan–Aug) | 12.24 (147%) | 21.92 (263%) | 17.05 (205%) |
| 2025 Jan–Aug *(like-for-like)* | 12.55 | 19.26 | 15.62 |

Per store, 2026 Jan–Aug (loan / inventory / blended):
CUL 11.85 / 23.29 / 18.07 · HAR 11.87 / 20.82 / 15.93 · LEX 12.60 / 18.33 / 15.60 ·
ROA 12.56 / 19.65 / 16.04 · WAY 12.76 / 27.16 / 19.52

**The finding:** loan yield is a near-constant ~12%/mo at every store and has not moved more than a
point in 20 months — it is rate-driven, not management-driven. Inventory yield spans 18.3–27.2% and
is where the entire inter-store performance difference lives. All of 2026's +1.43pt blended gain came
from inventory (gross margin 51.1% → 54.3%); loan yield slipped 0.31pt.

---

## Files (all net-new, additive)

| File | Role |
|---|---|
| `eom_validate.py` | shared trust layer + archive. **Import this in any new EOM consumer.** |
| `yield_by_asset_class.py` | the extractor. `python3 yield_by_asset_class.py [FROM TO]` |
| `test_yield_by_asset_class.py` | 6-check regression harness — the publish gate |
| `render_yield_artifact.py` | rewrites the artifact's data blob from the CSV |
| `artifact/yield-by-asset-class.html` | the published page (canonical copy) |
| `YIELD_RUN_LOG.md` | run history; all technical detail goes here, never to Slack |
| `output/yield_by_asset_class.csv` / `.json` | 120 rows (20 months × 5 stores + COMPANY) |
| `eom_archive/` | range-stamped, collision-proof EOM archive |

**Scheduled:** `yield-by-asset-class-monthly` — day 6, 2:00 PM, model `claude-sonnet-5`.
**Type B** (reads exported files only; zero Bravo contact, no trigger, no computer-use), so no
contention check is required and it can sit anywhere in the day. Day 6 chosen because analytics
staging (day 28–31) and the month-end pulls (day 1–3) have all settled by then; the only other day-6
task fires at 9 AM.

Artifact URL: `https://claude.ai/code/artifact/a2c1c285-29a3-4c6c-9388-f9b460063239` (private).

## Deliberately NOT changed (Rule #4)
`EndOfMonth.ahk` · `OutputFilename()` · `monthly-analytics-prestage` · `layaway-yield-weekly` ·
`store_kpis_compile.py` · `bonus_kpis_extract.py` · any saved Bravo report or existing task.

## Open
1. **`layaway-yield-weekly` period framing** — divides month-to-date collections by a full balance,
   so its published % tracks the calendar rather than performance (a 14th-of-month pull reads ~half
   as good as a 30th). Extraction itself verified correct, cell-for-cell against
   `layaway_yield_compile.py` for 2026-07-14, all 5 stores. Joshua's call: move to a full-month basis
   or rename it so it doesn't read as a rate.
2. **Other EOM consumers still trust filenames** — `store_kpis_compile.py`, `layaway_yield_compile.py`
   and `monthly-analytics`' own parser glob for `<date>_<STORE>_end-of-month.xlsx` without checking
   the range. They are exposed to the same collision. The one-line fix for each is to call
   `eom_validate.resolve()`. Not done here (Rule #4 — they're hardened and in production); worth
   doing deliberately, one at a time, with a smoke test each.
