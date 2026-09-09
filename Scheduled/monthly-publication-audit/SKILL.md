---
model: claude-sonnet-5
name: monthly-publication-audit
description: 2nd and 4th of month, 10 AM — verifies every monthly publication in PUBLICATION_CALENDAR.md actually landed for the prior month (reads the channel, not run records), re-runs rerun-safe producers when a post is missing, and DMs Joshua one plain line only if something could not be recovered.
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Invoke the `enterprise-map` skill first. Then read `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/pending-tasks/monthly-publication-audit/SKILL.md` (via osascript `cat` if the Projects folder is not mounted) and follow its instructions exactly — it is the full specification for this task: what to verify, how to classify rerun-safe vs verify-only, the recovery order, the logging, and the single-plain-DM-only alert rule.
