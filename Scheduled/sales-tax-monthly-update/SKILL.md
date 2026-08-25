---
name: sales-tax-monthly-update
description: Monthly Valley Pawn sales tax data refresh — runs the 1st, 2 hours after eom-bravo-gl-export, reuses the per-store GL CSVs that task pulls as part of its own core process, actively waits/retries/falls back if missing, and populates Sales Tax.xlsx (Taxable Sales / Ebay / Taxes Due format). Never leaves a month silently blank — alerts Joshua if it truly can't get the data.
model: claude-sonnet-5
---

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
You are updating Full Circle Finance Inc DBA Valley Pawn's monthly sales tax workbook. Act as a forensic accountant — precise, source-cited, and willing to flag anomalies rather than paper over them.

GOAL: populate the row for LAST CALENDAR MONTH (relative to today) in the workbook at:
/Users/joshuadavis/Documents/Claude/Projects/Sales Tax/Sales Tax.xlsx (Sheet1)

BACKGROUND / CONTEXT — read first
- Read the `valley-pawn-context` and `bravo-context` skills for company/store details and Bravo operating procedure before doing anything.
- As of 2026-07-08 the workbook layout is: cell G1 holds the VA sales tax rate assumption (currently 5.3% = 4.3% state + 1.0% local — this is the standard rate and applies to all 5 stores, none of which are in a special regional-tax zone; verify this is still current if it's been a long time since last checked). Row 3 has store names merged across 3 columns each; row 4 has column headers "Taxable Sales" | "Ebay" | "Taxes Due" repeated per store. Data starts at row 5, ONE row per month (no more two-row-per-month structure — that was removed 2026-07-08 along with the old Non-Taxable and Total columns).
- Store column starts: Culpeper C (Taxable=C, Ebay=D, Taxes Due=E), Harrisonburg F (F,G,H), Lexington I (I,J,K), Roanoke L (L,M,N), Waynesboro O (O,P,Q).
- Column A has month labels already typed in sequence (SEP, OCT, NOV, DEC, JAN, FEB, MAR, APRIL, MAY, JUNE, JULY, AUG, SEP, OCT, NOV, DEC — running Sep 2025 through Dec 2026 as of 2026-07-08). Find the row whose column-A label matches last month's name in the correct calendar position. If last month's row doesn't exist yet (workbook wasn't extended that far), add a new row directly below the last row in use with the month label in column A, matching the same formatting/formulas as the row above it. Do not restructure or overwrite any other row.
- **Before writing anything, check whether last month's row already has data in it.** If it's already fully populated (all 5 stores' Taxable Sales / Ebay filled in), this run has nothing to do — verify and stop rather than overwriting good data. This guards against accidental double-runs.

PIPELINE DEPENDENCY (updated 2026-08-03; hardened 2026-08-24 after a real miss) — read before Step 1
This task now runs the 1st of the month at 8:00 AM, 2 hours after `eom-bravo-gl-export` (runs the 1st at 6:00 AM, fully scripted as of 2026-08-02 — no Parallels/computer-use in its normal path). As part of ITS OWN core process (not a bolt-on), that task posts unposted days and pulls the per-store `post-to-accounting-gl` CSVs for the prior month — the exact same CSVs this task needs. Both tasks target the prior calendar month, which has already fully ended by the 1st, so running this early in the new month is safe in principle — the 2-hour gap is meant as buffer for the upstream task's ~10-15 min pipeline runs, not a hard data-availability guarantee.

**KNOWN FAILURE (2026-08-24): the July 2026 row was silently left blank.** The 2-hour gap was not enough on that run — the CSVs weren't actually written until roughly a day later (`eom-bravo-gl-export` ran late/slow that cycle) — and this task's fallback pull either didn't trigger or failed without telling anyone. The row sat empty for 3+ weeks until Joshua noticed and asked why. Root cause: Step 1 as previously written checked once, and if the data wasn't there, the task either silently ended or its fallback path was never actually exercised. **Do not repeat that failure mode.** Step 1 below now requires an active wait/retry loop before falling back to a live pull, and Step 4 now requires a plain DM to Joshua any time the row could not be fully filled — never a silent skip.

STEP 1 — get Bravo Consolidated GL data for last month, all 5 stores (CUL, HAR, LEX, ROA, WAY)
- First check `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/` for a file named `YYYY-MM-DD_<STORE>_post-to-accounting-gl.csv` where the date is last month's last day (e.g. for June, 2026-06-30) — one per store. If all 5 already exist, use them, don't re-pull. This is the expected normal path now that `eom-bravo-gl-export` produces this automatically as part of its own process — check here first before assuming anything is missing.
- **If any are missing, do NOT immediately give up or silently move on.** First wait for `eom-bravo-gl-export` to finish, since it may simply still be running: re-check the output folder every 3 minutes for up to 20 minutes total (about 7 checks). If all 5 appear during this wait, use them and skip the trigger below entirely — this is the common recovery case (upstream just ran long) and needs no pipeline trigger of its own.
- If still missing after that 20-minute wait, trigger the existing production Bravo pipeline cell `post-to-accounting-gl` yourself (do NOT build a new one — it already exists and works). Drop a trigger JSON via `mcp__Control_your_Mac__osascript` into `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/` with this shape:
  {"id": "sales-tax-monthly-<yyyymm>-<timestamp>", "requested_at": "<ISO8601>", "reports": [{"name": "post-to-accounting-gl", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "YYYY-MM-01..YYYY-MM-DD"}]}
  Then poll `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/` and the matching `results/<id>.result.json` every ~40s until all 5 stores succeed (each store takes roughly 1-3 minutes; expect ~10-15 min total). Before driving Bravo live, check the concurrency guard `eom-bravo-gl-export` uses so you don't collide with it or the watcher: `do shell script "'/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/_bravo_foreground_guard.sh' check"` — if it prints BUSY, wait and recheck rather than forcing through.
  - If a store's cell errors with "EnsureStore failed" or "BackToDashboard could not return Bravo to Dashboard", Bravo is likely wedged. Recovery (documented in `bravo-context` → "Bravo hang recovery"): request computer-use access to Parallels Desktop, bring Bravo forward, press Alt+F4 to close it, relaunch it from the Windows taskbar Search ("Bravo" under Top apps), log in via the `bravo-store-cycle` skill (username FREE1@<STORE>, password from `bravo-context`, paste via clipboard — never type it), dismiss the "Overdue Task Reminder" with "Remind Me Later", then re-drop the trigger for the remaining stores.
  - Retry failed stores up to 3 times total.
- **If, after the 20-minute wait AND the trigger-and-3-retries path, any store's CSV is still missing: STOP and go straight to the DM in Step 4 flagging exactly which store(s) are blocked and why.** Never end the run with the month's row left blank and nobody told — that silent-skip is the exact failure this hardening pass exists to close.

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
- Add an openpyxl cell Comment on the Taxable Sales and Ebay cells noting: "Source: Bravo POS Consolidated GL (post-to-accounting-gl), <Month> <Year>, pulled <today's date>." — if the CSVs were reused from `eom-bravo-gl-export`'s pull rather than pulled fresh by this task, note that in the comment instead, e.g. "...fed by eom-bravo-gl-export <date>."
- Format the Taxes Due cell as currency ($#,##0.00) to match the existing Taxes Due column.
- Save the file, then run `python scripts/recalc.py "Sales Tax.xlsx"` from the xlsx skill to recalculate formulas and confirm zero errors. If errors appear, fix them before finishing — do not deliver a workbook with formula errors.

STEP 4 — verify like a forensic accountant, then report (ALWAYS runs — success or blocked)
- Sanity-check: if any store's Taxes Due is negative, zero when it shouldn't be, or more than ~2x or less than ~0.5x that store's trailing 3-month average, flag it explicitly rather than silently accepting it — could be a Bravo categorization issue worth Joshua's attention before filing.
- Compute the company-wide (5-store) Taxes Due total for the month.
- **If the row was successfully filled:** send a Slack DM to Joshua (search for his user, or post to a sensible ops channel if no direct message capability) with: the month covered, per-store Taxes Due figures, the company-wide total, whether the data came from eom-bravo-gl-export's pull, this task's wait-loop, or a live pull it triggered itself, and any anomalies flagged. Keep it short — a few lines, not a report.
- **If Step 1 could not get all 5 stores' data even after the wait loop and the trigger-and-3-retries path:** this is NOT a silent-skip case. Send Joshua a plain-language Slack DM (per Failure Alert Policy v2 — no technical jargon, no stack traces) saying the month's sales tax figures could not be pulled from Bravo yet, naming which store(s) are still missing, and that the row is being left blank until the data is available — then explicitly note this needs a manual follow-up or a re-run once Bravo data catches up. This DM is the final action that completes the run even in the blocked case — do not end the task without sending it.
- If Slack isn't connected at all (not just this DM failing, but no Slack capability whatsoever), state the blocker plainly in your final summary instead — but this should be very rare given Slack is the normal channel for every other Valley Pawn task.
- Do not ask the user any clarifying questions during this run — this is a fully autonomous scheduled task.

Reference: this workbook was rebuilt on 2026-07-08 to a Taxable Sales / Ebay / Taxes Due format (Taxes Due = (Taxable − Ebay) × 5.3% VA rate). Earlier versions with Non-Taxable/Total columns are obsolete — do not resurrect that structure. Pipeline dependency on `eom-bravo-gl-export` added 2026-07-14; simplified 2026-08-02 when `eom-bravo-gl-export` itself became fully scripted; both tasks moved to fire on the 1st of the month 2026-08-03 (6:00 AM / 8:00 AM respectively) per Joshua's request. Hardened 2026-08-24 (active wait/retry loop in Step 1, mandatory alert-on-failure in Step 4) after the July 2026 row was found silently blank three weeks after the fact — see `Life OS/OPEN_ITEMS_REGISTER.md` 2026-08-24 entry for the incident writeup.
