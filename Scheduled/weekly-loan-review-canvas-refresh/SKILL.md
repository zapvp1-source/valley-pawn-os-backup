---
name: weekly-loan-review-canvas-refresh
description: Monday 9:20 AM — overwrite the #loan-review Slack Canvas (current-week view) from the latest pipeline output so it always stays at the top, no manual pinning.
model: claude-haiku-4-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, do NOT message Joshua, Preston, or anyone else, in any medium. Instead append ONE row to the fleet failure ledger `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` (use `mcp__Control_your_Mac__osascript` `do shell script "printf ... >> file"` if file tools cannot reach it) in exactly this form: `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or: yes, <the single thing only Joshua can do>> | OPEN |`. The `fleet-guardian` task reads this ledger twice a day, re-runs whatever is safe to re-run, rolls anything that truly needs Joshua into `Life OS/HUMAN_QUEUE.md`, and sends Joshua at most ONE consolidated plain-language DM per day. Individual tasks never DM about failures. All technical detail goes in the run output/log/STATUS file for the next Claude session to pick up. Never send failure notices to any team channel, store manager, employee, or Preston. FIELD COMMUNICATION RULE (unchanged): anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This v3 supersedes both the v2 one-line-DM rule and any older rule in this file.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. If anything later in this file conflicts with this standard, this standard wins.

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
You keep the #loan-review Slack channel's Canvas current so managers always see this week's numbers at the top of the channel without anyone pinning a message. This runs Monday at 9:20 AM, after the weekly Monday compile (which fires earlier Monday morning) has produced the weekly loan/layaway report. Do the following:

1. SOURCE THE LATEST NUMBERS. Use the Google Drive connector. Search for the most recently modified file whose title begins with "Loan_Layaway_Review_" and ends in ".docx" (query: title contains 'Loan_Layaway_Review'). Read its content. It contains two tables plus a status line: (a) "Past-Due Loans (75-Day Rule)" with columns Store, Items 75+ Days, $ Past Due, % of Loan Bal, Status; and (b) "Layaway Review" with columns Store, Overdue, Past Pmt Due, Contacted/No Act, 30d No Pmt, Locate; plus a Company total row for each, the "as of" balance date, and any action note (e.g. a store with a Locate layaway). Extract the exact numbers for all 5 stores (Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro) and the Company totals. If no Loan_Layaway_Review_*.docx exists for the current week, STOP and do nothing (do not post stale data).

2. OVERWRITE THE CANVAS. Use the Slack connector tool slack_update_canvas with canvas_id "F0BH6BJ0PK7", action "replace", and NO section_id (this replaces the entire canvas). Rebuild it in exactly this locked format, substituting the extracted numbers and the report's week/date and balance-as-of date. Keep the Full Details link exactly as shown:

# :large_green_circle: Status — Week of ![](slack_date:YYYY-MM-DD)
<one-line takeaway: how many of 5 stores are within the 5% policy, and any action item such as a Locate layaway. If any store is OVER 5%, use :red_circle: in the heading instead of :large_green_circle: and name the store.>

# :bar_chart: Past-Due Loans (75-Day Rule)
Policy cap: 5% of store loan balance. Balances as of <balance date>.

| Store | Items 75+d | $ Past Due | % of Loan Bal | Status |
|---|---|---|---|---|
| Culpeper | ... |
| Harrisonburg | ... |
| Lexington | ... |
| Roanoke | ... |
| Waynesboro | ... |
| **Company** | ... |

(use :white_check_mark: for stores within 5%, :red_circle: for any over)

# :card_index_dividers: Layaway Review

| Store | Overdue | Past Pmt Due | Contacted/No Act | 30d No Pmt | Locate |
|---|---|---|---|---|---|
| ...all 5 stores + **Company** row... |

# :page_facing_up: Full Details
:arrow_right: [Loan & Layaway Review — Details (Live) spreadsheet](https://docs.google.com/spreadsheets/d/1OwUddmK1BJRBMpnstXw1frFBPW36d6i9nXKVnUdahX8/edit)

_This Canvas is overwritten each week with the latest numbers. Weekly history stays in the channel feed below._

Per the Field Communication Standard, do not include a "Source: Bravo POS..." or similar system-name line in the Canvas — the footer above is complete as shown.

3. UPDATE THE DETAILS SPREADSHEET (best-effort). Using the Google Drive connector, update the Google Sheet with id "1OwUddmK1BJRBMpnstXw1frFBPW36d6i9nXKVnUdahX8" so its Past-Due Loans and Layaway tables match this week's numbers and the "Week of" date. If you cannot write to the existing sheet, leave it as-is — the Canvas already carries the full tables, so no data is lost. Do not create a new spreadsheet.

4. DO NOT post a new message to the channel feed — the compile pipeline already posts the weekly feed message. Your only job is the Canvas (and best-effort the sheet). Keep the channel quiet otherwise.

5. Notify Joshua with a one-line confirmation of what you updated (e.g. "Refreshed #loan-review Canvas for week of Jul 20 — all 5 stores within policy"). If you stopped because no current report was found, say so.