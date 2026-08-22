---
name: monthly-bonus-targets
description: Generate next month's store revenue bonus targets for Valley Pawn using Option B yield methodology (Bravo data pulled via the trigger/watcher pipeline, no computer-use), update the VP BONUS FINAL spreadsheet, and draft a Slack message for Joshua's review. Runs automatically day 2 of each month, 9 AM.
model: claude-opus-4-8
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

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
You are generating next month's store revenue bonus targets for Full Circle Finance Inc DBA Valley Pawn using the Option B yield methodology. Run this at the end of each calendar month, or on demand when Joshua asks.

## Context
- Company: Full Circle Finance Inc DBA Valley Pawn
- Stores: Culpeper, Harrisonburg, Roanoke, Lexington, Waynesboro
- Tracking spreadsheet: Look for "VP BONUS FINAL Updated.xlsx" / "VP BONUS FINAL*.xlsx" / "VP_BONUS_FINAL_rebuilt.xlsx" in the "Claude 4 back up" mounted folder (typically at a path like /sessions/<session>/mnt/Claude 4 back up/). The rebuilt version has a new row layout — see Step 3 below. NOTE (2026-08-02): the live file has repeatedly turned out to be the PRE-rebuild layout, not the rebuilt one — always confirm actual row numbers per Step 3, never assume.
- Slack channel for bonus goals: #bonus-goals (channel ID: C04TXF0KGNL)
- Bravo KPI data: pulled programmatically through the Bravo Data Extraction trigger/watcher pipeline (see Step 2, added 2026-08-02) — NOT via computer-use/Parallels GUI. This is what makes the task runnable unattended on a schedule; computer-use access cannot be approved during a non-interactive scheduled run, which is why the original computer-use design blocked every scheduled attempt.

## CRITICAL RULES (added 2026-08-02 — read before Step 2)
- **NEVER use Parallels GUI / computer-use for this task, and NEVER ask Joshua to sign into Bravo.** All Bravo access is via the trigger/watcher pipeline over `mcp__Control_your_Mac__osascript`. This is the same no-GUI design already proven by `weekly-store-kpis`, `daily-funds-verification`, and `monday-bravo-combined-run`.
- All host execution / file I/O for anything under the Bravo Data Extraction folder is via `mcp__Control_your_Mac__osascript` `do shell script` (load via ToolSearch `select:mcp__Control_your_Mac__osascript` if not already loaded). NEVER use the Write/Edit tools for files under that folder or under `/Users/joshuadavis/Documents/Claude/Scheduled/` — both are outside this session's connected folders and will error; osascript reaches the real filesystem directly.
- Read `/Users/joshuadavis/Documents/Claude/Scheduled/BRAVO_KNOWN_ISSUES.md` first if anything about the pull looks off (stalled trigger, missing output, a store failing repeatedly). Don't re-litigate settled facts in there. In particular: WAY has a recurring history (7/21, 7/23, 7/27–7/31 2026) of losing its Bravo window mid-pull with a 0% headless-recovery success rate — one retry (via one `_restart_watcher.ps1` cycle) is reasonable; a second consecutive failure on the same store is not a reason to attempt Parallels GUI recovery. Proceed with the other 4 stores' data if only WAY is missing, note the gap, and DM Joshua per the failure policy for that store specifically — never fabricate or estimate a missing store's figures.
- `osascript do shell script` calls time out around ~25s — keep in-call sleeps ≤18s, poll across separate calls, and avoid literal single quotes / unescaped parentheses in AppleScript strings (use `quoted form of`, or base64-encode content that's complex).

## Standing fact — data source of truth (confirmed 2026-07-16)
**Never use QuickBooks/QBO as a source of truth for any KPI or revenue figure in this task.** Bravo and Bravo-extracted data (Company Performance / KPI reports, End-of-Month reports, Store Rankings exports) are the only source of truth for revenue and every other business KPI used here.

## CRITICAL — "Net Revenue" definition (corrected 2026-07-16, read carefully)
Column D ("2026 Revenue Actual") must be Bravo's **Net Revenue** KPI, and nothing else. This was found to be the root cause of a real data-quality bug: multiple months of column D had been populated with a broader, WRONG figure (apparently "Retail Sales Total Amt" and/or "Retail Sales + Pawn Service Charges," i.e. gross figures, not gross-profit-based Net Revenue) — these ran $5,000–$30,000+ higher per store per month than true Net Revenue, silently breaking every Bridge 1 (target-hit) determination downstream.

**The exact, verified formula:** `Net Revenue = Pawn Service Charges (interest & fees, MTD, in-store only) + Sales Revenue (Profit) (MTD)`. This was confirmed 2026-07-16 by matching it to Preston Peters' actual June 2026 commission-basis figures to the penny (Culpeper $66,649.27, Harrisonburg $61,666.31, Roanoke $36,906.77, Waynesboro $43,416.44, Lexington $21,455.49), and re-confirmed 2026-08-02 as the exact formula already implemented and verified to the penny in `store_kpis_compile.py` (used weekly by `weekly-store-kpis`). Step 2's `bonus_kpis_extract.py` duplicates that same verified formula — do not substitute a different combination of fields.

On the Bravo Company Performance / KPI report (or the End-of-Month xlsx export the pipeline pulls), there is a line literally labeled **"Net Revenue MTD"** — Step 2's script computes this exact figure programmatically. If you ever fall back to reading a Bravo report by hand, always pull that exact line — never "Retail Sales Total Amt," "Retail Sales (Taxable)," or any combination you compute yourself from gross sales figures.

## The Option B Methodology

Revenue target for store S in month M+1:

  Target(S, M+1) = EndingAssets(S, M) × AdjustedYield(S, M+1)
  AdjustedYield = Trail12_AvgYield(S)  [Friday multiplier removed 2026-08-06 - not statistically supported; see Scheduled/bonus-targets-SEASONALITY-FINDINGS-2026-08.md. Effect measured at -1.7% to -9.2% per extra Friday across 2025+2026 data, opposite the assumed +4.5%.]
  MonthlyYield(S, month) = Revenue(S, month) / EndingAssets(S, prior month)
  Trail12_AvgYield = average of the trailing 12 monthly yields ending at the completed month (changed 2026-08-06 from an expanding 2026-only YTD average - see Step 4 for rationale)
"Revenue(S, month)" here means Net Revenue as defined above — the whole target methodology is self-consistent as long as every Revenue input is Net Revenue, never a gross figure.

Ending Assets = Loan Balance + Inventory Balance (from Bravo KPI report — NOT a separate assets field).

## Steps

### 1. Determine months
- Completed month = the calendar month that just ended
- Target month = the next calendar month (M+1)
- Confirm if there's any ambiguity about which month is closing

### 2. Pull Bravo KPI data — via the trigger/watcher pipeline (rewritten 2026-08-02, no computer-use)

This mirrors `weekly-store-kpis`'s proven approach, but requests the FULL completed month (not just month-to-date) since this task runs after the month has closed.

**Step 2.0 — read BRAVO_KNOWN_ISSUES.md** (`/Users/joshuadavis/Documents/Claude/Scheduled/BRAVO_KNOWN_ISSUES.md`) if this is the first Bravo-touching action this session.

**Step 2.1 — osascript gate:** `do shell script "echo READY"` to confirm the channel works.

**Step 2.2 — dates:** Let COMPLETED_MONTH = the month that just closed. FIRST = first day of COMPLETED_MONTH (YYYY-MM-01). LASTDAY = last calendar day of COMPLETED_MONTH (YYYY-MM-DD). ENDDATE = LASTDAY (this becomes both the Bravo report end-date and the filename key). TRIGGER_ID = "bonustargets-" + current timestamp.

**Step 2.3 — ensure Bravo healthy** (same mechanism as `weekly-store-kpis` Step 2): backgrounded call to `bravo_ensure_healthy.sh CUL`, poll `logs/_health_gate_status.txt` (≤18s sleeps, ~12 min cap) until PASS. If it ends FAIL, DM Joshua per the failure policy and STOP — do not fall back to computer-use.

**Step 2.4 — drop ONE 5-store EOM trigger** for the FULL month. JSON (double quotes only):
```
{"id":"<TRIGGER_ID>","requested_at":"<NOW ISO8601>","reports":[{"name":"end-of-month","stores":["CUL","HAR","LEX","ROA","WAY"],"date":"<FIRST>..<LASTDAY>"}]}
```
Write via: `do shell script "printf %s " & quoted form of json & " > " & quoted form of ("/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/" & TRIGGER_ID & ".json")`

**Step 2.5 — poll for the 5 xlsx** (≤18s sleeps per call, ~25 min cap). Done when `results/<TRIGGER_ID>.result.json` exists AND all 5 `output/<LASTDAY>_<STORE>_end-of-month.xlsx` exist and are >500 bytes. If the run aborts early or a store is missing after the cap (most likely WAY — see CRITICAL RULES above), re-run Step 2.3 once and re-drop a fresh trigger for just the missing store(s), cap ~20 more min. If still missing after that, proceed with whichever stores succeeded, note the gap explicitly, and DM Joshua per the failure policy — never estimate a missing store's numbers, never post partial targets to Slack for the whole company if a store's actuals are missing (see Step 8).

**Step 2.6 — extract the KPIs.** Run:
```
do shell script "/usr/bin/python3 '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/bonus_kpis_extract.py' '<LASTDAY>' 2>&1"
```
This is a NEW, additive script (added 2026-08-02) — it does NOT modify `store_kpis_compile.py`. It reuses that script's already-penny-verified Net Revenue formula (Pawn Service Charges + Sales Revenue (Profit)) and reads the same EOM xlsx files, but emits clean JSON with exactly the 3 fields this task needs per store: `net_revenue`, `loan_balance`, `inventory_balance`. On success it prints `{"enddate": "...", "data": {"CUL": {...}, ...}}`. On missing files it prints `{"error": "missing", "missing": [...]}"` and exits 2 — treat that the same as Step 2.5's missing-store case.

**Step 2.7 — Ending Assets** = `loan_balance + inventory_balance` per store, from the Step 2.6 JSON. This is the same figure Step 5 uses as `EndingAssets(S, completed month)`.

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

**Confirmed 2026-08-02: the live file has actually been the PRE-rebuild layout every time it's been checked** (header rows 9/24/39/54/69/84, data 10-21/25-36/40-51/55-66/70-81/85-96, no Preston section, column K is an unrelated "5-Friday vs 4-Friday Months" note column — NOT a Bonus Payout formula). If the file you open doesn't match either layout exactly, locate the header row containing "Month" for each store block dynamically rather than assuming fixed row numbers — don't silently write to the wrong row, and note in your summary to Joshua which layout you found.

Column mapping (A=1 through J=10, both layouts):
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
- K (rebuilt layout only): Bonus Payout (Two-Bridge) — formula, don't overwrite; implements Bridge 1 (D>=C, hard gate) and Bridge 2 (D>=B, rate selector) automatically. In the pre-rebuild layout K is unrelated — do not treat it as a protected formula column there, but also don't write anything to it.

Read D, G, H for all months with actuals to rebuild the YTD yield series for each store.
If H is blank but D and G are present, compute yield = D_value / prior_month_G_value.

### 4. Calculate trailing-12-month average yield (changed 2026-08-06 from expanding YTD - see rationale below)
Build a rolling 12-month yield window ending at the completed month. For the 2026 months, use D/G/H already in the spreadsheet (Step 3). For any months in the window that fall in 2025, pull Ending Assets and Net Revenue via `bonus_kpis_extract.py <ENDDATE>` (full 2025 is already cached in `Bravo Data Extraction/output/` as of 2026-08-06 - reuse those files, do not re-pull Bravo unless a specific month is missing). For each of the 12 months: MonthlyYield = NetRevenue(month) / EndingAssets(prior month). Trail12_AvgYield = average of all 12.
Why trailing-12 instead of expanding YTD: verified 2026-08-06 (see Scheduled/bonus-targets-SEASONALITY-FINDINGS-2026-08.md) that monthly yield does not show a year-over-year-consistent seasonal pattern, so a full 12-month trailing window is the most defensible approach - it always represents exactly one occurrence of every calendar month (never overweights whatever season happens to dominate an expanding YTD window), and it ages out stale early-year readings as new months complete, unlike an expanding-YTD average which grows more anchored to early-year data as the year progresses. Confirmed impact when adopted: shifted the August 2026 targets by -$1,999 (Culpeper), -$2,102 (Harrisonburg), -$157 (Lexington), -$521 (Roanoke), +$178 (Waynesboro) versus the old expanding-YTD method.

### 5. Calculate targets
For each store: Target = EndingAssets(completed month) × Trail12_AvgYield
(No Friday multiplier - removed 2026-08-06, not statistically supported across 2025+2026 data. No seasonal yield term either - tested and also not confirmed; see the findings doc.)
Round to nearest whole dollar.
Company total = sum of all five store targets.

Show a summary table with: Store | Ending Assets | Trail-12 Yield | Target

### 7. Update the spreadsheet

Use openpyxl to update the file. IMPORTANT: be careful with merged cells — use a try/except around each cell write to skip merged non-primary cells gracefully. Never overwrite formula cells (columns E, H, I, J, and K in the rebuilt layout — these recalculate automatically; also never overwrite the Company block's SUM-based cells or the Preston section if present).

For the COMPLETED month row in each store block:
- Column D: actual Net Revenue from Step 2.6/2.7 (`net_revenue`)
- Column G: actual ending assets from Step 2.7 (`loan_balance + inventory_balance`)
- (Columns E, H, I, J, K recompute themselves via formula — do not write to them)

For the TARGET month row in each store block:
- Column C: the new bonus target
- Column F: ending assets assumption (= prior month actual G value)

After writing D/G values, also update the Company-wide summary block's D column for that month (it's a SUM formula referencing the 5 stores in the rebuilt file — confirm it recalculates rather than overwriting it with a literal). In the pre-rebuild layout, confirm whether the Company block's D is a literal or formula before writing — don't overwrite a formula cell.

If any store's data is missing from Step 2 (e.g. WAY failed twice), do NOT write a placeholder or estimate for that store's D/G — leave those cells untouched, compute and write only the stores you have real data for, and flag the gap prominently in the Step 9 summary and in the Slack draft's absence (skip that store from the draft rather than posting a guessed number).

Write mode: load with data_only=False, preserve existing formulas, write updated values, save back. Then run the file through LibreOffice (`recalc.py`, or a direct `soffice --headless --convert-to xlsx` round-trip if recalc.py times out) so cached formula values are refreshed — an openpyxl save alone leaves formula cells blank to anything that reads cached values.
Save to the same path as the source file. chmod 0o644 after saving.

### 8. Draft Slack message — DO NOT SEND

Compose a message for #bonus-goals using EXACTLY this format and structure (this is Joshua's approved template):

```
📅 [Month] [Year] Bonus Targets
[Month] Targets by Store
🏪 Culpeper — $XX,XXX
🏪 Harrisonburg — $XX,XXX
🏪 Roanoke — $XX,XXX
🏪 Lexington — $XX,XXX
🏪 Waynesboro — $XX,XXX

How We Got Here.
-Targets are built using each store's own 2026 YTD yield — not a company average. Formula: [prior month] ending assets × store's YTD yield.
-[Prior Month] Ending Assets (Loans + Inventory):
Culpeper $XXX,XXX · Harrisonburg $XXX,XXX · Roanoke $XXX,XXX · Lexington $XXX,XXX · Waynesboro $XXX,XXX
-YTD Avg Yield (Jan–[Prior Month] [Year]): Culpeper XX.X% · Harrisonburg XX.X% · Roanoke XX.X% · Lexington XX.X% · Waynesboro XX.X%
Each store's number reflects what they've actually been doing this year. Hit it and earn it. This not math anymore, it's science. Let's have a great [Month]. 💪
```

Formatting rules — follow these exactly:
- Each store target is on its own line — never run stores together on one line
- Ending assets: each store on its own line inside the bullet, not comma-separated inline
- "How We Got Here." section uses dash bullets (-), not markdown bullets or bold
- No markdown bold/italic — Slack renders plain text
- No company total line in the targets section
- The sign-off line is fixed every month: "Each store's number reflects what they've actually been doing this year. Hit it and earn it. This not math anymore, it's science. Let's have a great [Month]. 💪"
- If a store's data was missing this run (see Step 7), omit that store's line from the draft entirely and flag it in your chat message to Joshua rather than guessing a number for the template.

Present the full draft to Joshua in chat. Ask him to confirm before sending. NEVER auto-send.
Use Slack MCP tool slack_send_message (channel C04TXF0KGNL) ONLY after Joshua explicitly says "send it" or "looks good, send."

### 9. Deliver summary to Joshua

Present:
1. Per-store target table (from Step 5)
2. Confirmation that spreadsheet was updated with actuals (Net Revenue, not gross) + new targets, and which spreadsheet layout was found (pre-rebuild vs rebuilt)
3. The Slack draft for his review
4. File link to the updated spreadsheet
5. Any store(s) whose Bravo data couldn't be pulled this run, and what's needed to complete them

## Important Notes
- Yield in the formula is a ratio (e.g., 0.186 for 18.6%) — confirm units from spreadsheet before multiplying
- Ending Assets must come from Bravo (Loan Balance + Inventory Balance), not estimated
- Column D must always be Bravo's "Net Revenue MTD" line — never a gross-sales figure, never QBO
- Never auto-send the Slack message — always wait for Joshua's explicit approval
- If Bravo KPI data for the completed month is not yet available (pipeline still catching up right after month-end), note this in the summary and let the schedule (see below) retry — don't ask Joshua a clarifying question in a non-interactive run.
- **Never use computer-use/Parallels for this task as of 2026-08-02.** If you ever find yourself about to call `request_access` for Parallels Desktop in this task, stop — that means Step 2 was skipped or the trigger pipeline is being bypassed; go back to Step 2.

<!-- migrated to working model 2026-06-15 -->
<!-- corrected Net Revenue sourcing + rebuilt-file row layout 2026-07-16 -->
<!-- rewrote Step 2 to use the Bravo trigger/watcher pipeline (bonus_kpis_extract.py) instead of computer-use, so this task can run unattended on a schedule; scheduled cadence added (day 2 of month, 9 AM) — 2026-08-02 -->