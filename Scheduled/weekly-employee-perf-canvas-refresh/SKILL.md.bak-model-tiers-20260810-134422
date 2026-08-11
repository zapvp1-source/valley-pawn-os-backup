---
name: weekly-employee-perf-canvas-refresh
description: Monday 9:24 AM — overwrite the #employee-performance Slack Canvas from the latest employee sales rankings so it stays at the top, no manual pinning.
---

> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. If anything later in this file conflicts with this standard, this standard wins.

You keep the #employee-performance Slack channel's Canvas current so the team always sees this week's MTD sales leaderboard at the top without anyone pinning. Runs Monday 9:24 AM, after the weekly Monday compile runs. Steps:

1. SOURCE NUMBERS. Use the Google Drive connector. Find the most recently modified file whose title begins with "employee-sales-rankings-" ending ".xlsx" (query: title contains 'employee-sales-rankings'). Read it. It lists each employee, their store(s), and Total (Retail Sales Excluding Fees) for the MTD period, plus a Company Total row and the period dates. Build the RANKED view: exclude any employee with $0.00 total and exclude Preston Peters (he is ownership, shown only in the company total). Rank the rest high to low.

2. OVERWRITE THE CANVAS. Use Slack tool slack_update_canvas with canvas_id "F0BH9UK284S", action "replace", NO section_id. Rebuild in this locked format, substituting the period end date, the ranked rows, and the company total:

# :bar_chart: MTD Employee Sales — as of ![](slack_date:YYYY-MM-DD)
Retail sales excluding fees. Period: <period>.
:trophy: <one-line takeaway: who leads, and which store total is strongest>

# :1234: Ranked Leaderboard

| # | Employee | Store | Retail Sales (excl. fees) |
|---|---|---|---|
| :first_place_medal: / :second_place_medal: / :third_place_medal: then 4,5,6... | ... | ... | ... |

_Company total (incl. Preston): **$XX,XXX.XX**_

# :page_facing_up: Full Details
:arrow_right: [Employee Sales Rankings — Details (Live) spreadsheet](https://docs.google.com/spreadsheets/d/1--Kn_2ybJCf6_PGnTdyMjCHBDsoEM4iCYPtokjHRIsg/edit)

_This Canvas is overwritten each week with the latest numbers. Weekly history stays in the channel feed below._

Per the Field Communication Standard, do not include a "Source: Bravo POS..." or similar system-name line in the Canvas — the footer above is complete as shown.

3. Best-effort update the Google Sheet id "1--Kn_2ybJCf6_PGnTdyMjCHBDsoEM4iCYPtokjHRIsg" to match this week's ranked list. If you cannot write it, leave as-is (the Canvas carries the full table). Do not create a new spreadsheet.

4. Do NOT post a feed message — the compile pipeline already posts it. Canvas only.

5. Notify Joshua with a one-line confirmation, or say so if you stopped because no current file was found.