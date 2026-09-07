---
name: monday-bravo-part1-watchdog
description: Sunday 7:15 PM ET completion check for monday-bravo-combined-run (Part 1). If it silently failed to drop this week's trigger, self-heal by dropping it directly — closes the 3-week silent-outage gap found 2026-08-21.
---

---
name: monday-bravo-part1-watchdog
description: Sunday 7:15 PM ET — confirms monday-bravo-combined-run (Part 1) actually dropped this week's combined trigger; self-heals by dropping it directly if not, rather than letting the whole Monday pipeline go silently dark.
model: claude-sonnet-5
---

> **LOCAL ACCESS GATE — DO THIS FIRST.** This task runs on Joshua's Mac Studio and has local machine access via `mcp__Control_your_Mac__osascript`. If that tool is deferred, load it first: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`. Probe with a trivial `do shell script` echo; if it errors, wait 30s and retry for up to 12 minutes before concluding local access is unavailable (it almost never is — a not-yet-loaded tool is not a missing capability).
> **Timeout rule:** the osascript wrapper kills any single call at ~25s. Never sleep longer than ~18s inside one call; poll in short increments across separate calls.

> ⚠️ **FAILURE ALERT POLICY (platform standard):** If this run fails, errors out, or cannot complete, send Joshua ONE plain-language Slack DM line (channel D03BHQH5VGT): "⚠️ Scheduled task \"monday-bravo-part1-watchdog\" did not complete — <date>." Nothing technical in that DM — put detail in the run output for the next session. Never post failure notices to any team channel or employee.

## Why this task exists (added 2026-08-21)

`monday-bravo-combined-run` (Part 1, Sunday ~6:00 PM ET) is supposed to preflight Bravo and drop the
week's combined multi-report trigger (aged inventory, loans, layaways, employee-activity, chekkit,
FPD × 5 stores) so `monday-bravo-combined-compile` and `monday-bravo-postcheck` have data to read
Monday morning. Confirmed incident: for at least the weeks of 2026-08-16 and 2026-08-17, Part 1's
`lastRunAt` advanced on schedule but it produced **no trigger file, no log, no result.json, and no
start-notice DM** — a silent failure with an unconfirmed root cause. Because the downstream compile
task used to depend on Part 1 to reschedule it, this cascaded into all 5 ops Slack channels —
including #employee-performance — going dark for 3 consecutive weeks with zero alert to Joshua. That
specific cascade (compile depending on Part 1 for its own schedule) was fixed 2026-08-21 by giving
compile its own independent cron. This task is the second half of the fix: catching Part 1 itself
silently failing to even drop the trigger, the same evening, while Bravo is still idle (Sunday) —
instead of discovering it via a downstream task noticing stale data days or weeks later.

==========================================================================
STEP 1 — Check this week's heartbeat
==========================================================================

Compute TODAY's date in ET (this fires Sunday, same calendar day as `monday-bravo-combined-run`'s
own cron, ~75 minutes after it).

```bash
cat '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/monday-bravo-combined-run.last_success' 2>/dev/null || echo MISSING
```

If the file exists AND its date-stamp is TODAY → Part 1 succeeded. **Stay completely silent — no
Slack post, no DM.** Done.

If missing, or its date-stamp is NOT today → Part 1 did not reach its Step 1.5 this week. Proceed
to Step 2 to self-heal. Also check for a stuck run first: `ls '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/' | grep -v -E '^(processed|claimed|killed|payloads|staging)$'` — if something non-standard is sitting there, a run may still be genuinely in flight (not silently dead); if so, wait ~10 minutes and re-check the heartbeat once before concluding it's actually missing.

==========================================================================
STEP 2 — Self-heal: run Part 1's own preflight + trigger-drop directly
==========================================================================

Read `/Users/joshuadavis/Documents/Claude/Scheduled/monday-bravo-combined-run/SKILL.md` and execute
its STEP 0 (pre-flight check) and STEP 1 (drop the combined multi-report trigger) and STEP 1.5
(write the heartbeat) verbatim, using TODAY's date for `<TODAY>` and `<FIRST_OF_MONTH>`. Do NOT
re-run its STEP 3 (that task's own start-notice DM format) — instead use the DM below so Joshua can
tell this was a recovered run, not a normal one.

If STEP 0's preflight fails (VM down, watcher dead and won't restart, trigger queue jammed) — this
mirrors that task's own escape hatch: DM Joshua with what failed (per the failure alert policy
above) and stop. Do not force through a failed preflight.

If the trigger drops successfully, DM Joshua (`U03BB52MDSA`):
```
🩹 Sunday Bravo pull recovered — <DATE>
monday-bravo-combined-run didn't drop this week's trigger on its own schedule (cause still unconfirmed — see its SKILL.md changelog). This watchdog dropped it directly instead, ~75 min late. Compile still fires its normal fixed 8:00 AM ET Monday publish and will pick this up.
If this keeps recurring, the root cause needs a real fix, not just this safety net.
```

==========================================================================
STEP 3 — Guard rails
==========================================================================

- This task must never post to any team/ops Slack channel — DM Joshua only, per the policy above.
- Do not touch `monday-bravo-combined-compile` or `monday-bravo-postcheck` — they already have their
  own independent schedules and self-heal logic; this task's only job is Part 1's trigger-drop.
- If this watchdog itself has had to recover Part 1 for 3+ consecutive weeks, say so explicitly in
  the DM ("this is the Nth week in a row") so Joshua knows the safety net is being used as the
  primary path, not a rare exception — check for prior `🩹 Sunday Bravo pull recovered` DMs in this
  channel's recent history before sending, and note the streak if found.
