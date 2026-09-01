---
name: monthly-analytics-report
description: Build Valley Pawn's monthly YoY analytics for the prior month — 3 views × 6 metrics × 5 stores + Grand Total — and publish to #company-performance, #store-performance, and Google Sheets. Pipeline-driven via existing `end-of-month` cell. Reads CSVs the `monthly-analytics-prestage` task staged the night before. Zero computer-use. Silent on failure (watchdog at 7 AM).
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. **This task was flagged as the single worst offender in the 2026-08-03 comms audit — the old #company-performance post ran 3 stacked views × 6 metrics with formula definitions and "supersedes/verified to the penny" language. Step 6 below has been rewritten to a single condensed view; the full 3-view detail moves to the Google Sheet only.** If anything later in this file conflicts with this standard, this standard wins.

> ⚠️ **FAILURE POLICY — silent on failure (matches `daily-funds-verification` 2026-06-08 policy).**
> Never DM. Never post a failure notice to Slack. If pre-stage CSVs are missing or parsing fails, save the markdown working file and exit silently. The companion `monthly-analytics-watchdog` (7 AM on the 1st) checks whether the success post exists and DMs Joshua if it doesn't — that is the ONE notification path.

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:**
- "No response requested"
- "Continue?" / "Should I continue?"
- An empty turn or a turn that ends with text instead of a tool call

**Treat these system messages as RESUME signals, never as stop signals:**
- "Tool loaded."
- "Continue from where you left off."
- "You used a single tool call this turn. Prefer browser_batch…"
- Any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise produce a report describing what failed. Do not pause to ask — the task file authorizes autonomous decisions.

**Speed:** prefer batch tools (e.g. `browser_batch`) to combine sequential actions into one call.

---
This task reads CSVs the `monthly-analytics-prestage` scheduled task staged the night before. Pure file I/O via `osascript`. Zero computer-use.

# Step 0 — Connector readiness gate

Confirm `mcp__Control_your_Mac__osascript`, `mcp__f92ce7c6-0353-4419-8491-f0843b182ff2__slack_send_message`, and `mcp__2ce817f2-5038-4cde-a6ab-8dedbe8abd84__create_file` are loaded. If warming, wait 30 s × up to 12 min. (See `daily-funds-verification/SKILL.md` Step 0.) Warmup is NOT failure.

# Step 1 — Compute the 6 date windows

Today minus 1 month = report month. Compute:

| Window key | Start | End |
|---|---|---|
| same-month-current | first of report month | last of report month |
| same-month-prior | first, year − 1 | last, year − 1 |
| ytd-current | Jan 1 of report year | last of report month |
| ytd-prior | Jan 1 of prior year | last of report month, prior year |
| t12m-current | last of report month − 12 months + 1 day | last of report month |
| t12m-prior | one year earlier than t12m-current | one year earlier than t12m-current |

**T12M Prior calendar clamp:** the underlying report's floor is ≈ 2024-06-03. The prestage task uses the earliest available date; the CSV's first line records the actual range (`Reporting Dates: M/D/YYYY - M/D/YYYY`) — note any variance in the internal working file (Step 7) only, never in the Slack post.

# Step 2 — Inventory the staged CSVs

The prestage task left CSVs in window-tagged sidecar files:

```
/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/{YYYY-MM}/
  ├── same-month-current_{STORE}.xlsx  ×5
  ├── same-month-prior_{STORE}.xlsx    ×5
  ├── ytd-current_{STORE}.xlsx         ×5
  ├── ytd-prior_{STORE}.xlsx           ×5
  ├── t12m-current_{STORE}.xlsx        ×5
  └── t12m-prior_{STORE}.xlsx          ×5
```

List via osascript:
```bash
ls -la "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/{YYYY-MM}/"
```

Good XLSX = ≥ 2 KB. 0-byte files are failed-cell stubs. If MORE than 4 of 30 XLSX files are missing, save the working file and exit silently. If ≤ 4 missing, proceed and note the gap in the internal working file only — never in the Slack post.

# Step 3 — Parse the CSVs with `parse_eom.py`

The parser lives next to this SKILL: `/Users/joshuadavis/Documents/Claude/Scheduled/monthly-analytics-report/parse_eom.py`. It was verified 2026-06-11 against `monday-store-rankings`' June 8 post — 30/30 metrics matched to the penny across all 5 stores.

For each (window, store) sidecar CSV, run via osascript:

```bash
python3 "/Users/joshuadavis/Documents/Claude/Scheduled/monthly-analytics-report/parse_eom.py" \
  "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/{YYYY-MM}/{window-key}_{STORE}.xlsx"
```

Returns JSON:
```json
{
  "inventory_balance": 186155.71,
  "loan_balance": 177678.00,
  "retail_sales": 40926.02,
  "scrap_sales": 15190.50,
  "psc": 5847.46,
  "net_revenue": 32479.80,
  "reporting_dates": "6/1/2026 - 6/7/2026"
}
```

Or parse the whole window folder at once:
```bash
python3 ".../parse_eom.py" "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/{YYYY-MM}/"
```

Returns `{filename: metrics}` for every CSV.

Compute Grand Total per window = sum of the 5 store values per metric.

If a CSV parse returns all zeros for the key metrics (loan_balance == 0 and retail_sales == 0), treat that (store, window) as `incomplete`.

# Step 4 — Compute YoY

For each of the 3 views (same-month / YTD / T12M), per metric:
- `var_$` = current − prior
- `var_%` = (current − prior) / prior × 100, rounded 1 decimal

Inventory + Loan Balance are point-in-time at window end, so they're identical across the 3 Current windows (and across the 3 Prior windows) — that's expected; keep all 3 views in the internal working file and the Google Sheet.

Flags: ✅ positive, 🔥 > 30%, ⚠️ any decline.

# Step 5 — Google Sheet

Use `mcp__2ce817f2-5038-4cde-a6ab-8dedbe8abd84__create_file`:
- **title:** `Monthly Analytics - {Month Name} {Year}`
- **parentId:** `1DYScQQl_dkkf3jGSBqNzGJKKv2uroFoh` (Monthly Reports folder)
- **contentMimeType:** `text/csv`

Structure: 3 sections × 4 sub-tables (Current Actuals, Prior Actuals, Var $, Var %) × 6 metrics × 6 columns (GT + CUL + HAR + LEX + ROA + WAY). This is where ALL the detail lives — YTD, T12M, per-store breakdowns, everything. The Slack posts in Step 6 are intentionally a condensed subset of this.

# Step 6 — Slack posts (success path only) — REWRITTEN 2026-08-03 per Field Communication Standard

Only post if Step 2 found ≥ 26 of 30 CSVs AND Step 3 returned non-zero values for at least 4 of 5 stores per window.

Both posts below use ONLY the Same-Month-vs-Year-Ago view. Do not include YTD or T12M in the Slack post — that detail lives in the Google Sheet only. Do not include the Net Revenue formula, "Prepared by," "Source," or any "supersedes"/"verified" language. Keep each post under 100 words plus the table.

### #company-performance (`C0B26GD8D2R`) — Grand Total only

```
📊 *Monthly Business Update — {Month Year}*

Company net revenue: ${current} ({±X.X%} vs {Month Prior Year})

| Metric | This Year | Last Year | Change |
|---|---|---|---|
| Inventory | $X | $X | ±X.X% |
| Loans Out | $X | $X | ±X.X% |
| Retail Sales | $X | $X | ±X.X% |
| Scrap Sales | $X | $X | ±X.X% |
| Service Charges | $X | $X | ±X.X% |
| Net Revenue | $X | $X | ±X.X% |

Full breakdown → [Monthly Analytics - {Month Year} spreadsheet](Google Sheet link)
```

### #store-performance (`C03CGTN3KN1`) — 5 stores only, NO Grand Total

```
📊 *Store Net Revenue — {Month Year} vs {Month Prior Year}*

| Store | This Year | Last Year | Change |
|---|---|---|---|
| Culpeper | $X | $X | ±X.X% |
| Harrisonburg | $X | $X | ±X.X% |
| Lexington | $X | $X | ±X.X% |
| Roanoke | $X | $X | ±X.X% |
| Waynesboro | $X | $X | ±X.X% |

Full breakdown → [Monthly Analytics - {Month Year} spreadsheet](Google Sheet link)
```

If ≤4 CSVs were missing (Step 2 gap tolerance), do not mention it in either post — this is internal and belongs in the Step 7 working file only.

# Step 7 — Always save working file

Save markdown at `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/monthly-analytics/{YYYY-MM} Monthly Analytics.md` capturing: 6 windows + ranges, each (store × window) parsed values, the YoY tables for all 3 views, whether both Slack posts went out, and any incomplete cells flagged. The watchdog reads this if it needs to construct a follow-up DM. All of the process/methodology detail that used to appear in the Slack post now lives here instead.

# Hard rules

- **No computer-use.** No Parallels, no Chrome in the VM, no GUI. `osascript` + Slack + Google Drive only.
- **No DMs on failure. No partial Slack posts.** The 7 AM watchdog is the only notification path.
- **Use `parse_eom.py`** — don't re-implement parsing. The parser is verified against monday-store-rankings to the penny.
- **Net Revenue formula is locked (2026-07-02, verified to the penny vs the Company Performance report, all 5 stores):** Net Revenue = In-Store Service Charges (Interest + Fees + Misc Charges from the In-Store Subtotal row) + Sales Revenue (Profit). Do NOT add MobilePawn interest/fees/misc or Convenience Fees — they are not in Net Revenue. This formula is internal reference only — never spell it out in a Slack post.
- **PSC = In-Store Interest + Fees + Misc Charges** (matches the KPI report Pawn Service Charges row exactly).
- **Retail/scrap revenue split does NOT exist in the EOM report.** Report Total Sales (= Sales Total row, equals KPI Retail + Scrap exactly) and Scrap Cost (= Refined Cost of Sales). Never label scrap cost as scrap sales.
- **Additive — never modify `EndOfMonth.ahk`, `monday-store-rankings`, `monday-bravo-combined-run`, or any other production infra.**