---
name: nics-monthly-ranking
description: 1st of each month, 9:30 AM: pull the prior full month's FFL transfers for all 5 stores from Bravo, rank stores by transfers + revenue, and post the monthly ranking to #ffl-transfer-performance.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Monthly (1st-of-month) FFL transfer ranking for the PRIOR full month, RANKED BY REVENUE: pull all 5 stores, rank by revenue, post to #ffl-transfer-performance, AND update the Google Drive trend report in place. BOUNDED — reuse the pipeline; do not modify the handler, do not touch the display, do not re-enable scrap.

CONTEXT: Read skills enterprise-map, valley-pawn-context, bravo-context. Bravo folder access via mcp__Control_your_Mac__osascript `do shell script` only. PROJECT: /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction (=<DIR>). CSVs: <DIR>/output/<start>_to_<end>_<STORE>_nics-transfers.csv. Stores WAY,CUL,HAR,LEX,ROA.

STEP 0 — dates (python): PRIOR calendar month. start=1st of prior month, end=last day of prior month (calendar.monthrange; handle Jan year-rollover). YYYY-MM-DD.

STEP 1 — MAKE BRAVO READY, then guard. (a) Contention: nothing mid-run (no <DIR>/logs/*.log modified ~2 min; nothing in triggers/ or triggers/claimed). If busy, wait up to 10 min. (b) RECOVER Bravo to a logged-in dashboard (a logged-out Bravo aborts the pull): `do shell script "B='<DIR>'; rm -f \"$B/logs/_health_gate_status.txt\"; nohup bash \"$B/bravo_health_gate.sh\" WAY >/dev/null 2>&1 & echo started"`, then poll <DIR>/logs/_health_gate_status.txt every ~25s up to ~4 min for a line starting `PASS`. If it never PASSes, DM Joshua (U03BB52MDSA) "monthly FFL ranking: Bravo wasn't reachable, skipping" and STOP.

STEP 2 — pull: drop ONE trigger nics-month-<ts>.json, reports [{"name":"nics-transfers","stores":["WAY","CUL","HAR","LEX","ROA"],"date":"<start>..<end>"}]. Poll ~12-15 min. Verify all 5 store CSVs; re-run any missing store ONCE. A legitimate 0 is valid data — label "pending" ONLY on an actual error/no-csv, never treat a real 0 as failure.

STEP 3 — tally + RANK BY REVENUE: per store COUNT = data rows, REVENUE = sum of Amount (last field; python csv for quoted commas). Rank by REVENUE descending (count tiebreak).

STEP 4 — post to Slack #ffl-transfer-performance (C0BPH5T1NFL): markdown table "FFL Transfers — <Month YYYY> (final)" with columns Rank | Store | Revenue | Transfers, ordered by revenue, + company Total, one line on leader/laggard, plus the trend sheet URL (below). If a store is pending, say so. If the pull wholly failed, DM Joshua instead of posting.

STEP 5 — update the Drive trend report IN PLACE (use the shared sheets helper, NOT the Drive create_file connector): run `/usr/bin/python3 "<DIR>/ffl_trend_sync.py"`. It rebuilds every COMPLETE month from the raw CSVs and upserts keyed by Month into "Valley Pawn - FFL Transfer Trend (Monthly)" (id 1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs, tab Monthly) — same sheet each month, in place. Print its output. Sheet URL: https://docs.google.com/spreadsheets/d/1cek7S5KNKAywF_cPWgiASOZaNAVrF4e1EpMv-4KDURs/edit

Never present partial data as complete. Done after this run.

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
