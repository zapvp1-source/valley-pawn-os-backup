# Optimize Loan Portfolio — Project STATUS

> **READ THIS FILE FIRST.** Every session that touches this project starts here. Append to it as work progresses. Do not restart what's already been done.

**Last updated:** 2026-06-10 (framework workbook built from existing data; Bravo pull still blocked)
**Owner:** Joshua Davis

---

## Project Goal

Optimize Valley Pawn's loan portfolio — maximize **true ROI per dollar of capital deployed** by identifying which collateral categories, loan sizes, and patterns produce the best blend of:
- interest income on redeemed loans, and
- post-forfeit resale margin on PFI'd items,
weighted by outcome mix (redeem vs. forfeit vs. FPD).

Secondary: flag collateral categories and patterns that go into **FPD (First Payment Default)** or **forfeit** disproportionately, so the counter can avoid them or price them more conservatively.

---

## Hard Rules for This Project (Joshua 2026-05-20)

- **DO NOT modify** any existing saved Ad Hoc report in Bravo (including "Claude Loan Reviews", "Claude Low Dollar Loans", etc.).
- **DO NOT modify** any existing AHK handler in `Bravo Data Extraction/reports/`.
- **DO NOT modify** any existing pipeline cell entry in `bravo_watcher.ahk` or `bravo_export.ahk`.
- **DO NOT touch** the Monday combined Bravo run, daily funds verification, weekly aged inventory, weekly employee rankings, weekly loan/layaway review, or any other scheduled task.
- This project ONLY adds new infrastructure: new saved report, new handler file, new pipeline cell name, new entries (additive) in dispatch tables. Existing rows stay byte-identical.

---

## Decisions Already Made (do not re-ask)

| Question | Decision |
|---|---|
| Data source | Bravo Data Extraction pipeline (Joshua keeps his computer free) |
| Time window | Trailing 12 months |
| Stores | All 5 (CUL, HAR, LEX, ROA, WAY) |
| Customer-level segmentation | **NO** — collateral + category only |
| Optimization target | True ROI per $ deployed (NOT raw redemption rate, NOT volume) |
| Deliverables | All three: (1) loan-window decision guide, (2) Word report + Excel model, (3) live HTML dashboard |
| Granularity | Subcategory level (e.g., "Gold → 14k jewelry"), not just top-level category |
| FPD definition | Loan where the first interest payment was missed and the loan went to forfeit/lost without any payment |

---

## Data Inventory

### What's already in the pipeline output folder
`/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/`

| Report | Coverage | Notes |
|---|---|---|
| `aged-inventory-summary` | 2026-05-12, -13, -18 snapshots, all 5 stores | Forfeit-inventory aging — KEY input for forfeit→resale leg |
| `loans-75-days-past-due` | 2026-05-12, -13, -18 snapshots, all 5 stores | Currently at-risk balance, not historical |
| `fpd-cohort` | 2026-05-18 partial (CUL has ~10 rows, others empty) | Saved Ad Hoc reports not yet built per-store — needs setup in Bravo before this report is reliable |
| `low-dollar-loans` | 2025-05-01 → 2026-04-30 (12 mo), all 5 stores — but only WAY/LEX/ROA have rows; CUL & HAR are header-only | Partial — see pipeline status |
| `low-dollar-buys` | Same window, similar partial coverage | Buys are not loans — useful for inventory context only |
| `employee-activity` | 2026-05-01, all 5 stores | Not directly relevant to portfolio optimization |
| `safe-register-journal` | Daily | Not relevant |

### What's MISSING for the analysis we want

These data shapes are not currently produced by the pipeline as one-shot reports:
1. **Loan-cohort outcomes**: every loan originated in last 12 months, tagged with disposition (redeemed / forfeited / active / FPD), category, subcategory, principal, interest collected if redeemed.
2. **Forfeit-to-sale margin**: for items that forfeited and were resold, the sale price, days-to-sell, and gross margin vs. original loan principal.

The closest existing report is **`loan-reviews`** (uses "Claude Loan Reviews" saved Ad Hoc report in Bravo, handler is `reports/LoanReviews.ahk`). Need to verify what columns and filters that saved report has — it may already cover (1) above.

---

## Gap Plan (next session picks up here)

1. **Verify what `loan-reviews` actually produces.** Drop one trigger for CUL only over the trailing 12 months, inspect the CSV columns. If it includes disposition + category + amount, it's the master dataset.
2. **Verify aged-inventory-summary columns.** Sample one CSV to confirm it captures category, days-on-shelf, original loan amount, asking price, sold price (if sold).
3. **Build the saved Ad Hoc reports per-store for `fpd-cohort`** (one-time, ~75 min total across 5 stores) — needed for clean FPD attribution.
4. Once the cohort data lands: build the **forfeiture-rate / FPD-rate / true-ROI table by subcategory**.
5. Render the three deliverables.

---

## Files Produced So Far

| File | What it is | Generated |
|---|---|---|
| `Loan_Portfolio_Analysis_2026-05-21.xlsx` | Multi-sheet workbook: cover, per-store KPIs, disposition mix, loan-size×dispo, top customers, category mix, all tickets raw | 2026-05-21 |
| `Loan_Portfolio_Findings_2026-05-21.docx` | Phase 1 written findings memo with executive summary, top findings, recommended next steps | 2026-05-21 |
| `loan_portfolio_dashboard.html` | Live HTML dashboard (Chart.js) — open in browser, reads loan_portfolio_summary.json on each load | 2026-05-21 |
| `loan_portfolio_summary.json` | Machine-readable digest powering the dashboard | 2026-05-21 |
| `loan_portfolio_data.json` | Full ticket + category data for the dashboard | 2026-05-21 |
| **`Valley_Pawn_Loan_Portfolio_Framework.xlsx`** | **7-tab analysis framework — LIVE DATA in Forfeit Risk Snapshot + Executive Summary tabs. Auto-populates when full loan CSV is pasted into Raw Data tab.** | **2026-06-10** |

---

## Session Log

- **2026-06-10 (framework build session)** — Bravo 12-month pull still blocked (Ok button grayed in dialog — same as 2026-05-20). Built `Valley_Pawn_Loan_Portfolio_Framework.xlsx` (28K, saved to project folder) using data already on disk. Zero formula errors (recalc.py verified 21 formulas). **No Slack post — internal analysis only.**

  **Framework workbook tabs:**
  - **Executive Summary** — KPI dashboard with live per-store data (loans 75+ past due, aged inventory cost by category). Prior v2 findings (1,459 tickets, $242K principal) embedded as benchmarks. Blocker/next-step callouts.
  - **By Category** — Skeleton rows for all known categories (Jewelry/Gold/Silver, Tools, Electronics, Firearms, Coins, Knives, Lawn/Outdoor, etc.) with COUNTIFS/AVERAGEIFS formulas pointing to Raw Data tab. Cells show "DATA NEEDED" placeholders until full data is pasted.
  - **By Loan Size** — Buckets ($1–25, $26–50, $51–100, $101–200, $201–500, $501–1K, $1K+) with v2 partial-data ROI findings embedded. Full-data columns ready for paste-in.
  - **FPD Analysis** — Framework by store + by category. Documents that FPD tracking requires payment-count column not yet in the Bravo export; flags categories from v2 as historically high-FPD risk.
  - **Forfeit Inventory** — **LIVE** — Full aged-inventory breakdown by store × category × age bucket (data: 2026-06-08). Total 12mo+ cost flagged as stranded forfeit capital (~$100.5K across all 5 stores). CUL largest ($28.6K), WAY smallest ($11.0K).
  - **Forfeit Risk Snapshot** — **LIVE, ACTIONABLE NOW** — Three-tier risk view: Tier 1 = loans 75+ past due (62 loans, $12,564 at risk; HAR/ROA each have 22 loans, $5–6K); Tier 2 = 6-12mo aged inventory needing markdown ($46.6K combined); Tier 3 = 12mo+ dead stock ($100.5K, 78% est. loss rate based on v2). Summary box shows total capital at risk via SUM formulas.
  - **Raw Data** — Column headers matching expected Bravo output (Ticket Number, Store, Pawn Date, Disposition, Disposition Date, Category, Full Description, Loan Amount, etc.). Category and Full Description columns highlighted gold — they're missing from current Bravo column layout and must be added before the full pull. Smoke test sample rows included as illustration.

  **Data sources used:**
  - `2026-06-08_*_aged-inventory-summary.csv` — all 5 stores
  - `2026-06-08_*_loans-75-days-past-due.csv` — all 5 stores
  - `smoke_*_low-dollar-loans.csv` — all 5 stores (CUL, HAR, LEX, ROA have data; WAY empty)

  **One remaining blocker (pipeline):** `Valley_Pawn_Loan_Portfolio_Framework.xlsx` will auto-populate all formula tabs the moment the full 12-month Bravo loan CSV is pasted into the Raw Data tab. The only thing gating that is the Bravo Ok-button fix — same issue as 2026-05-20. Fix options (unchanged):
  1. Check `IsEnabledPattern` before invoke; Tab into dialog body first to enable the button, then retry.
  2. Use `LegacyIAccessiblePattern.DoDefaultAction` instead of `InvokePattern.Invoke`.
  3. Find Ok by `AutomationId` instead of Name.
  
  **Columns gap still open:** Current Bravo column layout is missing `Category` and `Full Description`. Must add these to the "Claude Loan Portfolio 2026" saved report column layout before running the full 12-month pull (or use "Save Copy" to create a parallel layout).

- **2026-05-25 (weekly scheduled refresh)** — Scheduled task `weekly-loan-portfolio-refresh` (Mondays 7am) fired. Dropped trigger `weekly-loan-portfolio-2026-05-25` covering trailing 12 months (2025-05-25..2026-05-24) for all 5 stores. Pipeline claimed the trigger in seconds and returned `status: partial` with `EnsureStore failed for <STORE>` on every cell (CUL/HAR/LEX/ROA/WAY — same failure mode as 2026-05-20 08:20, likely Bravo not in foreground in the Parallels VM, or an Overdue Task Reminder modal in front). **No new CSVs landed** — pipeline output folder still tops out at 2026-05-21 monthly slices. Analysis script run was **skipped** since there was no new data to incorporate; existing v3 deliverables remain the latest. Pipeline failure flagged in Slack DM to Joshua (channel #optimize-loan-portfolio does not exist). Per Hard Rules #4, did NOT attempt any pipeline fix in this scheduled task — needs a manual session to: (a) bring Bravo to front in the VM, (b) dismiss any modal dialogs, (c) re-drop the trigger. Known issues unchanged: AHK enumerator ~200-row cap, LEX dropdown discovery, CUL & WAY inventory-details gap.

- **2026-05-21 (evening, 5 PM final pass)** — Scheduled `loan-portfolio-final-pass-2026-05-21` ran. Pipeline result file confirms `loan-portfolio-2026-monthly-12mo-2026-05-21T09-30-00` **aborted** at 10:11 — only 13 of 62 cells logged (9 success, 4 error, 49 never ran). v2 analysis re-ran on the partial data + the pre-existing HAR 12-month single-pull + 20-day windows. **Outputs refreshed:** `Loan_Portfolio_Analysis_v2_2026-05-21.xlsx`, `Loan_Portfolio_DecisionDoc_2026-05-21.docx`, `loan_portfolio_v2_summary.json`. Dashboard (`loan_portfolio_dashboard_v2.html`) reads JSON dynamically.

  **Final pass headline numbers (partial data, 1,459 unique tickets, $242,330 principal deployed):**
  - **Per-store true ROI ranking** (best → worst): LEX 14.10% → WAY 10.89% → HAR 7.74% → ROA 7.21% → CUL 4.25%. CUL is the persistent laggard.
  - **Confidence stores:** LEX (260 tickets, 119 completed — strongest sample), ROA (461 tickets, 190 completed — largest sample). CUL & WAY each have only 1 monthly slice → sparser dispositions.
  - **Categories with FULL forfeit (0 redemptions in sample):** Gold/Jewelry (-78.2% on 10 forfeits, $2,076 deployed → $452 realized), Electronics (-78.6% on 3 forfeits), Lawn/Outdoor (-43.0%), Tools (-25.4%), Other (-21.4%). Firearms shows +323.7% but only n=3.
  - **Loan-size sweet spots:** $25–$50 bucket = 19.4% ROI (197 tickets). Under-$25 = 17.9% (83 tickets). $50–$100 = 13.1% (315 tickets). **The small-ticket book is the profit engine.**
  - **Loan-size DANGER zone:** $1000+ bucket = 0.0% ROI on 15 tickets / $27,230 deployed — every big loan in the sample is still open or forfeited without resale recovery.

  **Coverage gaps to note:** CUL & WAY have only 1 successful monthly slice (May 21–Jun 20). HAR has 1 monthly slice + the prior 12-month single-pull (173 rows). LEX & ROA have 2–3 monthly slices. Cells from Jun 21 onward for most stores never ran (pipeline aborted). Recommended: re-trigger the failed cells before treating per-category numbers as definitive — current cat counts (n=2–10) are directional, not statistically tight.

- **2026-05-21 (afternoon)** — Phase 2 v2 deliverables and monthly-sliced pipeline run kicked off. After Joshua called out Phase 1 as incomplete/unactionable, switched strategy: dropped 62-cell trigger (12 months × 5 stores × monthly windows + missing CUL/WAY inventory pulls). LEX now SUCCEEDS on monthly slices (smaller row counts let the dropdown render in time — no AHK fix needed for monthly use). Built proper true-ROI analysis: realized interest on REDEEMED + realized resale margin on FORFEITED (cross-referenced via inventory.Number prefix-match to loan ticket base — fixed the 2/32 match rate to 12/32+ on partial data). New v2 deliverables: `Loan_Portfolio_Analysis_v2_*.xlsx` (with Sweet-spot/Stop-lending rec sheets), `Loan_Portfolio_DecisionDoc_*.docx` (per-store action plan + per-category lend/no-lend recommendations), `loan_portfolio_dashboard_v2.html` (decision dashboard with true ROI focus). Scheduled `loan-portfolio-final-pass-2026-05-21` to fire at 5 PM for final-data refresh once all 62 cells land.

  **PRELIMINARY HEADLINE FINDINGS (partial data, 9 of 62 cells in):**
  - True-ROI ranking INVERTS the Phase 1 redemption-rate picture. LEX is best (14.10% true ROI), CUL is worst (4.25%). CUL's high avg loan ($254) means each forfeit is a big loss — the redemption advantage is wiped out by forfeit-resale losses.
  - **Gold/Jewelry forfeits lose ~78% of principal on resale** (10 forfeits, $2,076 deployed → $452 realized). Either tighten LTV dramatically OR set a minimum LTV-to-melt-value floor. Confirm with full data.
  - Electronics: similar -78.6% on forfeit. Forfeit Electronics is essentially worthless on resale.
  - Firearms: +323% ROI but only 3-sample — wait for more data.

- **2026-05-21 (morning)** — Phase 1 deliverables landed. Widened saved Bravo report date range to 5/1/2025–12/31/2026 (via date picker — typing breaks the mask, lesson saved to memory). Dropped 12-month × 5-store trigger (`loan-portfolio-2026-12mo-2026-05-21T08-45-00`). Result: PARTIAL — only HAR succeeded with 173 rows (truncated by AHK enumerator). CUL/WAY: WriteBuysGridToCsv -1. LEX: dropdown discovery failure. ROA: EnsureStore failed mid-run. Built deliverables on combined dataset: 20-day window (4 stores, 967 rows) + HAR 12-month partial (173 rows) + inventory-details 12 months (HAR/LEX/ROA, ~10k items with Category) + aged-inventory snapshots. Headline finding: **Harrisonburg is the underwriting outlier** — 71% redemption vs. 83–86% elsewhere, 15% forfeit vs. 5–13%. Created weekly scheduled task `weekly-loan-portfolio-refresh` (Mondays 7am). New pipeline tasks opened: fix AHK enumerator pagination cap, fix LEX-specific dropdown discovery.

- **2026-05-20** — Project kicked off. Pipeline chosen as data source. Memory/skill rules added to enforce "check prior work first" pattern + "additive only" pattern (Rule #4). Built Valley Pawn Business OS master map at `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/BUSINESS_OS.md`.

### Additive infrastructure added today (all confirmed clean diffs, backups left)

1. **New AHK handler:** `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/reports/LoanPortfolio2026.ahk` (cloned from `LoanReviews.ahk`, function `PullLoanPortfolio2026`, saved-report value `Claude Loan Portfolio 2026`, output suffix `loan-portfolio-2026`).
2. **New pipeline cell registered in `bravo_watcher.ahk`:** `REPORT_HANDLERS["loan-portfolio-2026"] := PullLoanPortfolio2026` (added as line 102, no existing rows modified). Include line added: `#Include reports\LoanPortfolio2026.ahk`.
3. **New entry in `config.json`:** `"loan-portfolio-2026": "reports\\LoanPortfolio2026.ahk"` (only existing change was a trailing-comma added to the prior last entry — JSON syntactic requirement, not semantic).
4. **New saved Ad Hoc report in Bravo:** "Claude Loan Portfolio 2026", Shared Company-Wide, Ticket Kind=LOAN, Create Date range (handler overrides at runtime), column layout "High Dollar Loan Demographic", Initial Rows 1000 (may bump to 5000 later), Sort by Age.
5. **Watcher restarted** at 09:09:59 — confirmed handler list now includes `loan-portfolio-2026`.

### Known issue, fixed but not yet validated

The 09:11 probe ran end-to-end but the grid never rendered → 0-row sentinel CSV written. Same failure mode as the prior `loan-reviews` probe earlier today. Root cause: `Send("{Enter}")` after Update is not reliably triggering Bravo's `Ok` button — same issue plagues both handlers.

**Fix (additive only, applied to `LoanPortfolio2026.ahk` only — `LoanReviews.ahk` untouched per Rule #4):** changed Step 6 from `Send("{Enter}")` to `ClickByName("Ok", 5000)` with Enter as fallback. Backup `LoanPortfolio2026.ahk.bak-pre-okclick-2026-05-20` left in place.

### Resume next session

1. Restart watcher (`restart_watcher.bat` in VM) — picks up the Ok-click patch.
2. Drop a fresh CUL April 2026 probe trigger for `loan-portfolio-2026`.
3. If probe returns >0 rows with the expected columns (Ticket #, Pawn Date, Disposition, Disposition Date, Category, Full Description, Loan Amount), proceed to the 12-month × 5-store extract.
4. If grid still won't render, switch to a more robust dialog-driving approach (find the Ok button by `AutomationId` instead of Name, or programmatically trigger the saved-report's Run action).

### Probe #3 result (2026-05-20 09:41) — **PIPELINE END-TO-END WORKS** ✅

- Handler patched to match FpdCohort.ahk pattern (no runtime date override, just select → Ok → grid).
- Watcher restarted at 09:38:53.
- Probe `loan-portfolio-2026-probe3-CUL-2026-05-20T14-40-00` ran successfully.
- **244 rows written** to `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/2026-04-01_to_2026-04-30_CUL_loan-portfolio-2026.csv`
- Header: `Ticket Number,Disposition,Disposition Date,Due Date,Pull Date,Customer,Loan Amount,Age,MobilePawn,SMS,Address`
- Sample rows show real loan data (REDEEMED disposition, $5–$100 loan amounts, May 2026 dates).
- Saved-report Create Date range is currently **5/1/2026 → 5/20/2026** (only ~3 weeks). Needs to be widened to **5/1/2025 → 12/31/2026** for the full 12-month analysis.

### 5-store extraction running (2026-05-20 09:53)

Trigger `loan-portfolio-2026-5store-2026-05-20T15-00-00` dropped covering all 5 stores. Handler is the proven FPD-style flow (uses saved report's static 5/1-5/20/2026 Create Date range; runtime override is patched in `LoanPortfolio2026.ahk.bak-pre-dateoverride-v2-*` but not loaded — needs watcher restart). Expected: ~1200 rows across all 5 stores in ~15 min.

Outputs land at `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/2026-05-01_to_2026-05-20_<STORE>_loan-portfolio-2026.csv`.

### Sustainability fix for next session (Joshua's priority)

Runtime date override needs to work programmatically so we don't have to manually widen the saved report's date range for every analysis window. The patch is on disk:
1. Restart watcher to load the patched `LoanPortfolio2026.ahk` (with SetReportDate + Update + 4-second wait + ClickByName Ok)
2. Probe CUL with a different date range (e.g., 2026-03-01..2026-03-31) to verify the override takes effect
3. If grid renders >0 rows for the OVERRIDDEN range (not the saved 5/1-5/20), date override works → ready for arbitrary date ranges per trigger
4. If grid still doesn't render, fall back: keep saved-report dates wide (5/1/2025 → 12/31/2026), handler stays FPD-style with no override, post-filter at analysis time

### Columns gap

The current column layout "High Dollar Loan Demographic" gives us 11 columns but is missing:
- **Category** — needed for ROI-by-collateral-category analysis (the project's primary goal)
- **Full Description** — needed for subcategory analysis

For the initial 12-month pull we can proceed without Category and do customer/disposition/amount analysis. Add Category in a follow-up by editing the column layout (or use "Save Copy" to create a new "Claude Loan Portfolio Columns" layout that includes Category + Full Description).

### Probe #2 result (2026-05-20 09:22)

- Watcher restarted at 09:18:53 with patched handler (ClickByName Ok).
- Probe trigger `loan-portfolio-2026-probe2-CUL-2026-05-20T14-20-00` ran successfully end-to-end.
- Log confirms: selected `Claude Loan Portfolio 2026`, set dates to 4/1–4/30/2026, clicked Update, clicked Ok via UIA.
- BUT: still 0-row sentinel CSV. **Root cause identified visually**: dialog screenshot during the run shows the `Ok` button is GRAYED/DISABLED. UIA `InvokePattern.Invoke()` fires on the disabled control but it's a no-op. The watcher's "[UIA] clicked Ok" log is accurate ("clicked the button" in UIA terms) but the button doesn't respond when disabled.
- This is a real, narrowly-scoped final blocker. Three candidate fixes for the next session:
  1. Check `IsEnabledPattern` before clicking; if disabled, focus the dialog first (Tab into the body) and retry.
  2. Try a different UIA pattern (e.g., `LegacyIAccessiblePattern.DoDefaultAction`) instead of InvokePattern.
  3. Find the Ok button by AutomationId (not Name) — there may be a hidden but enabled "Run" action element distinct from the visible "Ok".
  4. Diagnostic: keep the dialog open, screenshot the Ok button's UIA properties via the `uia-discover` handler to see why it's disabled.

### Original probe history (resolved by the additive approach above)
- **2026-05-20** — Dropped probe trigger `loan-reviews-probe-CUL-2026-05-20T13-00-00` for CUL Apr 2026. Watcher returned `Unknown report name: loan-reviews`. **Root cause:** AHK watcher in Parallels VM was last restarted 2026-05-19 18:45, but the `loan-reviews` handler was registered AFTER that restart (backup `bravo_watcher.ahk.bak-pre-loan-reviews-2026-05-19` confirms). Yesterday's 22:04 smoke test failed the same way. **Blocker:** need to restart `bravo_watcher.ahk` inside the VM by running `Y:\Documents\Claude\Projects\Bravo Data Extraction\restart_watcher.bat`. Once restarted, re-drop the probe trigger.
- **2026-05-20 08:19** — Watcher restarted (build tag `claim-fix-2026-05-13`, 18 handlers registered including `loan-reviews`).
- **2026-05-20 08:20** — Re-dropped probe `T13-30-00`. Failed with `EnsureStore failed for CUL` — File Explorer window was the foreground app, blocking watcher's UIA access to Bravo.
- **2026-05-20 08:21** — Brought Bravo to front, dismissed Overdue Task Reminder modal.
- **2026-05-20 08:22** — Re-dropped probe `T13-45-00`. Watcher progressed through saved-report selection and date override but the criteria visible in the dialog reveal that **"Claude Loan Reviews" saved report has WRONG criteria** for portfolio-wide analysis:
  - Ticket Kind = BUY (should be PAWN/LOAN for our purposes)
  - Loan Amount range $1.00–$5.00 (should be unconstrained)
  - Disposition Date range 5/1/2026–5/14/2026 (handler tried to override to 4/1–4/30 but the visible field didn't update; possibly handler is targeting the wrong date wrappers — log claimed wrappers at x=885 and x=1159 but only two date fields are visible in the dialog at roughly x=555 and x=652)
  - **Implication:** the saved report is essentially a clone of "Claude Low Dollar Loans" with no portfolio-wide loan-cohort criteria. Need to rebuild or replace it.

### Next decisions to make (SUPERSEDED — we went additive instead, see below)
- **2026-05-20 08:25** — Probe `T13-45-00` returned `status: success, row_count: 0` after 175s. Output CSV header confirmed: `Ticket Number, Category, Full Description, Loan Amount`. **Two gaps confirmed:** (1) wrong filter criteria → empty result; (2) display columns missing the dispositon/date fields needed for portfolio analysis. Pipeline plumbing is otherwise fully working.

### Required state of "Claude Loan Reviews" saved report for portfolio analysis
**Criteria (filter the dataset):**
- Active Loans and Buys: unchecked (so we get redeemed/forfeited history, not just currently active)
- Ticket Kind = LOAN (not BUY)
- Date filter: Pawn Date range (Bravo's term for origination date), overridable per-run by the handler. Or no date constraint and rely on handler-set Disposition Date.
- Initial Rows = 5000+ (CUL alone could have 1500–3000 loans in 12 months)
- Sort By Pawn Date, ascending

**Display columns (the CSV will export):**
- Ticket Number
- Pawn Date (origination)
- Disposition (REDEEMED / FORFEITED / ON LOAN / VOIDED / etc.)
- Disposition Date
- Category
- Full Description
- Loan Amount
- Customer name (optional — we said no customer segmentation, but it's useful for de-duplication)
