---
name: nics-weekly-mtd-ranking
description: Every Monday 9:30 AM: pull month-to-date FFL transfers for all 5 stores from Bravo, rank stores by transfers + revenue, and post the MTD ranking to #ffl-transfer-performance.
---

Weekly MONTH-TO-DATE FFL transfer ranking. Pull MTD nics-transfers for all 5 stores, rank, and post to #ffl-transfer-performance. BOUNDED — reuse the existing pipeline; do not modify the handler, do not touch the display, do not re-enable scrap.

CONTEXT: Read skills enterprise-map, valley-pawn-context, bravo-context. Bravo Data Extraction folder access is via mcp__Control_your_Mac__osascript `do shell script` only. PROJECT: /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction. Output CSVs: <DIR>/output/<start>_to_<end>_<STORE>_nics-transfers.csv. Stores: WAY,CUL,HAR,LEX,ROA.

STEP 0 — dates. Compute (python) the MTD range: start = first day of the CURRENT month, end = TODAY. Format YYYY-MM-DD.

STEP 1 — contention guard. Confirm the watcher is idle (no <DIR>/logs/*.log modified in ~2 min; no active nics run; check <DIR>/triggers and triggers/claimed for anything in flight). If busy, wait up to 10 min, re-check; if still busy, DM Joshua (U03BB52MDSA) that it was busy and skip this week.

STEP 2 — pull. Drop ONE trigger into <DIR>/triggers/ named nics-mtd-<ts>.json with reports [{"name":"nics-transfers","stores":["WAY","CUL","HAR","LEX","ROA"],"date":"<start>..<end>"}]. Poll for completion (each store ~2 min; total ~12-15 min). After it finishes, verify all 5 store CSVs for this range exist. Re-run any missing store ONCE (single-store trigger, store-first). If a store still fails, label it "pending" — never imply zero.

STEP 3 — tally + rank. Per store: transfer COUNT = data rows; REVENUE = sum of the Amount column (last field; parse with python csv to handle quoted commas). Rank stores by transfers (revenue as tiebreak).

STEP 4 — post to Slack channel #ffl-transfer-performance (id C0BPH5T1NFL): a markdown table titled "FFL Transfers — Month-to-Date (<Month> 1–<day>)" ranked by store with Transfers + Revenue columns and a company Total row. One line calling out the current leader and any store at 0/low. If any store is pending/failed, say so explicitly. Keep it concise. Do NOT post if the pull wholly failed — instead DM Joshua what went wrong.

Never post partial data as complete. When done you are finished for this run.