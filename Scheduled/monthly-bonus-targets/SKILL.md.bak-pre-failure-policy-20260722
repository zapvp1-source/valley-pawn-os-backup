---
name: monthly-bonus-targets
description: Generate next month's store revenue bonus targets for Valley Pawn using Option B yield methodology, update the VP BONUS FINAL spreadsheet, and draft a Slack message for Joshua's review.
model: claude-opus-4-8
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are generating next month's store revenue bonus targets for Full Circle Finance Inc DBA Valley Pawn using the Option B yield methodology. Run this at the end of each calendar month, or on demand when Joshua asks.

## Context
- Company: Full Circle Finance Inc DBA Valley Pawn
- Stores: Culpeper, Harrisonburg, Roanoke, Lexington, Waynesboro
- Tracking spreadsheet: Look for "VP BONUS FINAL Updated.xlsx" / "VP BONUS FINAL*.xlsx" / "VP_BONUS_FINAL_rebuilt.xlsx" in the "Claude 4 back up" mounted folder (typically at a path like /sessions/<session>/mnt/Claude 4 back up/). The rebuilt version has a new row layout — see Step 3 below.
- Slack channel for bonus goals: #bonus-goals (channel ID: C04TXF0KGNL)
- Bravo KPI data: Accessed via Chrome in Parallels on Joshua's Mac
- Read the bravo-context skill for Bravo navigation guidance if needed

## Standing fact — data source of truth (confirmed 2026-07-16)
**Never use QuickBooks/QBO as a source of truth for any KPI or revenue figure in this task.** Bravo and Bravo-extracted data (Company Performance / KPI reports, End-of-Month reports, Store Rankings exports) are the only source of truth for revenue and every other business KPI used here.

## CRITICAL — "Net Revenue" definition (corrected 2026-07-16, read carefully)
Column D ("2026 Revenue Actual") must be Bravo's **Net Revenue** KPI, and nothing else. This was found to be the root cause of a real data-quality bug: multiple months of column D had been populated with a broader, WRONG figure (apparently "Retail Sales Total Amt" and/or "Retail Sales + Pawn Service Charges," i.e. gross figures, not gross-profit-based Net Revenue) — these ran $5,000–$30,000+ higher per store per month than true Net Revenue, silently breaking every Bridge 1 (target-hit) determination downstream.

**The exact, verified formula:** `Net Revenue = Pawn Service Charges (interest & fees, MTD) + Retail Sales Gross Profit Amt (MTD) + Scrap Sales Gross Profit Amt (MTD)`. This was confirmed 2026-07-16 by matching it to Preston Peters' actual June 2026 commission-basis figures to the penny (Culpeper $66,649.27, Harrisonburg $61,666.31, Roanoke $36,906.77, Waynesboro $43,416.44, Lexington $21,455.49).

On the Bravo Company Performance / KPI report, there is a line literally labeled **"Net Revenue MTD"** (also appears as "Net Revenue" on Store Rankings exports) — always pull that exact line. Do NOT pull "Retail Sales Total Amt," "Retail Sales (Taxable)," or any combination you compute yourself from gross sales figures — the report already computes Net Revenue for you; find that line and use it verbatim. If you can't find a line literally labeled "Net Revenue" on the report you're looking at, stop and flag it rather than approximating from other fields.

## The Option B Methodology

Revenue target for store S in month M+1:

  Target(S, M+1) = EndingAssets(S, M) × AdjustedYield(S, M+1)
  AdjustedYield = YTD_AvgYield(S) × FridayMultiplier
  MonthlyYield(S, month) = Revenue(S, month) / EndingAssets(S, prior month)
  YTD_AvgYield = average of all monthly yields for each store in 2026 with actuals
  FridayMultiplier = 1 + 0.045 × (Fridays_in_target_month − YTD_avg_Fridays_per_month)

The Friday multiplier should not fall below 1.0 — if it would, hold it at 1.0 and flag this for Joshua. "Revenue(S, month)" here means Net Revenue as defined above — the whole target methodology is self-consistent as long as every Revenue input is Net Revenue, never a gross figure.

Ending Assets = Loan Balance + Inventory Balance (from Bravo KPI report — NOT a separate assets field).

## Steps

### 1. Determine months
- Completed month = the calendar month that just ended
- Target month = the next calendar month (M+1)
- Confirm if there's any ambiguity about which month is closing

### 2. Pull Bravo KPI Report
Use computer-use tools (Parallels → Chrome) to open Bravo and navigate to the Company Performance / KPI Report for the completed month. Read the bravo-context skill first if you need navigation help. If the report is already visible on screen, scrape it visually.

Extract for EACH store:
- **Net Revenue MTD** for the completed month (the literal report line — see the CRITICAL section above, do not substitute a gross-sales figure)
- Loan Balance (ending, last day of completed month)
- Inventory Balance (ending, last day of completed month)
- Ending Assets = Loan Balance + Inventory Balance

### 3. Load YTD data from spreadsheet
Open the tracking spreadsheet using openpyxl. Read the "2025 compared to Bonus" sheet.

Spreadsheet layout (rebuilt 2026-07-16 — row numbers changed from the pre-rebuild version, confirm against the actual file before writing):
- Culpeper: title row 3, header row 4, data rows 5-16 (Jan-Dec), Total row 17
- Harrisonburg: title row 19, header row 20, data rows 21-32, Total row 33
- Roanoke: title row 35, header row 36, data rows 37-48, Total row 49
- Lexington: title row 51, header row 52, data rows 53-64, Total row 65
- Waynesboro: title row 67, header row 68, data rows 69-80, Total row 81
- Company-wide summary: title row 83, header row 84, data rows 85-96, Total row 97
- Preston Peters Market Manager section: title row 99, header row 100, data rows 101-112, Total row 113
- "Employees by Store" is now a SEPARATE TAB, not part of this sheet.
If the file you open doesn't match this layout (e.g. it's the pre-rebuild original), locate the header row containing "Month" for each store block dynamically rather than assuming fixed row numbers — don't silently write to the wrong row.

Column mapping (A=1 through K=11):
- A: Month name
- B: 2025 Revenue (prior year)
- C: 2026 Bonus Target
- D: 2026 Revenue Actual — **must be Net Revenue, see CRITICAL section**
- E: Variance (D - C) — formula, don't overwrite
- F: Ending Assets Target
- G: Actual Ending Assets
- H: Yield (D / prior month G) — formula, don't overwrite
- I: Cumulative Variance ($) — formula, don't overwrite
- J: YoY Rev Var ($) — formula, don't overwrite
- K: Bonus Payout (Two-Bridge) — formula, don't overwrite; this implements Bridge 1 (D>=C, hard gate) and Bridge 2 (D>=B, rate selector) automatically

Read D, G, H for all months with actuals to rebuild the YTD yield series for each store.
If H is blank but D and G are present, compute yield = D_value / prior_month_G_value.

### 4. Calculate YTD average yields
Average the monthly yields for each store across all months with actual revenue (col D non-empty) in 2026.

### 5. Count Fridays and compute multiplier
Count exact Fridays in the target month (M+1).
Count average Fridays per month across the YTD period (Jan through completed month).
Apply: FridayMultiplier = 1 + 0.045 × (TargetFridays − YTD_AvgFridays)
Round multiplier to 4 decimal places for intermediate calc; present to 2 decimal places.

### 6. Calculate targets
For each store: Target = EndingAssets(completed month) × YTD_AvgYield × FridayMultiplier
Round to nearest whole dollar.
Company total = sum of all five store targets.

Show a summary table with: Store | Ending Assets | YTD Yield | Friday Mult | Target

### 7. Update the spreadsheet

Use openpyxl to update the file. IMPORTANT: be careful with merged cells — use a try/except around each cell write to skip merged non-primary cells gracefully. Never overwrite formula cells (columns E, H, I, J, K — these recalculate automatically; also never overwrite the Company block's SUM-based cells or the Preston section).

For the COMPLETED month row in each store block:
- Column D: actual Net Revenue from Bravo (see CRITICAL section — verify this is the "Net Revenue MTD" line, not a gross-sales figure)
- Column G: actual ending assets from Bravo
- (Columns E, H, I, J, K recompute themselves via formula — do not write to them)

For the TARGET month row in each store block:
- Column C: the new bonus target
- Column F: ending assets assumption (= prior month actual G value)

After writing D/G values, also update the Company-wide summary block's D column for that month (it's a SUM formula referencing the 5 stores in the rebuilt file — confirm it recalculates rather than overwriting it with a literal).

Write mode: load with data_only=False, preserve existing formulas, write updated values, save back. Then run the file through LibreOffice (`recalc.py`, or a direct `soffice --headless --convert-to xlsx` round-trip if recalc.py times out) so cached formula values are refreshed — an openpyxl save alone leaves formula cells blank to anything that reads cached values.
Save to the same path as the source file. chmod 0o644 after saving.

### 8. Draft Slack message — DO NOT SEND

Compose a message for #bonus-goals using EXACTLY this format and structure (this is Joshua's approved template):

```
📅 [Month] [Year] Bonus Targets
[Month] is a [N]-Friday month — our [period] average is [X] Fridays/month, so every store's target already has a +[X]% calendar lift baked in.

May Targets by Store
🏪 Culpeper — $XX,XXX
🏪 Harrisonburg — $XX,XXX
🏪 Roanoke — $XX,XXX
🏪 Lexington — $XX,XXX
🏪 Waynesboro — $XX,XXX

How We Got Here.
-Targets are built using each store's own 2026 YTD yield — not a company average. Formula: [prior month] ending assets × store's YTD yield × Friday multiplier.
-[Prior Month] Ending Assets (Loans + Inventory):
Culpeper $XXX,XXX · Harrisonburg $XXX,XXX · Roanoke $XXX,XXX · Lexington $XXX,XXX · Waynesboro $XXX,XXX
-YTD Avg Yield (Jan–[Prior Month] [Year]): Culpeper XX.X% · Harrisonburg XX.X% · Roanoke XX.X% · Lexington XX.X% · Waynesboro XX.X%
-Friday adjustment: [Month] has [N] Fridays vs. a [X] monthly average. At +4.5% per extra Friday, that's a [X.XXX]× multiplier on every store's baseline.
Each store's number reflects what they've actually been doing this year. Hit it and earn it. This not math anymore, it's science. Let's have a great [Month]. 💪
```

Formatting rules — follow these exactly:
- Each store target is on its own line — never run stores together on one line
- Ending assets: each store on its own line inside the bullet, not comma-separated inline
- "How We Got Here." section uses dash bullets (-), not markdown bullets or bold
- No markdown bold/italic — Slack renders plain text
- No company total line in the targets section
- The sign-off line is fixed every month: "Each store's number reflects what they've actually been doing this year. Hit it and earn it. This not math anymore, it's science. Let's have a great [Month]. 💪"

Present the full draft to Joshua in chat. Ask him to confirm before sending. NEVER auto-send.
Use Slack MCP tool slack_send_message (channel C04TXF0KGNL) ONLY after Joshua explicitly says "send it" or "looks good, send."

### 9. Deliver summary to Joshua

Present:
1. Per-store target table (from Step 6)
2. Confirmation that spreadsheet was updated with actuals (Net Revenue, not gross) + new targets
3. The Slack draft for his review
4. File link to the updated spreadsheet

## Important Notes
- Yield in the formula is a ratio (e.g., 0.186 for 18.6%) — confirm units from spreadsheet before multiplying
- Ending Assets must come from Bravo (Loan Balance + Inventory Balance), not estimated
- Column D must always be Bravo's "Net Revenue MTD" line — never a gross-sales figure, never QBO
- Never auto-send the Slack message — always wait for Joshua's explicit approval
- If Bravo KPI data for the completed month is not yet available, note this and ask when to rerun

<!-- migrated to working model 2026-06-15 -->
<!-- corrected Net Revenue sourcing + rebuilt-file row layout 2026-07-16 -->