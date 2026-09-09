---
name: weekly-store-perf-canvas-refresh
description: Monday 9:28 AM — overwrite the #store-performance Slack Canvas from the latest weekly store KPI files so it stays at the top, no manual pinning.
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
You keep the #store-performance Slack channel's Canvas current so managers always see this week's store rankings at the top without anyone pinning. Runs Monday 9:28 AM, after the weekly store-KPI compile runs. Steps:

1. SOURCE NUMBERS. Use the Google Drive connector. Find the newest pair of files titled "YYYY-MM-DD_store_kpis_msg1.txt" and "YYYY-MM-DD_store_kpis_msg2.txt" for the latest date (query: title contains 'store_kpis'). Read both. msg1 has the overall rankings (each store's Avg Rank and category wins, plus a quick summary and the report period date). msg2 has "Full Category Rankings" — per-store dollar figures for: Loan Balance, Inventory Balance, Total Assets, Retail Sales, Pawn Service Charges, Scrap Sales, Layaway Balance, Net Revenue MTD, and Company Totals. Extract for all 5 stores (Culpeper, Harrisonburg, Roanoke, Waynesboro, Lexington). If no current-week store_kpis files exist, STOP and do nothing.

2. OVERWRITE THE CANVAS. Use Slack tool slack_update_canvas with canvas_id "F0BH6S9U5FX", action "replace", NO section_id. Rebuild in this locked format. Lead with the overall ranking line + a one-line takeaway, then a single consolidated "Key Metrics by Store" table (do NOT reproduce 8 separate lists — consolidate into one grid). Round dollars to whole numbers. Columns: Store, Loan Bal, Inv Bal, Retail Sales, PSC, Layaway Bal, Net Rev MTD, plus a bold Company row.

# :trophy: Overall Rankings — MTD as of ![](slack_date:YYYY-MM-DD)
<ranked list of 5 stores with avg rank + category wins, using :1st_place_medal: :2nd_place_medal: :3rd_place_medal: then 4th/5th>
:bulb: <one-line takeaway: who leads and why, and the focus/watch store>

# :bar_chart: Key Metrics by Store

| Store | Loan Bal | Inv Bal | Retail Sales | PSC | Layaway Bal | Net Rev MTD |
|---|---|---|---|---|---|---|
| ...5 stores + **Company** row... |

_Category leaders: Retail Sales -> <store> · PSC & Net Rev -> <store> · Loan/Inv/Layaway -> <store>. Note scrap if $0._

# :page_facing_up: Full Details
:arrow_right: [Store Performance Rankings — Details (Live) spreadsheet](https://docs.google.com/spreadsheets/d/1vpcnbR6V4YGHIrqP8GpHDL5LcciekDPA_Dq6FOHbCts/edit)

_This Canvas is overwritten each week with the latest numbers. Weekly history stays in the channel feed below._

Per the Field Communication Standard, do not include a "Source: Bravo POS..." or similar system-name line in the Canvas — the footer above is complete as shown.

3. Best-effort update the Google Sheet id "1vpcnbR6V4YGHIrqP8GpHDL5LcciekDPA_Dq6FOHbCts" to match this week's Key Metrics grid and overall ranking. If you cannot write it, leave as-is (the Canvas carries the full grid). Do not create a new spreadsheet.

4. Do NOT post a feed message — the compile pipeline already posts the weekly rankings. Canvas only.

5. Notify Joshua with a one-line confirmation, or say so if you stopped because no current files were found.