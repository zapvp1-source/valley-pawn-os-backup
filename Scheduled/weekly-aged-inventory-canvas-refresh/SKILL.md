---
name: weekly-aged-inventory-canvas-refresh
description: Monday 9:26 AM — overwrite the #aged-inventory-review Slack Canvas from the latest per-store aged-inventory CSVs so it stays at the top, no manual pinning.
---

> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. If anything later in this file conflicts with this standard, this standard wins.

You keep the #aged-inventory-review Slack channel's Canvas current so managers always see this week's aged-inventory picture at the top without anyone pinning. Runs Monday 9:26 AM, after the weekly Monday compile runs. Steps:

1. SOURCE NUMBERS. Use the Google Drive connector. Find the 5 most recent files (one per store) whose titles match "YYYY-MM-DD_<STORE>_aged-inventory-summary.csv" for the latest date, where STORE is CUL, HAR, LEX, ROA, WAY (query: title contains 'aged-inventory-summary'; take the newest date present for all 5). Read each. In each file, use the "Subtotals:" row, which gives merchandise totals across age buckets: Price (total inv retail), and the age-bucket columns <6mo, 6mo-1yr, 1yr-18mo, 18mo-2yr, 2yr-3yr, >3yr. For each store compute: Total Inv (Price) = Subtotals Price; <6mo; 6mo-1yr; Aged 1yr+ = sum of (1yr-18mo + 18mo-2yr + 2yr-3yr + >3yr); % Aged = Aged 1yr+ / Total Inv (Price). Compute Company totals by summing across the 5 stores. If fewer than 5 current-date store files exist, STOP and do nothing.

2. OVERWRITE THE CANVAS. Use Slack tool slack_update_canvas with canvas_id "F0BHDL6AULU", action "replace", NO section_id. Rebuild in this locked format (round dollars to whole numbers, one decimal on %), substituting the as-of date and numbers:

# :large_green_circle: Status — as of ![](slack_date:YYYY-MM-DD)
Company aged inventory (1yr+) is **X.X%** of on-hand retail value.
:warning: <name the store with the highest % aged and the leanest>

# :bar_chart: Aged Inventory by Store
Retail value by age. "Aged 1yr+" = everything older than one year.

| Store | Total Inv (Price) | <6mo | 6mo–1yr | Aged 1yr+ | % Aged |
|---|---|---|---|---|---|
| ...all 5 stores + **Company** row... |

# :page_facing_up: Full Details
:arrow_right: [Aged Inventory — Details (Live) spreadsheet](https://docs.google.com/spreadsheets/d/1aEatyu3YMfJcjIfcaIVHU9Lq8jOUtpH0Jd77LGDdvPM/edit)

_This Canvas is overwritten each week with the latest numbers. Weekly history stays in the channel feed below._

Per the Field Communication Standard, do not include a "Source: Bravo POS..." or similar system-name line in the Canvas — the footer above is complete as shown.

3. Best-effort update the Google Sheet id "1aEatyu3YMfJcjIfcaIVHU9Lq8jOUtpH0Jd77LGDdvPM" to match. If you cannot write it, leave as-is (the Canvas carries the full table). Do not create a new spreadsheet.

4. Do NOT post a feed message — the compile pipeline already posts it. Canvas only.

5. Notify Joshua with a one-line confirmation, or say so if you stopped because current files were not found.