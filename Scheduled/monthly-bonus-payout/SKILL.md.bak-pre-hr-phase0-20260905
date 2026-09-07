---
name: monthly-bonus-payout
description: Monthly (10th, 11:30 AM — after qualifiers): compute per-employee bonus payouts for the completed month (two-bridge gate, Tier 2 / Aug+ penalty regime), fill the Payouts + Trend tabs in VP_Bonus_Tracker_MASTER_2026.xlsx, draft results for Joshua — never auto-sent, never touches Gusto. Payday = first Friday after the 15th.
model: claude-sonnet-5
---

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard, added 2026-08-02).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed with the task.
> 3. If it errors (no such tool available, not connected, tool-not-found): wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **NEVER conclude that this run executes in a cloud container, has no bridge to the Mac Studio, or otherwise lacks local/desktop access. That conclusion is false** and is the single most common cause of a false failure on this platform. If you believe you cannot reach the Mac, you have simply not loaded the tool yet — go back to step 1.
>
> **Filesystem rule:** all I/O outside the agent sandbox — including anything under `/Users/joshuadavis/Documents/Claude/...` — goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s inside one call; poll in short increments across separate calls. Guard any command that may exit nonzero with a trailing || true.


> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


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
You calculate the monthly bonus/commission payout for Valley Pawn employees (Managers, Sales & Loan Associates/Representatives) across all 5 stores. DRAFT-ONLY for money: never post $ amounts to public Slack (use `slack_send_message_draft`, never `slack_send_message`, for anything with dollar figures), never write to Gusto (no payments, no payroll runs — read-only for job titles/departments via `list_employees`). Additive task. Read valley-pawn-context and bravo-context first; read `monthly-bonus-qualifiers`'s latest output for the target month before computing anything — do not recompute qualifiers yourself, that task is the source of truth and its schema is stable by design.

## Standing fact — data source of truth (confirmed 2026-07-16)
**Never use QuickBooks/QBO as a source of truth for any KPI or revenue figure in this task, or anywhere in the bonus program.** Bravo and Bravo-extracted data (Company Performance / KPI reports, End-of-Month reports, Store Rankings exports) are the only source of truth for revenue and every other business KPI used here. QBO's own categorization isn't reliable for this: a spot-check of June 2025 found the entire month's income sitting in an uncategorized "Ask My Accountant" bucket rather than a real Income account, with no store-level split at all. If Bravo data is unavailable for a given month, report the gap — do not fall back to QBO.

## Tier 1 — TWO-BRIDGE GATE (redefined 2026-07-16 by Joshua; read from monthly-bonus-qualifiers' output, do not recompute)
- **Bridge 1 (hard gate):** store's 2026 Revenue Actual >= its 2026 Bonus Target for the month. **If Bridge 1 fails, the store's bonus is $0 for every employee at that store that month, period — do not compute anything else for that store/month.**
- **Bridge 2 (rate selector, only relevant if Bridge 1 passed):** store's 2026 Revenue Actual >= its same-month 2025 Revenue (prior year). This selects which commission rate applies below — it does not independently zero out the bonus.
- **Verified real-world impact (June 2026, informational only — do not retroactively re-pay):** Roanoke failed Bridge 1 that month (Actual $42,193.38 < Target $47,164.52) — Benjie's actual payment of $738.14 was computed under the old single-gate rule and would be $0 under this corrected rule. Lexington passed both bridges (Actual $24,977.23 >= Target $24,064.52 >= prior-year $23,134.00) — Uriah was paid $0 in June under the old process but would have qualified under this corrected rule. Apply the two-bridge rule going forward from July 2026 onward; for any earlier month, note the discrepancy if asked but do not unilaterally issue retroactive pay.

## Formula — TWO regimes, pick by month
**June 2026 and earlier (OLD, additive-only-if-hit)** — validated exactly against Preston Peters' real June numbers under the OLD single-gate rule (Chadd $1,235.41, Martin $491.18, Sandi $1,666.23, Bree $541.56, Robert $356.56, Benjie $738.14, Walker $1,233.33, Lexington $0). Note Benjie's and Lexington's figures are now known to be wrong under the corrected two-bridge rule (see above) — reproduce them only if explicitly asked to show "what was actually paid," and flag the discrepancy inline; use the two-bridge rule for any new calculation.
- Manager: 2% base commission on Revenue. If store's Tier 2 (3-qualifier set: Reviews + Email + Gold, gated on Bridge 1) was hit, add +0.5% (→2.5% total). If Bridge 1 wasn't hit, no bonus at all regardless of Tier 2.
- Associate/Representative: 4% base commission on Retail/Sales Gross Profit. Same +1% add-on logic (→5% total) gated the same way.
- Confirmed from real data: Benjie/Roanoke got exactly 2% (Tier 2 = No) — now known to actually owe $0 (Bridge 1 fail). Sandi/Culpeper got exactly 2.5% (Tier 2 = Yes, Bridge 1 pass).

**July 2026 onward (NEW, symmetric bump-or-penalty)** — per Joshua 2026-07-16: "if a store hit their monthly bonus and hits their task bonus the manager would get 2.5% but if they hit their monthly number and did not hit task they will get 1.5%":
- Manager: base rate 2%. If Bridge 1 hit AND Tier 2 hit → 2.5%. If Bridge 1 hit AND Tier 2 NOT hit → 1.5%. If Bridge 1 not hit → no bonus (hard gate, see above).
- Associate/Representative: base rate 4%, ± 1% instead of ± 0.5% → 5% if Tier 2 hit, 3% if Bridge 1 hit but Tier 2 missed, 0 if Bridge 1 missed.
- Tier 2 for July+ = full 4-qualifier set (Reviews + Email + Gold + **Social Media**, all gated on Bridge 1). Read the exact qualifier counts and threshold-met flags from `monthly-bonus-qualifiers`' output, do not recompute.
- **Top Performer Bonus**: $300 pool (or current Settings-tab amount from `monthly-bonus-qualifiers`' spreadsheet — reread each run rather than hardcoding) paid ONLY to the single store `monthly-bonus-qualifiers` names as Overall Top Performer, split among that store's employees. Not distributed to all 5 stores. This is separate from, and paid in addition to, Preston's Market Manager override below.

## Preston Peters — Market Manager override (CONFIRMED 2026-07-16 by Joshua)
Preston Peters (Market Manager, dept "Corporate Support") gets a separate, standing bonus: **$300 per store that hits its bonus that month.** "Hits its bonus" = Bridge 1 passes for that store that month (2026 Revenue Actual >= 2026 Bonus Target) — the same hard gate used for every store's employee commissions above. This is independent of Bridge 2, Tier 2 qualifiers, and the Top Performer pool; it's a flat $300 per Bridge-1-passing store, up to 5 stores ($1,500 max/month). This applies both to the OLD and NEW regimes — it doesn't change with the July 2026 formula switch, only the per-store gate (Bridge 1) matters.
- Compute: count how many of the 5 stores pass Bridge 1 that month (per `monthly-bonus-qualifiers`' output), multiply by $300 — that's Preston's payout for the month.
- Example: June 2026 under the corrected two-bridge rule — Culpeper, Harrisonburg, Lexington, and Waynesboro passed Bridge 1; Roanoke failed. Preston's June payout = 4 x $300 = $1,200.
- Include Preston as his own row in the per-employee tab (role "Market Manager", basis "N/A — flat $300 per Bridge-1-passing store", stores hit / stores total e.g. "4/5", bonus $ = stores-hit x $300). Do not fold him into any store's rollup — his bonus is company-wide, not store-attributed.

## Basis sourcing — CORRECTED 2026-07-16
- **Manager basis = Bravo's native "Net Revenue" KPI for that store/month, NOT VP BONUS FINAL's column D.** `Net Revenue = Pawn Service Charges (interest & fees, MTD) + Retail Sales Gross Profit Amt (MTD) + Scrap Sales Gross Profit Amt (MTD)`. Pull this from Bravo's "Company Performance" report (Store menu → Company Performance, or the Drive-extracted "BRAVO Company Performance.xlsx" pipeline output) for the target month. This was confirmed 2026-07-16 by matching Preston's actual June 2026 Slack commission figures to the exact Net Revenue line in that report (Culpeper $66,649.27, Harrisonburg $61,666.31, Roanoke $36,906.77, Waynesboro $43,416.44 — all matched to the penny). VP BONUS FINAL's column D runs $5,300–$9,900+ higher per store per month than actual Net Revenue and must NOT be used as the commission basis — it's a target-tracking figure only, useful for the Bridge 1/Bridge 2 gate check above, not for the dollar math.
- **Store-without-a-titled-Manager rule:** if a store has no active Gusto employee titled "Manager" (confirmed case: Harrisonburg, where Walker Tapley — titled "Sales and Loan Associate" — is the de facto lead and was paid on the Manager/Revenue-basis formula, not the Associate/Gross-Profit-basis formula), treat that store's de facto lead the same way: Manager-tier formula and Net Revenue basis, regardless of their formal Gusto title. Flag this explicitly in the output so it's visible, not silent.
- Associate/Representative basis = "Retail Gross Profit" / "Sales Gross Profit" from the Employee Productivity Report for that store/month (e.g. `Valley_Pawn_MTD_Employee_Rankings_*_BRAVO.xlsx` or the Employee Performance Deep Dive report) — use per-employee figures, not store aggregate.
- Roles/titles/store assignment: Gusto `list_employees`, `department` field = store. Roles seen: Manager, Sales and Loan Associate, Sales and Loan Representative, Market Manager, Chief Executive Officer, Chief Support Officer. Only Manager and Sales-and-Loan (Associate/Representative) roles get the per-store commission bonus; corporate roles are excluded from that part — except Preston, whose separate Market Manager override is defined above.

## Output
1. Spreadsheet `Bonus Payout — {Month} {Year}.xlsx` in Drive folder 1nR6j_0IL6Jqtn2pXlc4hqJjo_uahM7Ru: per-employee tab (name, role, store, basis, base rate, bonus rate applied, bonus $ — including Preston's Market Manager row), per-store rollup tab, Top-Performer-payout tab, a dedicated "Preston / Market Manager" line showing stores-hit count and total, and a "Gaps" tab listing anything you couldn't compute and why.
2. A DRAFT Slack DM to Joshua (U03BB52MDSA) — never sent directly — summarizing total payout, per-store totals, which regime (OLD/NEW) applied and why, Bridge 1/Bridge 2 result per store, Preston's payout and store-hit count, and any gaps.
3. Never silently drop an employee the formula would pay just because a reference list (e.g. Preston's June message) didn't happen to mention them — the formula is the source of truth for who's owed something, the reference data is only for validating the rate math.
4. Never silently drop a store to $0 either — if Bridge 1 fails, show the store explicitly with a $0 result and the reason, so it's visible rather than absent from the sheet.

## Failure policy
If `monthly-bonus-qualifiers` hasn't been run for the target month yet, or Gusto/Employee Productivity Report data is missing, do not guess — draft a Slack DM to Joshua listing exactly what's missing and stop. Never fabricate a number.
## AUGUST 2026 REGIME CHANGE (announced by Joshua 2026-07-21 - applies to August earnings, paid September)
Effective with the August 2026 earning month, the task-qualifier set and rate logic change:
1. **New qualifier - Facebook follower gains (per store).** Data rail: **Publer analytics** (system of record for all social - never raw FB Graph tokens). Threshold per store TBD by Joshua/Preston before first August evaluation - flag if unset at run time. This REPLACES the QR-landing-page-views social proxy for qualifier purposes.
2. **New qualifier - Revenue YOY.** Store must beat same-month prior-year revenue by at least $1 (this formalizes Bridge 2 as an explicit task goal alongside Reviews/Email/Gold/Facebook).
3. **Penalty rule (symmetric).** Missing task goals is no longer just "no bump" - it is a **-0.5% penalty off the commission rate**. Manager: 2.5% (hit) / 1.5% (miss). Associate/Rep: per Joshua's 2026-07-21 statement the penalty is 0.5%; prior July-regime documentation showed the associate spread as 5%/3% - CONFIRM the associate miss-rate (3.5% vs 3.0%) with Joshua before the first August payout calc and update this line.
4. June/July runs are unaffected - use the regime rules above this section for any month <= July 2026.
## AUGUST 2026 REGIME - CONFIRMED DETAILS (Joshua 2026-07-21, second confirmation)
- **Facebook follower-gain threshold: +15 net new followers per store per month** (via Publer). Not TBD anymore - use 15.
- **Penalty structure confirmed via Manager example: Managers get 2.5% if they hit the task goals, 1.5% if they miss.** (Base 2% +/- 0.5%.) Applying the same symmetric +/-1% around base for Associates/Reps: 5% hit / 3% miss - consistent with the previously documented July+ spread; the "0.5%" figure refers to the Manager swing. The earlier CONFIRM flag in the section above is now RESOLVED: Associate miss-rate = 3.0%.

- **August 2026+: Reviews threshold raises from 12 to 15 per store per month** (Joshua 2026-07-21). June/July stay at 12.

## DATA-RAIL CORRECTIONS + PUBLER VERIFICATION (2026-07-21)
**Email % and Reviews come from the Monday combined run - do NOT re-pull separately:**
- Email %: the Monday combined Bravo run already pulls the "Chekkit Invites" custom report (chekkit-inactives/gridonly cells) weekly - it captures BOTH email and phone. Qualifiers task should read the accumulated Monday CSVs for the target month from the pipeline output / _shared-bravo-data folders (latest pull on/after month-end covers the month).
- Reviews: Chekkit review data is also already pulled every Monday (review-obtained-last-week + weekly digests). Use those weekly pulls summed to the calendar month; only fall back to a direct Chekkit leaderboard month-window read if a week is missing or a store sits on a threshold boundary.
**Publer Facebook follower rail - TESTED LIVE 2026-07-21, WORKS:**
- Path: app.publer.com -> Analytics -> Overview -> pick store account in left rail -> date-range dropdown (top right) -> "Last month" (= prior calendar month). Followers card shows total + net gain/loss badge for the period. Chrome saved session logs in automatically.
- Store account analytics URLs: Culpeper /#/analytics/overview/6a3596d3fe216c70f7e67261 · Harrisonburg /#/analytics/overview/6a3596d807e1b3bf83f1c379 · Lexington /#/analytics/overview/6a3596d4fe216c70f7e67266 · Roanoke /#/analytics/overview/6a3596d2bbd130d6e889bf58 · Waynesboro /#/analytics/overview/6a3596d789dea67771497918
- June 2026 verification values (vs +15 August threshold): Culpeper 876 (+1), Harrisonburg 763 (+1), Lexington 1.6K (0/no badge), Roanoke 35 (+1), Waynesboro 1.2K (-1). Every store would currently MISS the +15 bar - stores need a real follower push before August.

## GOLD ATTRIBUTION RULE - VERIFIED FROM BRAVO DATA 2026-07-21 (supersedes name-based matching)
Gold for bonus month M = gold buckets with Status=CLOSED and **StatusDate falling in month M** (Preston's physical collection run closes them). Attribute by CLOSE DATE, never by bucket name (names are inconsistent per store: WAY named its 7/20-closed buckets "JULY", CUL/ROA named theirs "JUNE") and never by CreatedOn.
Proof: June bonus gold per Preston = buckets closed 6/6 (HAR 66.35+26.10=92.45, ROA 30.61+28.70=59.31, WAY 70.49+31.44=101.93 - exact match to his tracker).
July 2026 bonus gold = buckets closed 7/20 (FINAL): CUL 128.63+148.02=**276.65 PASS** | ROA 53.29+42.37=95.66 | LEX 41.57+23.50=65.07 | HAR 34.80+25.89=60.68 | WAY 27.04+29.50=56.54. Only Culpeper passes the 100dwt bar for July.
Pipeline note: run scrap-refining-gold and filter output rows by StatusDate month = bonus month. The monthly qualifiers run (2nd) captures this correctly as long as Preston's collection happened during the bonus month (it did: 6/6, 7/20).
## SCHEDULE + OUTPUT TARGETS (set 2026-07-21, supersedes the 2nd/3rd schedule)
Both tasks now run on the **10th of every month** (qualifiers 9:00 AM, payout 11:30 AM), computing the just-completed month. The 10th gives time for month-end data to settle and precedes payday (first Friday after the 15th).
Required outputs each run - ALL of these, every month:
1. **VP BONUS FINAL trackers (BOTH copies)**: write the completed month's 2026 Revenue actual into column D of the "2025 compared to Bonus" sheet for all 5 stores, in BOTH files: `VP BONUS FINAL Updated.xlsx` (Drive, id 1AC-LF0gEPDLY0oUWZ7D1hCITt_xECHcx - the live file Preston uses) and the local `/Users/joshuadavis/Documents/Claude/Projects/Optimize Loan Portfolio/_input_VP_BONUS_FINAL.xlsx` reference copy. Revenue = Sales Revenue Profit + Interest & Fees Total from Bravo EOM (the verified methodology).
2. **Master tracker**: `/Users/joshuadavis/Documents/Claude/Projects/Bonus Program/VP_Bonus_Tracker_MASTER_2026.xlsx` - append/fill the month tab (qualifiers run) and payout lines + Trend + Running Totals refresh (payout run). Keep the existing tab schema exactly.
3. Slack: qualifiers summary to #bonus-goals (status data, direct post OK); payout numbers DRAFT-ONLY to Joshua.

- Payout delivery (Joshua 2026-07-21): send the per-store/per-employee payout breakdown as a DIRECT SLACK DM to Joshua (U03BB52MDSA) each run - private DM is approved for dollar figures; public channels remain draft-only. Then fill the Trend + Running Totals tab in the master tracker.

## FILE-ID CORRECTION (2026-07-21): the LIVE VP BONUS FINAL tracker is `VP BONUS FINAL Updated.xlsx` Drive id **1HKTWucLG8R2Yzgdm62vb2rrwYUTpntBB** (has Cumulative Variance + YoY Rev Var columns; targets refreshed monthly by monthly-bonus-targets). Id 1AC-LF0gEPDLY0oUWZ7D1hCITt_xECHcx is the 2026-07-02 BACKUP - do NOT write to it. Monthly runs must write actuals to the LIVE file (edit in Google Sheets via Chrome) + the local `_input_VP_BONUS_FINAL.xlsx` copy, keeping both in sync with live values.
