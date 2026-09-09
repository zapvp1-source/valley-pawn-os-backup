---
name: bonus-july-finish
description: One-shot. Re-runs the July 2026 bonus close once the queued Roanoke employee-activity pull has landed, so the Roanoke associate lines are included, and DMs Joshua the corrected numbers. Never posts to a team channel.
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Finish the July 2026 Valley Pawn bonus close. Autonomous, non-interactive.

BACKGROUND: the July close ran on 2026-09-06 with everything except Roanoke's per-employee gross profit — July's month-range employee-activity CSV did not exist, so a pipeline trigger (`bonus-july-empact-20260906T0110`, employee-activity-range ROA 2026-07-01..2026-07-31) was queued behind another session's work. Roanoke is the only store that hit its target in July, so its associate lines are the only ones missing.

HARD RULES
- Output ONLY to Joshua's DM (D03BHQH5VGT). Never #bonus-goals, never a manager or employee — Joshua's instruction 2026-09-06 was "do not alert the field."
- Host shell via mcp__Control_your_Mac__osascript (`do shell script`); sleeps <= 18s per call.
- Never estimate a missing number.

STEPS
1. Check for `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/2026-07-31_ROA_employee-activity-range.csv`.
2. If it is NOT there: check whether `triggers/bonus-july-empact-20260906T0110.json` is still pending (queue depth is normal, not a hang — see bravo-context). If the trigger is gone but no file appeared, drop a fresh one with a new id for the same report/store/date range, wait up to 40 minutes polling, then continue.
3. Once the file exists: `cd '/Users/joshuadavis/Documents/Claude/Projects/Bonus Program' && /usr/bin/python3 bin/bonus_engine.py collect --month 2026-07 && /usr/bin/python3 bin/bonus_engine.py close --month 2026-07`.
4. DM Joshua the updated Roanoke lines and the new July total, in plain language, noting that it supersedes the earlier July figure and that nothing has been paid or posted.
5. Append a dated line to `Bonus Program/RUN_LOG.md`.
6. If the file still cannot be produced after step 2, DM Joshua one plain sentence saying the July Roanoke employee split still isn't available and that the manager and Preston figures are unaffected. No technical detail in the DM.