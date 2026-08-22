---
name: weekly-store-perf-canvas-refresh
description: Monday 9:28 AM — overwrite the #store-performance Slack Canvas from the latest weekly store KPI files so it stays at the top, no manual pinning.
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. If anything later in this file conflicts with this standard, this standard wins.

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