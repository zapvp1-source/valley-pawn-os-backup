---
name: weekly-layaway-review-canvas-refresh
description: Monday 9:22 AM — overwrite the #layaway-review Slack Canvas from the latest pipeline output so it stays at the top, no manual pinning.
model: claude-haiku-4-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, do NOT message Joshua, Preston, or anyone else, in any medium. Instead append ONE row to the fleet failure ledger `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` (use `mcp__Control_your_Mac__osascript` `do shell script "printf ... >> file"` if file tools cannot reach it) in exactly this form: `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or: yes, <the single thing only Joshua can do>> | OPEN |`. The `fleet-guardian` task reads this ledger twice a day, re-runs whatever is safe to re-run, rolls anything that truly needs Joshua into `Life OS/HUMAN_QUEUE.md`, and sends Joshua at most ONE consolidated plain-language DM per day. Individual tasks never DM about failures. All technical detail goes in the run output/log/STATUS file for the next Claude session to pick up. Never send failure notices to any team channel, store manager, employee, or Preston. FIELD COMMUNICATION RULE (unchanged): anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This v3 supersedes both the v2 one-line-DM rule and any older rule in this file.
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


## Final step (MANDATORY) — write the publication receipt

This task publishes to a surface with no readable history (a DM or a Slack canvas), so this receipt
is the ONLY evidence the task ran and delivered. Without it, a healthy run and a dead task are
indistinguishable in the fleet audit, and this task will read as AWAITING RECEIPTS forever.

Run this as the LAST action of the task, only after the publication actually succeeded:

```bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_receipt.py" write weekly-layaway-review-canvas-refresh \
  --surface canvas --target "F0BJ48BMZGQ" --note "<first line of what you published>"
```

Rules:
- Write it ONLY on a real, confirmed send. Never write a receipt for something you did not publish.
- If the task is silent by design this run (nothing to report), still write the receipt, with
  `--note "checked, nothing to report"`. Recording the look is what makes the silence trustworthy.
- If the publication FAILED, write it with `--ok false` and the reason in `--note`. Do not post the
  failure to Slack (Rule 16).


## Precondition (MANDATORY) — FLEET PUBLISH GUARD

Before publishing ANYTHING — a channel post, a DM to Joshua, a DM to a store manager, a canvas
refresh, an email, a Facebook post — check whether the fleet publish guard is armed:

```bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_dryrun.py" status
```

Exit code 0 means **ARMED**. When it is armed:

- Do the ENTIRE task for real — same pull, same data, same compile, same message text. The point is
  to test the task, not to skip it.
- Publish NOTHING. Not to a channel, not to a DM, not to a manager, not to a canvas, not anywhere.
- Instead write exactly what you would have published to
  `Valley Pawn OS/fleet/test_output/<task-name>-<YYYYMMDD-HHMMSS>.txt`, with a first line naming the
  channel or person it would have gone to.
- Do NOT write a normal publication receipt. A diverted run is not evidence that the task delivered,
  and recording it as one would corrupt the fleet audit.
- Say clearly in your final summary that the guard was armed and nothing was published.

Exit code 1 means not armed — run and publish normally.

This guard is ENFORCED for native scripts (they all publish through `vp_slack.py`, which intercepts
them). A Cowork task like this one has no such chokepoint, so here the guard is only as good as this
instruction. Honour it exactly. The guard always carries an expiry and disarms itself, so a stale
flag can never silence this task indefinitely.
