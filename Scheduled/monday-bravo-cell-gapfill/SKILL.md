---
model: claude-haiku-4-5
name: monday-bravo-cell-gapfill
description: Sunday 8:30 PM ET — re-pulls any cells that failed in the Sunday combined Bravo run so Monday morning's ops posts have all 5 stores. Runs the native gap-fill runner; silent, no Slack.
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Launch and verify the native Monday gap-fill runner. It re-pulls the cells that failed in tonight's `monday-bravo-combined-run`, so tomorrow's 8 AM compile has a complete 5-store set for every report instead of withholding them under Completeness Gate v2.

STEP 0 — Load the `mcp__Control_your_Mac__osascript` tool (ToolSearch `select:mcp__Control_your_Mac__osascript`) and probe it with a trivial `do shell script "echo READY"`. If it is still warming, wait 30 s and retry for up to 12 minutes.

STEP 1 — Is it already running? `pgrep -f monday_gapfill_runner.py`. If yes, skip to Step 3.

STEP 2 — Launch it detached:
`cd "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin" && nohup /usr/bin/python3 monday_gapfill_runner.py >> "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/monday-gapfill/launcher.out" 2>&1 &`
With no --date it repairs the newest `monday-bravo-combined-*.result.json`, which is tonight's run. It is safe to launch twice (it re-checks what is already on disk before dropping anything).

STEP 3 — Verify it took (poll every 30 s, up to 5 times): the process is running, AND either a `monday-gapfill-*` trigger is present in `Bravo Data Extraction/triggers/` or `triggers/claimed/`, or the log at `Valley Pawn OS/monday-gapfill/gapfill-<date>.log` says "no failed cells — nothing to do" (the good case — nothing to repair).

STEP 4 — End the turn. Do NOT wait for it to finish; a full repair can take 45+ minutes and the runner writes its own status file at `Valley Pawn OS/monday-gapfill/{DATE}.md`. Post nothing to Slack and send no DM — `monday-bravo-combined-compile` (8 AM) and `monday-bravo-postcheck` (8:30 AM) own all notification. If the runner cannot be started at all, send Joshua ONE plain-language DM (D03BHQH5VGT): "Tomorrow's store reports may be missing some stores — worth a look." and stop.

Hard rules: all file I/O via osascript. Additive only — never edit a pipeline handler, the watcher source, or another task. The runner never restarts the watcher while the queue is busy; do not override that.


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
