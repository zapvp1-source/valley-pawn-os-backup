---
model: claude-sonnet-5
name: monthly-publication-audit
description: 2nd and 4th of month, 10 AM — verifies every monthly publication in PUBLICATION_CALENDAR.md actually landed for the prior month (reads the channel, not run records), re-runs rerun-safe producers when a post is missing, and DMs Joshua one plain line only if something could not be recovered.
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Invoke the `enterprise-map` skill first. Then read `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/pending-tasks/monthly-publication-audit/SKILL.md` (via osascript `cat` if the Projects folder is not mounted) and follow its instructions exactly — it is the full specification for this task: what to verify, how to classify rerun-safe vs verify-only, the recovery order, the logging, and the single-plain-DM-only alert rule.


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
