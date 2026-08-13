---
name: nics-monthly-ranking
description: 1st of each month, 9:30 AM: pull the prior full month's FFL transfers for all 5 stores from Bravo, rank stores by transfers + revenue, and post the monthly ranking to #ffl-transfer-performance.
---

Monthly (1st-of-month) FFL transfer ranking for the PRIOR full month, RANKED BY REVENUE: pull all 5 stores, rank by revenue, post to #ffl-transfer-performance, AND update the Google Drive trend report in place. BOUNDED — reuse the pipeline; do not modify the handler, do not touch the display, do not re-enable scrap.

CONTEXT: Read skills enterprise-map, valley-pawn-context, bravo-context. Bravo folder access via mcp__Control_your_Mac__osascript `do shell script` only. PROJECT: /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction (=<DIR>). CSVs: <DIR>/output/<start>_to_<end>_<STORE>_nics-transfers.csv. Stores WAY,CUL,HAR,LEX,ROA.

STEP 0 — dates (python): PRIOR calendar month. start=1st of prior month, end=last day of prior month (calendar.monthrange; handle Jan year-rollover). YYYY-MM-DD.

STEP 1 — contention guard: watcher idle (no <DIR>/logs/*.log modified ~2 min; nothing in triggers/ or triggers/claimed). If busy, wait up to 10 min; if still busy, DM Joshua (U03BB52MDSA) and skip.

STEP 2 — pull: drop ONE trigger nics-month-<ts>.json, reports [{"name":"nics-transfers","stores":["WAY","CUL","HAR","LEX","ROA"],"date":"<start>..<end>"}]. Poll ~12-15 min. Verify all 5 store CSVs exist; re-run any missing store ONCE. A store that legitimately returns 0 is valid data — label "pending" ONLY on an actual error/no-csv, never treat a real 0 as failure.

STEP 3 — tally + RANK BY REVENUE: per store COUNT = data rows, REVENUE = sum of Amount (last field; python csv for quoted commas). Rank stores by REVENUE descending (transfer count as tiebreak).

STEP 4 — post to Slack #ffl-transfer-performance (C0BPH5T1NFL): markdown table "FFL Transfers — <Month YYYY> (final)" with columns Rank | Store | Revenue | Transfers, rows ordered by revenue, + company Total, one line on the revenue leader/laggard, plus the trend sheet URL (below). If a store is pending, say so. If the pull wholly failed, DM Joshua instead of posting.

STEP 5 — update the Drive trend report IN PLACE (use the shared sheets helper, NOT the Drive create_file connector): run `/usr/bin/python3 "<DIR>/ffl_trend_sync.py"`. It rebuilds every COMPLETE month from the raw CSVs and upserts keyed by Month into "Valley Pawn - FFL Transfer Trend (Monthly)" (id 1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs, tab Monthly) — same sheet each month, in place. Print its output. Sheet URL: https://docs.google.com/spreadsheets/d/1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs/edit

Never present partial data as complete. Done after this run.