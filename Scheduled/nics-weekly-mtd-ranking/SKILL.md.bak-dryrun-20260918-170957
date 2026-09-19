---
name: nics-weekly-mtd-ranking
description: Every Monday 9:30 AM: pull month-to-date FFL transfers for all 5 stores from Bravo, rank stores by transfers + revenue, and post the MTD ranking to #ffl-transfer-performance.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Weekly MONTH-TO-DATE FFL transfer ranking, RANKED BY REVENUE. Pull MTD nics-transfers for all 5 stores, rank by revenue, post to #ffl-transfer-performance. BOUNDED — reuse the pipeline; do not modify the handler, do not touch the display, do not re-enable scrap.

CONTEXT: Read skills enterprise-map, valley-pawn-context, bravo-context. Bravo folder access via mcp__Control_your_Mac__osascript `do shell script` only. PROJECT: /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction (=<DIR>). CSVs: <DIR>/output/<start>_to_<end>_<STORE>_nics-transfers.csv. Stores WAY,CUL,HAR,LEX,ROA.

STEP 0 — dates (python): MTD range: start = first day of CURRENT month, end = TODAY. YYYY-MM-DD.

STEP 1 — MAKE BRAVO READY, then guard. (a) Contention: confirm nothing is mid-run (no <DIR>/logs/*.log modified in ~2 min; nothing in <DIR>/triggers or triggers/claimed). If busy, wait up to 10 min. (b) RECOVER Bravo to a logged-in dashboard (this is the piece that was missing — a logged-out Bravo aborts the pull): run `do shell script "B='<DIR>'; rm -f \"$B/logs/_health_gate_status.txt\"; nohup bash \"$B/bravo_health_gate.sh\" WAY >/dev/null 2>&1 & echo started"`, then poll <DIR>/logs/_health_gate_status.txt every ~25s for up to ~4 min until a line starting `PASS` appears. If it never PASSes, DM Joshua (U03BB52MDSA) "weekly FFL ranking: Bravo wasn't reachable, skipping this week" and STOP (do not post).

STEP 2 — pull: drop ONE trigger nics-mtd-<ts>.json, reports [{"name":"nics-transfers","stores":["WAY","CUL","HAR","LEX","ROA"],"date":"<start>..<end>"}]. Poll ~12-15 min. Verify all 5 store CSVs for the range exist; re-run any missing store ONCE (single-store trigger). A store that legitimately returns 0 for the period is valid data — label a store "pending" ONLY if its pull errored/produced no csv, never treat a real 0 as failure.

STEP 3 — tally + RANK BY REVENUE: per store COUNT = data rows, REVENUE = sum of Amount column (last field; python csv for quoted commas). Rank stores by REVENUE descending (transfer count tiebreak).

STEP 4 — post to Slack #ffl-transfer-performance (id C0BPH5T1NFL): markdown table titled "FFL Transfers — Month-to-Date (<Month> 1–<day>)" with columns Rank | Store | Revenue | Transfers, rows ordered by revenue, + company Total. One line on the revenue leader/laggard. If a store is pending, say so. If the pull wholly failed, DM Joshua instead of posting.

Never present partial data as complete. Done after this run.