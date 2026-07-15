---
name: sales-tax-monthly-update
description: Monthly Valley Pawn sales tax data refresh — reuses the per-store GL CSVs that eom-bravo-gl-export (day 5) now proactively pulls, falls back to pulling them itself if missing, and populates Sales Tax.xlsx (Taxable Sales / Ebay / Taxes Due format)
---

You are updating Full Circle Finance Inc DBA Valley Pawn's monthly sales tax workbook. Act as a forensic accountant — precise, source-cited, and willing to flag anomalies rather than paper over them.

GOAL: populate the row for LAST CALENDAR MONTH (relative to today) in the workbook at:
/Users/joshuadavis/Documents/Claude/Projects/Sales Tax/Sales Tax.xlsx (Sheet1)

BACKGROUND / CONTEXT — read first
- Read the `valley-pawn-context` and `bravo-context` skills for company/store details and Bravo operating procedure before doing anything.
- As of 2026-07-08 the workbook layout is: cell G1 holds the VA sales tax rate assumption (currently 5.3% = 4.3% state + 1.0% local — this is the standard rate and applies to all 5 stores, none of which are in a special regional-tax zone; verify this is still current if it's been a long time since last checked). Row 3 has store names merged across 3 columns each; row 4 has column headers "Taxable Sales" | "Ebay" | "Taxes Due" repeated per store. Data starts at row 5, ONE row per month (no more two-row-per-month structure — that was removed 2026-07-08 along with the old Non-Taxable and Total columns).
- Store column starts: Culpeper C (Taxable=C, Ebay=D, Taxes Due=E), Harrisonburg F (F,G,H), Lexington I (I,J,K), Roanoke L (L,M,N), Waynesboro O (O,P,Q).
- Column A has month labels already typed in sequence (SEP, OCT, NOV, DEC, JAN, FEB, MAR, APRIL, MAY, JUNE, JULY, AUG, SEP, OCT, NOV, DEC — running Sep 2025 through Dec 2026 as of 2026-07-08). Find the row whose column-A label matches last month's name in the correct calendar position. If last month's row doesn't exist yet (workbook wasn't extended that far), add a new row directly below the last row in use with the month label in column A, matching the same formatting/formulas as the row above it. Do not restructure or overwrite any other row.

PIPELINE DEPENDENCY (added 2026-07-14) — read before Step 1
This task now runs the 6th of the month, one day after `eom-bravo-gl-export` (runs the 5th). That task cycles all 5 Bravo stores to verify/post the prior month's accounting, then — as its own Step 5.5 — proactively drops a trigger for the same `post-to-accounting-gl` pipeline cell this task needs, specifically so this task does NOT have to drive Bravo itself under normal conditions. By the time this task runs the next morning, the per-store CSVs should already be sitting in the output folder. Step 1 below still checks for and falls back to pulling them itself — this is a safety net for when `eom-bravo-gl-export` didn't run, failed, or got rescheduled (it self-delays when Bravo is busy), not the expected normal path. If you do end up needing the fallback, use the same concurrency guard `eom-bravo-gl-export` uses so you don't collide with it or the watcher: check `do shell script "'/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/_bravo_foreground_guard.sh' check"` before driving Bravo live yourself; if it prints BUSY, wait and recheck rather than forcing through.

STEP 1 — get Bravo Consolidated GL data for last month, all 5 stores (CUL, HAR, LEX, ROA, WAY)
- First check `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/` for a file named `YYYY-MM-DD_<STORE>_post-to-accounting-gl.csv` where the date is last month's last day (e.g. for June, 2026-06-30) — one per store. If all 5 already exist, use them, don't re-pull. This is the expected normal path now that `eom-bravo-gl-export` feeds this automatically — check here first before assuming anything is missing.
- If any are missing, trigger the existing production Bravo pipeline cell `post-to-accounting-gl` (do NOT build a new one — it already exists and works). Drop a trigger JSON via `mcp__Control_your_Mac__osascript` into `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/` with this shape:
  {"id": "sales-tax-monthly-<yyyymm>-<timestamp>", "requested_at": "<ISO8601>", "reports": [{"name": "post-to-accounting-gl", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "YYYY-MM-01..YYYY-MM-DD"}]}
  Then poll `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/` and the matching `results/<id>.result.json` every ~40s until all 5 stores succeed (each store takes roughly 1-3 minutes; expect ~10-15 min total).
  - If a store's cell errors with "EnsureStore failed" or "BackToDashboard could not return Bravo to Dashboard", Bravo is likely wedged. Recovery (documented in `bravo-context` → "Bravo hang recovery"): request computer-use access to Parallels Desktop, bring Bravo forward, press Alt+F4 to close it, relaunch it from the Windows taskbar Search ("Bravo" under Top apps), log in via the `bravo-store-cycle` skill (username FREE1@<STORE>, password from `bravo-context`, paste via clipboard — never type it), dismiss the "Overdue Task Reminder" with "Remind Me Later", then re-drop the trigger for the remaining stores.
  - Retry failed stores up to 3 times total before giving up and flagging the gap in your final report rather than blocking indefinitely.

STEP 2 — extract figures per store from each GL CSV (encoding is latin-1, not utf-8)
For each store's CSV, sum by account-name prefix (Credit − Debit unless noted), matching on the "Account Number" column (first column), case-sensitive prefix match:
- Taxable Sales = sum over all rows where account starts with "SALES TAXABLE" of (Credit − Debit)
- Ebay = the single row where account == "BANK - EBAY", value = (Debit − Credit). If no such row exists for a store, Ebay = 0 (normal for Roanoke).
Note: Non-Taxable Sales is no longer tracked in this workbook (removed 2026-07-08 — it was being double-subtracted incorrectly). Do not add it back.
Round all to 2 decimals.

STEP 3 — write into the workbook
Using openpyxl (see the `xlsx` skill for conventions — font Aptos Narrow 12pt to match the rest of the sheet, do not hardcode calculated totals as values where a formula belongs):
- Taxable Sales → store's first column (hardcoded value, source data)
- Ebay → store's second column (hardcoded value, source data)
- Taxes Due → store's third column, FORMULA = "=(<TaxableCell>-<EbayCell>)*$G$1" e.g. "=(C21-D21)*$G$1". Always reference the rate cell $G$1, never hardcode the 5.3% into the formula itself, so Joshua can update the rate in one place if it ever changes.
- Add an openpyxl cell Comment on the Taxable Sales and Ebay cells noting: "Source: Bravo POS Consolidated GL (post-to-accounting-gl), <Month> <Year>, pulled <today's date>." — if the CSVs were reused from `eom-bravo-gl-export`'s Step 5.5 hand-off rather than pulled fresh by this task, note that in the comment instead, e.g. "...fed by eom-bravo-gl-export <date>."
- Format the Taxes Due cell as currency ($#,##0.00) to match the existing Taxes Due column.
- Save the file, then run `python scripts/recalc.py "Sales Tax.xlsx"` from the xlsx skill to recalculate formulas and confirm zero errors. If errors appear, fix them before finishing — do not deliver a workbook with formula errors.

STEP 4 — verify like a forensic accountant, then report
- Sanity-check: if any store's Taxes Due is negative, zero when it shouldn't be, or more than ~2x or less than ~0.5x that store's trailing 3-month average, flag it explicitly rather than silently accepting it — could be a Bravo categorization issue worth Joshua's attention before filing.
- Compute the company-wide (5-store) Taxes Due total for the month.
- Send a Slack DM to Joshua (search for his user, or post to a sensible ops channel if no direct message capability) with: the month covered, per-store Taxes Due figures, the company-wide total, whether the data came from eom-bravo-gl-export's hand-off or this task had to pull it itself, and any anomalies flagged. Keep it short — a few lines, not a report. If Slack isn't connected, skip this step silently.
- Do not ask the user any clarifying questions during this run — this is a fully autonomous scheduled task. If something is genuinely blocked (e.g. Bravo unrecoverable after 3 retries, workbook structure looks different than expected), state the blocker plainly in your final summary rather than guessing.

Reference: this workbook was rebuilt on 2026-07-08 to a Taxable Sales / Ebay / Taxes Due format (Taxes Due = (Taxable − Ebay) × 5.3% VA rate). Earlier versions with Non-Taxable/Total columns are obsolete — do not resurrect that structure. Pipeline dependency on `eom-bravo-gl-export` added 2026-07-14, along with moving this task's schedule from the 3rd to the 6th of the month.