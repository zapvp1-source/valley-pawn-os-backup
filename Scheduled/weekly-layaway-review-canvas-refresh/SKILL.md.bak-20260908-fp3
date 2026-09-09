---
name: weekly-layaway-review-canvas-refresh
description: Monday 9:22 AM — overwrite the #layaway-review Slack Canvas from the latest pipeline output so it stays at the top, no manual pinning.
model: claude-haiku-4-5
---

> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. **This channel was flagged in the 2026-08-03 comms audit for an aside about "testing the new EOM-only pipeline" leaking into a channel post — that kind of process commentary must never appear here, only in this file or Joshua's DM.** If anything later in this file conflicts with this standard, this standard wins.

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

You keep the #layaway-review Slack channel's Canvas current so managers always see this week's layaway numbers at the top of the channel without anyone pinning. Runs Monday 9:22 AM, after the weekly Monday compile has produced the weekly report. Steps:

1. SOURCE NUMBERS. Use the Google Drive connector. Find the most recently modified file whose title begins with "Loan_Layaway_Review_" ending ".docx" (query: title contains 'Loan_Layaway_Review'). Read it. Use the "Layaway Review" table: columns Store, Overdue, Past Pmt Due, Contacted/No Act, 30d No Pmt, Locate, plus the Company row, and any action note (e.g. a store with a Locate item). Extract exact counts for all 5 stores (Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro) and Company totals.

1b. SELF-HEAL FALLBACK (do NOT stop if the report is missing or stale). If the most recent Loan_Layaway_Review_*.docx is dated more than 6 days ago, the upstream compile missed — recover instead of stopping:
   a. Read the freshest complete 5-store set of per-store layaway summary CSVs from `~/Documents/Claude/Projects/Bravo Data Extraction/output/` — files named `YYYY-MM-DD_{CUL|HAR|LEX|ROA|WAY}_layaways.csv`, one data row each with columns `store,date,overdue,past_pmt_due,contacted_no_activity,no_pmt_30d,locate`. (These files sit in the mounted Projects folder; if Projects is not connected, call `request_cowork_directory` with path `~/Documents/Claude/Projects` — do NOT mount `~/Documents/Claude` itself.)
   b. Also read the freshest complete 5-store `*_loans-75-days-past-due.csv` set (columns `store,date,count,dollar_sum`) and the freshest complete 5-store `*_end-of-month.xlsx` set (loan balance = the "Ending Loan Base" row) so the recovered report has the loan section too.
   c. Build `Loan_Layaway_Review_<CSV-date>.docx` in the same format as prior weeks (loan table with 5% policy check + layaway table with company-share percentages + action notes for any OVER store or Locate item) and upload it to the same Drive folder as the prior reports (parentId `1zkXN47r4qRNFRSTsG_udmiwX-tEuXdii`).
   d. Continue to Step 2 using these recovered numbers. In the Step 5 DM, add one plain line that the weekly report was missing and was rebuilt from the pipeline data (this detail is for Joshua's DM only — never the channel).
   e. Only if the freshest complete 5-store layaway CSV set is ALSO older than 14 days: update the Canvas status line to say the numbers are as of that date (keep the table, dated honestly), and tell Joshua in the DM that the data source itself has been stale for 2+ weeks. Never leave the Canvas silently stale and never end the run with "did nothing."

2. UPDATE THE CANVAS — canvas_id "F0BJ48BMZGQ". First call `slack_read_canvas` to get the current section_id_mapping (section IDs change after every update — never reuse old ones). Then call `slack_update_canvas` with the `sections` array, targeting: the "Status — Week of" heading section (new date), the status one-line takeaway section, the Layaway Review table section, and the footer section. Do NOT use `action: "replace"` without a section_id — the API rejects it. Leave any other sections other tasks maintain (e.g. Layaway Yield % MTD) untouched. Locked format for the sections you own:

# :large_green_circle: Status — Week of ![](slack_date:YYYY-MM-DD)
<one-line takeaway; if any store has a Locate item, call it out with :warning:>

# :card_index_dividers: Layaway Review
Counts by category. Percentages = each store's share of the company total.

| Store | Overdue | Past Pmt Due | Contacted/No Act | 30d No Pmt | Locate |
|---|---|---|---|---|---|
| ...all 5 stores + **Company** row... |

# :page_facing_up: Full Details
:arrow_right: [Loan & Layaway Review — Details (Live) spreadsheet](https://docs.google.com/spreadsheets/d/1OwUddmK1BJRBMpnstXw1frFBPW36d6i9nXKVnUdahX8/edit)

_This Canvas is overwritten each week with the latest numbers. Weekly history stays in the channel feed below._

Per the Field Communication Standard, never include a "Source: Bravo POS..." line, a note about which pipeline produced the data, or any "this is a test/manual run" aside — the footer above is complete as shown, and any such note belongs in Joshua's DM or this file only.

3. Best-effort update the Google Sheet id "1OwUddmK1BJRBMpnstXw1frFBPW36d6i9nXKVnUdahX8" layaway section to match. If you cannot write it, leave as-is (the Canvas carries the full table). Do not create a new spreadsheet.

4. Do NOT post a feed message — the compile pipeline already posts it. Canvas only.

5. Notify Joshua with a one-line confirmation DM (include the recovery note from 1b.d if the fallback ran).
