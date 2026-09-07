---
name: weekly-employee-perf-canvas-refresh
description: Monday 9:24 AM — overwrite the #employee-performance Slack Canvas from the latest employee sales rankings so it stays at the top, no manual pinning.
model: claude-haiku-4-5
---

> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. If anything later in this file conflicts with this standard, this standard wins.

You keep the #employee-performance Slack channel's Canvas current so the team always sees this week's MTD sales leaderboard at the top without anyone pinning. Runs Monday 9:24 AM, after the weekly Monday compile runs. Steps:

1. SOURCE NUMBERS. Use the Google Drive connector. Find the most recently modified file whose title begins with "employee-sales-rankings-" ending ".xlsx" (query: title contains 'employee-sales-rankings'). Read it. It lists each employee, their store(s), and Total (Retail Sales Excluding Fees) for the MTD period, plus a Company Total row and the period dates.

**STALENESS CHECK (added 2026-08-21 — do not skip).** Before using this file, confirm it is genuinely current: its `createdTime`/`modifiedTime` should be within the last ~8 days (this task runs weekly, right after Monday's compile), and its contents should include a period/date header and a Company Total row (a bare rank list with no period line is a malformed partial export — treat it as stale even if the date looks recent). If the file is stale or malformed:

**SELF-HEAL — do not just alert (added 2026-08-21, replacing the old alert-and-stop behavior).** A 2026-08-21 incident found this file 18 days stale (3 missed weekly cycles) because of an upstream bug in `monday-bravo-combined-run`/`monday-bravo-combined-compile` (since fixed — see those tasks' SKILL.md changelogs, and the new `monday-bravo-part1-watchdog` safety net). Rather than repeat "detect stale data, DM Joshua, stop" every time some upstream link breaks, pull fresh numbers directly:
  a. Consult the `bravo-context` skill's Mandatory Contention & Scheduling-Safety Check first (`_bravo_foreground_guard.sh check` equivalent: confirm `triggers/claimed/` is empty of anything stuck and no other Bravo-touching scheduled task is firing in the next ~20 min). If BUSY, wait up to ~15 minutes and re-check once; if still busy, fall through to the DM-and-stop path below.
  b. If clear, drop a new trigger at `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/employee-perf-refresh-<TODAY>.json` (via `mcp__Control_your_Mac__osascript`, loading it first via ToolSearch if deferred):
     ```json
     {"id": "employee-perf-refresh-<TODAY>", "requested_at": "<TODAY>T<HH:MM:SS>-04:00", "reports": [{"name": "employee-activity", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "<FIRST_OF_MONTH>"}]}
     ```
  c. Poll `triggers/processed/` and `results/employee-perf-refresh-<TODAY>.result.json` in ≤18s increments (osascript calls time out ~25s) for up to ~15 minutes.
  d. Once all 5 cells succeed, read `output/<FIRST_OF_MONTH>_<STORE>_employee-activity.csv` for each store directly (same osascript file-read path) instead of the Drive spreadsheet. Parse per store: skip `Total Store`, `SYSTEM`, `FREE1 - FREE1 VALLEY PAWN` (a generic/shared-login bucket, not a real employee — historically never appears in this ranking; if its total is unusually large, note that once in the Joshua DM at the end as a data-quality flag, but never in the Canvas), and `Report printed on...`. Parse employee name as everything after the first `' - '`. Capture `Retail Sales Excluding Fees` as the metric. Aggregate by employee name across stores (multi-store employees shown as `STORE1+STORE2+...`), using the Total Store row's Retail Sales Excluding Fees per store summed for the Company Total.
  e. Proceed to Step 2 below using this freshly-pulled data instead of the Drive file. In your end-of-run Joshua DM, note one line that the source was a direct on-demand pull because the Drive file was stale, and why (in plain terms, e.g. "the usual Monday pull hadn't produced this week's numbers yet").
  f. Only if the self-heal trigger does NOT complete within ~15 minutes, or the contention check stays BUSY: DM Joshua the standard one-line failure alert per the policy above and stop. Do NOT post stale/malformed data to the Canvas under a current date.

Build the RANKED view: exclude any employee with $0.00 total and exclude Preston Peters (he is ownership, shown only in the company total). Rank the rest high to low.

2. OVERWRITE THE CANVAS. Use Slack tool slack_update_canvas with canvas_id "F0BH9UK284S". Read the canvas first with slack_read_canvas to get current section IDs, then submit a `sections` batch replacing each body section (leave the title/heading-only sections like "Ranked Leaderboard" and "Full Details" untouched unless their text needs to change). Rebuild in this locked format, substituting the period end date, the ranked rows, and the company total:

# :bar_chart: MTD Employee Sales — as of ![](slack_date:YYYY-MM-DD)
Retail sales excluding fees. Period: <period>.
:trophy: <one-line takeaway: who leads, and which store total is strongest>

# :1234: Ranked Leaderboard

| # | Employee | Store | Retail Sales (excl. fees) |
|---|---|---|---|
| :first_place_medal: / :second_place_medal: / :third_place_medal: then 4th,5th,6th... | ... | ... | ... |

_Company total (incl. Preston): **$XX,XXX.XX**_

# :page_facing_up: Full Details
:arrow_right: [Employee Sales Rankings — Details (Live) spreadsheet](https://docs.google.com/spreadsheets/d/1--Kn_2ybJCf6_PGnTdyMjCHBDsoEM4iCYPtokjHRIsg/edit)

_This Canvas is overwritten each week with the latest numbers. Weekly history stays in the channel feed below._

Per the Field Communication Standard, do not include a "Source: Bravo POS..." or similar system-name line in the Canvas — the footer above is complete as shown.

3. Best-effort update the Google Sheet id "1--Kn_2ybJCf6_PGnTdyMjCHBDsoEM4iCYPtokjHRIsg" to match this week's ranked list. If you cannot write it, leave as-is (the Canvas carries the full table). Do not create a new spreadsheet.

4. Do NOT post a feed message — the compile pipeline already posts it. Canvas only.

5. Notify Joshua with a one-line confirmation (note if the self-heal path was used), or say so if you stopped because no current file was found and the self-heal also could not complete.
