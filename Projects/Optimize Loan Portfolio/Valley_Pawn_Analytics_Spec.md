# Valley Pawn Comprehensive Analytics Spec
**Full Circle Finance Inc DBA Valley Pawn — Data Architecture for Fortune-500-Grade Decision Support**

**Author:** Claude (with Joshua Davis)
**Date:** 2026-05-22
**Status:** Draft v1 — ready for review

---

## Executive Summary

### Current state
Valley Pawn runs five stores producing combined ~$2.6M / year of revenue (per VP BONUS FINAL methodology). The analytical infrastructure today is:

- **Store-level monthly revenue + yield** — already produced by the monthly-bonus-targets workflow. Best data we have. Drives bonus targets.
- **Bravo POS** — the system of record. Holds every loan, buy, sale, layaway, inventory item, and customer interaction.
- **Bravo Data Extraction pipeline** — AHK watcher in a Parallels VM that pulls saved Bravo Ad Hoc reports to CSV on demand.
- **QBO** — books closed monthly. Has consolidated P&L.
- **Gusto** — labor hours and payroll by store.
- **Existing pipeline reports** — loans-75-days-past-due, layaways, buys-from-public, inventory, inventory-details, aged-inventory-summary, employee-activity, safe-register-journal, chekkit-inactives, fpd-cohort.

What's missing analytically: everything that lets us answer **why** a number moved, and **what to do** about it. We have outcomes but not the per-record economics that explain them.

### Target state
A unified analytics layer across **five business segments** plus a **CFO/cross-segment view**, all driven by structured data extracts from Bravo (plus QBO and Gusto where appropriate). Output: live dashboards per segment, monthly written reviews, and predictive models that turn raw activity into specific actions (which loans to write, which inventory to mark down, which categories to lean into).

### What this document is
A complete spec of:
1. The KPIs each segment requires
2. The exact data fields needed to compute those KPIs
3. Where each field lives (Bravo source, external feed) and how to extract it
4. The dashboards / decision documents that fall out
5. The phased build plan to get from today to full deployment

### Phased build (12 weeks)
- **Phase 1 (Wk 1-2):** Loan Portfolio — new Bravo Ad Hoc, pipeline cell, dashboard
- **Phase 2 (Wk 3-4):** Retail + Inventory (combined; inventory feeds retail margin)
- **Phase 3 (Wk 5-6):** Buys + Gold/Silver Spot integration
- **Phase 4 (Wk 7-8):** Layaway
- **Phase 5 (Wk 9-10):** Cross-segment CFO view + QBO/Gusto joins
- **Phase 6 (Wk 11-12):** Predictive models (redemption probability, customer LTV, markdown timing)

Each phase delivers a usable dashboard before moving to the next. Nothing is built that isn't actionable.

---

## Segment 1: Loan Portfolio Analysis

### What it answers
- Which collateral categories produce the best risk-adjusted yield?
- Which PBs are writing loans that perform vs. losing money?
- What's our customer-LTV mix — repeat customers vs. one-time?
- How fast is capital recycling? Where's it sitting idle vs. earning?
- Where's the LTV creep that's hurting forfeit recovery?

### KPIs

| KPI | Formula | Cadence |
|---|---|---|
| PSC Yield (monthly) | PSC + storage fees collected / avg outstanding loan balance | Monthly |
| PSC Yield (annualized) | Monthly yield × 12 | Monthly |
| Redemption Rate (cohort) | % of loans originated in month M redeemed by pull date | Monthly by origination cohort |
| Forfeit Rate (cohort) | % originated in M that forfeited | Monthly by cohort |
| First Payment Default (FPD) % | % of loans where customer made zero payments | Monthly |
| Average Days Outstanding | mean(disposition date − pawn date) | Monthly |
| Loan Loss Rate | (forfeit principal − inventory recovery) / total principal originated | Quarterly |
| Risk-Adjusted Yield | PSC Yield − Loan Loss Rate | Monthly |
| Avg LTV at Origination | mean(loan / appraised value) per category, per PB | Monthly |
| Customer LTV | mean total PSC per customer over lifetime | Quarterly |
| Repeat Customer Rate | % of new loans to customers with ≥2 prior loans | Monthly |
| Capital Velocity | total loan dollars originated / average outstanding balance | Monthly |
| Loan Mix by Category ($) | % of dollars deployed per top-level category | Monthly |
| Concentration Risk | Max % of book in any single category / customer / employee | Quarterly |

### Data fields required (per loan)

| Field | Source | Notes |
|---|---|---|
| Ticket Number | Bravo Loans | Primary key |
| Pawn Date | Bravo Loans | Origination |
| Store | Bravo Loans | |
| Customer ID | Bravo Loans | For customer LTV joins |
| Customer Name | Bravo Loans | Display |
| Employee/PB ID | Bravo Loans | Who wrote it |
| Top-level Category | Bravo Loans (currently missing on layout) | Gold, Tools, Electronics, etc. |
| Sub-category | Bravo Loans (missing) | 14k jewelry, Milwaukee tools, etc. |
| Full Description | Bravo Loans (missing) | Item description |
| **Appraised Value** | Bravo Loans (missing) | Needed for LTV |
| Loan Amount (principal) | Bravo Loans | Have it |
| LTV % | Computed | = loan / appraised |
| Initial PSC ($) | Bravo Loans (missing) | First-month interest charged |
| Storage/Insurance Fee ($) | Bravo Loans (missing) | Monthly fee |
| Total Monthly Charge ($) | Bravo Loans (missing) | PSC + storage |
| Term (days) | Bravo Loans (Due Date − Pawn Date) | Derivable |
| Due Date | Bravo Loans | Have it |
| Pull Date | Bravo Loans | Have it |
| Extensions Taken (count) | Bravo Loans (missing) | Number of times extended |
| Total PSC Paid ($) | Bravo Loans (missing) | Sum across all extensions — **revenue!** |
| Total Fees Paid ($) | Bravo Loans (missing) | Sum across all extensions |
| Disposition | Bravo Loans | Have it |
| Disposition Date | Bravo Loans | Have it |
| Final Payoff Amount ($) | Bravo Loans (missing) | What customer paid at redemption |
| Inventory # (if forfeited) | Bravo cross-reference | For retail join |

**What we have now:** Ticket, Pawn Date (derivable), Store, Customer, Loan Amount, Disposition, Disposition Date, Due Date, Pull Date.

**What's missing and blocks meaningful analysis:** Appraised Value, all PSC / fee fields, Category, Employee, extension history.

### Extraction strategy
**Build a new saved Ad Hoc report in Bravo:** "Claude Loan Master 2026"
- Ticket Kind = LOAN
- All dispositions (active, redeem, forfeit, void)
- Date range overridable per pipeline trigger
- Sort: Pawn Date ascending (oldest first — most resolved data first)
- Columns: every field above
- Saved column layout: "Claude Loan Master Columns" (new — don't modify any existing layout)

**Pipeline cell:** clone the existing LoanPortfolio2026.ahk to LoanMaster.ahk. Same Update→Ok flow. Monthly slicing.

### Dashboards / deliverables enabled

1. **Loan Portfolio Health** (live) — per-store PSC yield, redemption rate, forfeit rate, FPD%, capital velocity. Refreshes weekly.
2. **Cohort Performance** (monthly review) — for each origination month, what % redeemed / forfeited / still on loan. Spot quarter-over-quarter drift.
3. **Per-PB Lending Quality Scorecard** — every PB ranked on redemption rate, LTV discipline, forfeit recovery rate. Coaching tool.
4. **Per-Category Lending Playbook** — recommended max LTV by category, per store. Updated quarterly from model.
5. **Customer LTV Segmentation** — top customers by lifetime PSC, repeat-customer cohort retention curves. Drives loyalty/loan-renewal outreach.
6. **Concentration Risk Alerts** — flag when any category or PB exceeds the threshold for a given store.

---

## Segment 2: Buy Analysis

### What it answers
- Are we paying the right price relative to spot (gold/silver) and resale comp?
- Which categories produce the best buy-margin?
- Which PBs are good vs. bad buyers? (Different skill from lending.)
- What's our buy-to-sell cycle time? Capital tied up too long?
- Are we missing buy opportunities? (E.g., quoting too low and losing the seller.)

### KPIs

| KPI | Formula |
|---|---|
| Buy Volume (count, $) | Sum per period |
| Avg Buy Ticket | $ buys / count |
| Gross Margin % (Buy → Sale) | (sale price − buy price) / sale price |
| Buy-to-Spot Ratio (Au/Ag) | buy price / (weight × purity × spot price) — should be 50–70% |
| Days to List | mean(list date − buy date) |
| Days to Sell (from buy) | mean(sale date − buy date) |
| Sell-through 30/60/90 | % of items bought sold within X days |
| Buy Conversion Rate | quotes accepted / quotes given (if quote data captured) |
| Scrap Recovery $ | $ from items sold to refiners |
| Buy Volume per PB per Day | count + $ |

### Data fields required (per buy)

| Field | Source | Notes |
|---|---|---|
| Buy Ticket # | Bravo Buys | Primary key |
| Buy Date | Bravo Buys | |
| Store | Bravo Buys | |
| Customer ID | Bravo Buys | For repeat-seller tracking |
| Employee/PB ID | Bravo Buys | Who bought it |
| Top-level Category | Bravo Buys | |
| Sub-category | Bravo Buys | |
| Description | Bravo Buys | |
| **Weight (g/dwt)** | Bravo Buys (Au/Ag only) | For spot ratio |
| **Purity (karat / fineness)** | Bravo Buys (Au/Ag only) | For spot ratio |
| Buy Price ($) | Bravo Buys | |
| Spot Price on Date (Au/Ag) | External feed (kitco / LBMA / metalsapi) | Daily price |
| Buy-to-Spot Ratio | Computed | |
| Listed Date | Bravo Inventory | When it hit the floor |
| Listed Price | Bravo Inventory | |
| Last Sold Price | Bravo Inventory | If sold |
| Sale Date | Bravo Sales | |
| Days to List / Sell | Computed | |
| Status (active/sold/scrap) | Bravo Inventory | |
| Margin $ | Computed | sale − buy |
| Margin % | Computed | (sale − buy) / sale |

**What we have now:** buys-from-public report has Ticket, Category, Description, Loan Amount (buy price). Missing weight, purity, employee, customer, listing/sale linkage.

### Extraction strategy
**New saved Ad Hoc report in Bravo:** "Claude Buy Master 2026"
- Ticket Kind = BUY
- All buys (active + sold + scrapped)
- Columns: every field above
- Layout: "Claude Buy Master Columns" (new)

**External data:**
- **Daily gold/silver spot price feed.** Free APIs: metals-api.com (free tier 50 calls/month), GoldAPI.io. Pull once per day, store in a CSV: `daily_spot_prices.csv` with columns `date, gold_usd_oz, silver_usd_oz, platinum_usd_oz`.

**Pipeline cell:** new BuyMaster.ahk handler.

### Dashboards / deliverables enabled

1. **Buy Performance Dashboard** — buy volume, margin %, days-to-sell, by store/category/PB.
2. **Gold/Silver Buy Discipline** — daily report: did each store stay within target buy-to-spot ratio? Outliers flagged.
3. **Per-PB Buy Quality Scorecard** — separate from lending. Some PBs are better at one than the other.
4. **Slow-Moving Buys Watchlist** — buys aged 60+ days unsold, with recommended markdown.
5. **Scrap vs. Retail Decision Support** — for each aged item, is scrap recovery better than continued retail try?

---

## Segment 3: Retail Analysis

### What it answers
- Which categories sell fastest, with the best margin?
- Are we marking down too late (lost margin) or too early (left money on table)?
- What's our inventory turn vs. industry benchmarks?
- Same-store sales growth — which stores winning, which dragging?
- What's the optimal mix of forfeit-sourced vs. buy-sourced vs. wholesale inventory?

### KPIs

| KPI | Formula |
|---|---|
| Retail Revenue (period) | sum sales $ |
| Avg Ticket Size | sales $ / receipt count |
| Units per Transaction (UPT) | items / receipt count |
| Same-Store Sales Growth (SSSG) | (current − prior year same month) / prior year |
| Gross Margin % | (sale − cost basis) / sale |
| Gross Margin Return on Investment (GMROI) | gross margin $ / average inventory $ |
| Inventory Turn (annual) | COGS / average inventory $ |
| Days Sales in Inventory (DSI) | 365 / inventory turn |
| Sell-Through Rate (30/60/90 day) | % of items sold within X days of listing |
| Markdown % (period) | total markdown $ / original list $ |
| Markdown Effectiveness | sell-through pre vs. post markdown |
| Top SKU Concentration | top 10 SKUs % of revenue |
| Category Revenue + Margin | rolled up |
| Sourcing Mix | % rev from forfeit / buy / wholesale |
| Avg Days on Shelf at Sale | mean(sale date − list date) |

### Data fields required

**Per sale (one row per line item):**

| Field | Source |
|---|---|
| Sale Receipt # | Bravo Sales |
| Sale Date | Bravo Sales |
| Store | Bravo Sales |
| Customer ID | Bravo Sales |
| Employee ID | Bravo Sales |
| Inventory # (line) | Bravo Sales |
| Sale Price (line) | Bravo Sales |
| Discount (line) | Bravo Sales |
| Cost Basis (line) | Bravo Sales — must surface |
| Sale Tax | Bravo Sales |
| Payment Method | Bravo Sales |

**Per inventory item (master record):**

| Field | Source |
|---|---|
| Item # | Bravo Inventory |
| Category (top + sub) | Bravo Inventory |
| Description | Bravo Inventory |
| **Origin** (forfeit ticket# / buy ticket# / wholesale receiving#) | Bravo Inventory |
| Cost Basis | Bravo Inventory |
| Original List Price | Bravo Inventory |
| Current Price | Bravo Inventory |
| **Markdown History** (date + new price + % off) | Bravo Inventory — must surface as separate report or via item history |
| Date In (forfeit/buy/receive) | Bravo Inventory |
| Date Listed (on floor) | Bravo Inventory |
| Date Sold (if sold) | Bravo Inventory |
| Days on Shelf | Computed |
| Status (active/sold/aged/scrap/damaged) | Bravo Inventory |
| Location (case/bin/store) | Bravo Inventory |

**What we have now:** inventory-details has Number, Status, Category, Description, Cost, Price, Last Sold Price, Date. Missing markdown history, date-in, date-listed, origin linkage, line-level sale data.

### Extraction strategy

**New saved Ad Hoc reports (likely two):**
1. **"Claude Sale Master 2026"** — line-level sales. Ticket Kind = SALE. Date range overridable. Full line detail per receipt.
2. **"Claude Inventory Master 2026"** — full item master with markdown history. May need to combine inventory + an "item history" extract; if Bravo doesn't expose markdown history in a single report, build a daily snapshot CSV and compute markdowns by diffing day-over-day. The diff approach is reliable and doesn't require any Bravo column changes.

**Pipeline cells:** SaleMaster.ahk + InventoryMaster.ahk + DailyInventorySnapshot.ahk (the latter feeds markdown history).

### Dashboards / deliverables enabled

1. **Retail Performance Dashboard** — daily/weekly/monthly revenue, margin, units, by store. Heatmap of categories.
2. **Same-Store Sales Tracker** — current month vs. prior year, monthly trend. Variance vs. plan.
3. **Inventory Aging + Markdown Trigger** — items crossing into 60/90/180/365 day buckets, with recommended markdown.
4. **GMROI Ranking** — categories ranked by margin × turn. Reallocate floor space to winners.
5. **Top Sellers / Slow Sellers** — drives wholesale buying decisions.
6. **Sourcing Mix Analysis** — what % of retail revenue comes from forfeits vs. buys vs. wholesale. Informs lending/buying strategy.

---

## Segment 4: Layaway Analysis

### What it answers
- Are layaways profitable, or are they tying up sellable inventory for low conversion?
- Which customers / categories / stores have the best completion rates?
- Should we adjust down-payment requirements or fee structure?

### KPIs

| KPI | Formula |
|---|---|
| Layaway Origination ($ + count) | Sum per period |
| Active Layaway Balance | Sum of unpaid balances on active layaways |
| Completion Rate | % paid to zero |
| Default Rate | % cancelled with item returned to floor |
| Avg Days to Complete | mean(complete date − start date) |
| Avg Payment Frequency | payment count / days active |
| Layaway Fee Revenue ($) | Sum of non-refundable fees + restocking |
| % of Retail in Layaway | active layaway $ / total inventory $ |
| Avg Down Payment % | down / total |
| Aging Mix | $ in 0-30 / 31-60 / 61-90 / 90+ buckets |

### Data fields required (per layaway)

| Field | Source |
|---|---|
| Layaway Ticket # | Bravo Layaways |
| Start Date | Bravo Layaways |
| Store | Bravo Layaways |
| Customer ID | Bravo Layaways |
| Employee ID | Bravo Layaways |
| Items in Layaway (Inventory #, Price) | Bravo Layaways — line level |
| Total Layaway $ | Bravo Layaways |
| Down Payment $ | Bravo Layaways |
| Layaway Fee $ | Bravo Layaways |
| Payment Schedule | Bravo Layaways (if set) |
| Payment History (date + amount) | Bravo Layaways |
| Status (active / completed / defaulted / cancelled) | Bravo Layaways |
| Completion Date | Bravo Layaways |
| Cancellation Reason | Bravo Layaways (if captured) |

**What we have now:** layaways report has aggregate counts only (overdue, past_pmt_due, etc.). Missing all line-level detail.

### Extraction strategy

**New saved Ad Hoc:** "Claude Layaway Master 2026" — one row per layaway with line items + payment history. May require Bravo Layaway Ad Hoc which exists; verify and extend column set.

### Dashboards / deliverables enabled

1. **Layaway Health Dashboard** — active count, balance, completion rate, default rate by store.
2. **Layaway Aging Watchlist** — layaways at risk of default (no payment 30+ days). Triggers customer outreach.
3. **Profitability Test** — net P&L per layaway (fee income − inventory carrying cost during layaway − default loss). Decide whether layaway program is net contributor or drag.

---

## Segment 5: Aged Inventory Analysis

### What it answers
- What's our true dead-stock exposure?
- Where do we have categories aging faster than they should be?
- Is our markdown cadence aggressive enough?
- Should certain aged items go to wholesale, auction, or scrap?

### KPIs

| KPI | Formula |
|---|---|
| Age Mix ($ + count) | $ per bucket (0-30, 31-60, 61-90, 91-180, 181-365, 365+) |
| Aged % of Total Inventory | (180+ bucket $) / total inventory $ |
| Dead Stock $ | 365+ bucket $ |
| Dead Stock % | dead stock $ / total inventory $ |
| Recovery Rate by Age | sale price / original list price, per bucket |
| Markdown Cycle Time | mean days between price changes |
| Velocity by Category × Age | rate items move bucket-to-bucket |
| Scrap Rate | % of inventory sold to refiners |
| Carrying Cost Estimate | aged $ × annual cost-of-capital rate × time |

### Data fields required
All derivable from inventory + markdown history + sale data (no new fields beyond Segment 3). Aged inventory is a *view* over the inventory master.

The existing `aged-inventory-summary` extract provides category × age-bucket snapshots — useful for daily/weekly health checks but doesn't support item-level decisions. Item-level requires the Inventory Master extract (Segment 3).

### Dashboards / deliverables enabled

1. **Aged Inventory Health Dashboard** — live aging mix, trend over time. Targets per category.
2. **Dead Stock Action List** — every item 365+ days, recommended action (markdown / scrap / wholesale / transfer to another store).
3. **Markdown Cadence Audit** — per category, is our markdown cycle aggressive enough vs. industry benchmarks?
4. **Scrap Recovery Tracker** — for jewelry / metals, scrap revenue vs. continued retail attempt.

---

## Segment 6: Cross-Segment CFO View

### What it answers
- What's our true operating margin, fully loaded?
- Where's our capital best deployed: loans or inventory?
- Which store is most efficient on labor?
- Are we growing at all in real terms (vs. inflation, vs. peers)?
- What's the ROI on a hypothetical new store?

### KPIs

| KPI | Formula |
|---|---|
| Total Revenue (period) | PSC + retail + buy margin + layaway fees |
| Revenue Mix % | each segment / total |
| Capital Deployment Mix | Loans / Inventory / Cash, % of total assets |
| Total Capital Deployed | Loans + Inventory + Cash |
| Capital ROI (annualized) | net income / avg capital × 12 |
| Operating Margin % | (revenue − COGS − OpEx) / revenue |
| Same-Store Revenue Growth (annual) | YoY total revenue per store |
| Revenue per Labor Hour | total revenue / total labor hours (Gusto) |
| Revenue per Sq Ft | total revenue / store sq ft |
| Customer LTV (all segments) | total customer revenue across loans, retail, buys, layaway |
| Bonus Target vs. Actual Variance | per store per month |
| Capital Velocity | total revenue / avg capital × period |
| Working Capital | current assets − current liabilities (from QBO) |

### Data fields required

**From this project (Segments 1-5):** all per-loan, per-sale, per-buy, per-layaway, per-inventory records joined on customer + store + date.

**From QBO:** monthly P&L per store (already published via the `weekly-payroll-to-qbo` and existing GL exports). Joined on store + month.

**From Gusto:** labor hours per store per day (already accessed by `daily-clockin-check`). Joined on store + date.

**From census / external:** demographic data per store ZIP for the "demographic mix" cut. (Lower priority; useful for site selection.)

### Dashboards / deliverables enabled

1. **CFO Daily Brief** — single page: yesterday's revenue, week-to-date vs. plan, cash position, top alerts.
2. **Monthly Board Report** — auto-generated PDF with all KPIs, segment commentary, plan vs. actual variance.
3. **Store P&L Roll-up** — full P&L per store, fully loaded with allocated overhead.
4. **Capital Allocation View** — where each dollar is sitting (loans vs. inventory vs. cash) per store, with ROI on each pile.
5. **Customer 360** — every customer's history across loans, buys, retail, layaway. Drives loyalty program and targeted outreach.
6. **Bonus Reconciliation** — actual vs. target per store, with attribution (which segment drove the variance).

---

## Architecture Recommendation

### Data flow
```
Bravo POS (in Parallels VM)
   │
   ├── Saved Ad Hoc Reports (Loan Master, Buy Master, Sale Master,
   │   Inventory Master, Layaway Master, Daily Snapshot)
   │
   ▼
AHK Pipeline (one handler per master report)
   │
   ▼
CSV outputs (Bravo Data Extraction/output/)
   │
   ▼
[Recommended addition] SQLite / DuckDB local warehouse
   │
   ├── Joins with QBO monthly P&L
   ├── Joins with Gusto labor hours
   └── Joins with external feeds (gold spot, demographics)
   │
   ▼
Per-segment dashboards (HTML/Chart.js) + monthly written reviews + predictive models
```

### Why a small local warehouse
The pipeline currently dumps CSVs and analysis is one-shot Python scripts re-reading raw files. That scales to ~50k rows per report. Once we're pulling a year of per-loan + per-sale + per-buy + per-layaway data, we're at ~500k rows total and joins between segments get painful in pandas. A local SQLite or DuckDB file (single file, no server, queryable from Python or any BI tool) solves this in one weekend of work. Estimated effort: 1 day to stand up, 2 days to write the ingest scripts that load CSVs → tables.

### Refresh cadence (recommended)
- **Daily 6am:** inventory snapshot, safe register journal, gold/silver spot
- **Daily 6pm:** funds verification (existing)
- **Weekly Mon 5am:** loan master, sale master, buy master, layaway master (incremental — last 8 days)
- **Monthly 1st 6am:** full-month QBO P&L pull, full-month Gusto hours pull, monthly board report generation

---

## Phased Build Plan (12 weeks)

### Phase 1 — Loan Portfolio (Wk 1-2)
**Deliverable:** Loan Portfolio Health Dashboard + Cohort Performance Review
**Work:**
- Build "Claude Loan Master 2026" saved Ad Hoc in Bravo (Joshua, ~30 min one-time)
- Build "Claude Loan Master Columns" column layout (Joshua, ~10 min)
- Clone LoanPortfolio2026.ahk → LoanMaster.ahk handler (Claude, ~2 hrs)
- Register pipeline cell + watcher restart (Claude, ~30 min)
- Drop trigger for trailing 12 months (Claude, queues 12 monthly cells × 5 stores = 60 cells, ~3 hrs runtime)
- Build SQLite ingest script for loan master (Claude, ~1 day)
- Build Loan Portfolio Health Dashboard HTML (Claude, ~1 day)
- Build Cohort Performance written review template (Claude, ~half day)
**Stops:** AHK enumerator pagination cap (need to fix or stay with monthly slicing). LEX dropdown bug (resolved with monthly slicing).

### Phase 2 — Retail + Inventory (Wk 3-4)
**Deliverable:** Retail Performance Dashboard + Aged Inventory Action List
**Work:** Sale Master + Inventory Master Ad Hoc reports + handlers + ingest + dashboards.

### Phase 3 — Buys + Spot Integration (Wk 5-6)
**Deliverable:** Buy Performance Dashboard + Gold/Silver Buy Discipline report
**Work:** Buy Master Ad Hoc + handler + spot-price daily fetch + ingest + dashboards.

### Phase 4 — Layaway (Wk 7-8)
**Deliverable:** Layaway Health Dashboard + Layaway Aging Watchlist
**Work:** Layaway Master Ad Hoc + handler + ingest + dashboards.

### Phase 5 — Cross-segment CFO View (Wk 9-10)
**Deliverable:** CFO Daily Brief + Monthly Board Report (auto-generated)
**Work:** QBO + Gusto joins, P&L roll-up, customer 360 join, board report template.

### Phase 6 — Predictive Models (Wk 11-12)
**Deliverable:** Redemption probability model + customer LTV scoring + markdown timing model
**Work:** Train scikit-learn models on the full warehouse, deploy as functions called from dashboards.

### What you get along the way
At the end of each phase, you have a usable dashboard + a monthly written review. By Wk 4 you have actionable lending + retail insight. By Wk 10 you have full CFO-grade visibility. By Wk 12 you have predictive decision support.

---

## Open questions for you

1. **Bravo Ad Hoc field availability.** Some fields I'm assuming Bravo can expose (Appraised Value, PSC paid history, markdown history). Need to confirm — easiest: open the Bravo Ad Hoc builder for Loans and screenshot the full column picker. Same for Buys, Sales, Layaways.
2. **External cost of capital rate.** For carrying-cost calculations on aged inventory, what rate should I use? (Industry typical: 12-25% annual.)
3. **Sq footage per store** — for revenue/sqft. Can pull from lease docs or estimate.
4. **Demographic data depth.** Are census-tract income/poverty stats sufficient, or do you want richer data (Claritas, ESRI)? Census is free.
5. **Dashboard hosting.** Cowork artifacts (live, in this app) work for personal use. For sharing with managers/PBs, may want a hosted static site (Cloudflare Pages, Netlify) reading the same CSV/JSON outputs. Either works; just pick.
6. **Build order priority.** I have it as Loan → Retail → Buy → Layaway → CFO → Models because loan is the biggest revenue contributor and most underanalyzed. Want a different order? (E.g., retail first because of inventory pain right now.)

---

*End of spec. Total: 6 segments, 60+ KPIs, 8 new Bravo Ad Hoc reports, 12-week build plan.*
