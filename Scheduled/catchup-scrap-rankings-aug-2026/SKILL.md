---
name: catchup-scrap-rankings-aug-2026
description: One-shot 2026-09-05 — the 9/1 run of monthly-scrap-rankings produced no August post; run that task's SKILL.md for reporting period 2026-08.
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Catch-up run of the existing scheduled task `monthly-scrap-rankings` for reporting period August 2026 (its 9/1 run posted nothing).

1. Invoke the `enterprise-map` skill first, then `bravo-context` and `vp-operating-rules`.
2. Read `/Users/joshuadavis/Documents/Claude/Scheduled/monthly-scrap-rankings/SKILL.md` (via osascript `cat`) and follow it as written, treating the reporting period as 2026-08 (pull window `2026-07..2026-08`).
3. Before dropping any trigger, wait until the pipeline queue is idle: no `*.json` in `Bravo Data Extraction/triggers/`, nothing in `triggers/claimed/` named `monthly-analytics-prestage-*`, and `pgrep -f monthly_prestage_runner.py` empty (poll every 60 s, up to 45 min).
4. Duplicate guard: if #scrap-rankings (C05EHBH4G67) already has an "August gold scrap" post, do not post again.
5. Write the task's status file as its SKILL.md directs, and add one dated line under a `## 2026-09-05` heading at the top of `Valley Pawn OS/CHANGELOG.md` saying whether the August scrap rankings posted.