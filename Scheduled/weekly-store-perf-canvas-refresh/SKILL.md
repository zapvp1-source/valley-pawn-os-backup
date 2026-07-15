---
name: weekly-store-perf-canvas-refresh
description: Monday 9:28 AM — overwrite the #store-performance Slack Canvas from the latest weekly store KPI files so it stays at the top, no manual pinning.
---

You keep the #store-performance Slack channel's Canvas current so managers always see this week's store rankings at the top without anyone pinning. Runs Monday 9:28 AM, after the monday-bravo-combined-compile pipeline runs. Steps:

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

_This Canvas is overwritten each week with the latest numbers. Weekly history stays in the channel feed below. Source: Bravo POS Monday combined run._

3. Best-effort update the Google Sheet id "1vpcnbR6V4YGHIrqP8GpHDL5LcciekDPA_Dq6FOHbCts" to match this week's Key Metrics grid and overall ranking. If you cannot write it, leave as-is (the Canvas carries the full grid). Do not create a new spreadsheet.

4. Do NOT post a feed message — the compile pipeline already posts the weekly rankings. Canvas only.

5. Notify Joshua with a one-line confirmation, or say so if you stopped because no current files were found.