---
name: monday-bravo-combined-run
description: Sunday-evening Bravo pull (PART 1 of 2, moved off Monday morning 2026-08-10 to avoid contention) — drops all Monday ops triggers, schedules compile for a fixed Monday 8:00 AM ET publish.
model: claude-sonnet-5
---

---
name: monday-bravo-combined-run
description: Sunday-evening Bravo pull (PART 1 of 2, moved off Monday morning 2026-08-10 to avoid contention) — drops all Monday ops triggers, writes a completion heartbeat (added 2026-08-21 so Fleet Guardian's output-verification pass can detect a silent failure), schedules compile for a fixed Monday 8:00 AM ET publish.
model: claude-sonnet-5
---

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard, added 2026-08-02).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed with the task.
> 3. If it errors (no such tool available, not connected, tool-not-found): wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **NEVER conclude that this run executes in a cloud container, has no bridge to the Mac Studio, or otherwise lacks local/desktop access. That conclusion is false** and is the single most common cause of a false failure on this platform. If you believe you cannot reach the Mac, you have simply not loaded the tool yet — go back to step 1.
>
> **Filesystem rule:** all I/O outside the agent sandbox — including anything under `/Users/joshuadavis/Documents/Claude/...` — goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s inside one call; poll in short increments across separate calls. Guard any command that may exit nonzero with a trailing || true.


> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.



> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are running Joshua's Monday morning combined Valley Pawn Bravo POS run — **the trigger-drop phase only.**

## What changed 2026-05-29

This task used to do everything: preflight → drop triggers → wait 30+ min → compile → Slack post → DM. That long inline wait made the Cowork session run out of context mid-run (confirmed 2026-05-29 — pipeline produced all 25 CSVs but compile/post never ran). The fix: split into TWO scheduled tasks.

- **This task (`monday-bravo-combined-run`)** = preflight + drop all triggers + write heartbeat + schedule the compile task + exit. ~3 min wall time.
- **`monday-bravo-combined-compile`** = fires ~75 min later. Reads the result JSON files and CSVs, posts to all 5 ops Slack channels, saves files, DMs Joshua the rollup. ~5-10 min wall time.

Both tasks are short and context-safe.

## What changed 2026-06-22 — EOM / store-rankings split out

The 5 per-store **end-of-month** triggers were REMOVED from this task. On Bravo
2026.6.0.76 the EOM report's export commit intermittently freezes Bravo and
writes a 0-byte file, which used to strand the whole run and block the 4 reliable
reports from posting. EOM now lives in its own task — **`monday-store-rankings`** —
which runs later Monday morning (~10:30 AM) on a *settled* Bravo (the condition
where EOM export is reliable) with a resilient settle+retry runner.

So this task now drops ONLY the combined multi-report trigger (aged inventory,
loans, layaways, employee, chekkit). Those four reports posted cleanly and must
stay isolated from the flaky EOM. **Do NOT add EOM triggers back here.**

## What changed 2026-08-10 — moved off Monday morning entirely

This task used to fire ~5:30 AM Monday, landing it squarely in the densest Bravo-contention
window of the week (5:30-9:00 AM Monday: items-to-price, monday-bravo-postcheck,
vp-dashboard-refresh, and others all want Bravo at the same time). A 2026-08-10 collision with
daily-items-to-price ("FREE1 is busy with Inventory") made the cost of that concrete.

**This task now runs Sunday evening instead** (cron moved to Sunday ~6:00 PM ET — every store is
closed Sunday, so Bravo is completely idle and there is no realistic contention). The data itself
is unaffected: aged inventory, loans, layaways, employee activity, chekkit, and FPD are all
point-in-time snapshots as of Sunday evening, which is identical to a Monday-morning snapshot
since nothing happens at any store on Sunday.

**Step 2 below no longer schedules the compile task as "now + 90 minutes."** That relative offset
is what made Monday's Slack posts land anywhere from 7 AM to 9 AM depending on how fast Bravo
cooperated that morning (see monday-bravo-postcheck backfills). Since the Sunday pull now has a
huge overnight buffer to finish, Step 2 instead schedules compile for a FIXED Monday 8:00 AM ET
clock time — matching the middle of the range the team already sees today, not a new time.

See BRAVO_HEALTH_RUNBOOK.md section 0 for the contention rule that prompted this move, and
MEMORY feedback_bravo_contention_check for the incident it's based on.

## What changed 2026-08-21 — completion heartbeat + Fleet Guardian coverage added (this task had been silently failing)

**Confirmed incident:** this task's `lastRunAt` kept advancing every Sunday on schedule, but for
at least the weeks of 2026-08-16 and 2026-08-17 it produced **no trigger file, no log, no result.json,
and no start-notice DM** — meaning the run was invoked but silently failed before or during Step 0/1,
with no record of why. That silent failure cascaded: `monday-bravo-combined-compile` had nothing to
read, `monday-bravo-postcheck`'s backfill also had nothing to read (a separate date-mismatch bug in
both of those tasks compounded it further — fixed the same day, see their own SKILL.md headers), and
all 5 ops channels — including #employee-performance — went dark for **3 consecutive weeks** with
no alert to Joshua, discovered only when a downstream Canvas-refresh task noticed stale data on
2026-08-21.

**Fix (per `Valley Pawn OS/HARDENING_STANDARD.md` — no new per-task watchdogs; coverage comes from
self-verification inside the task plus the fleet-wide Fleet Guardian):**
1. This task now writes a completion heartbeat immediately after Step 1 succeeds (see STEP 1.5
   below) — a fast, local self-check.
2. Registered in `Valley Pawn OS/fleet/rerun_manifest.json` as **rerun-safe** (this task only
   preflights + drops an internal trigger + DMs Joshua — no external contact, no money, no
   Bravo-screen-driving, and Step 0 Check 5 already duplicate-guards against a stuck/duplicate
   trigger).
3. Registered in `Valley Pawn OS/fleet/expected_outputs.json` (marker: the Step 3 DM text "Sunday
   Bravo pull dispatched", channel D03BHQH5VGT, cadence weekly-sunday-1800et, grace_hours 2) so
   **Fleet Guardian's Step 1b output-verification pass** — which exists specifically to catch a
   task that fired but died silently mid-run, the exact class `lastRunAt`-only detection cannot see
   — will notice this task's DM never went out and re-run Steps 0-1 itself at its next pass
   (12:45 PM or 9:45 PM ET; the Sunday 9:45 PM pass is ~3h45m after this task's 6 PM cron, well
   inside the 2-hour grace window).

This closes the gap without adding a bespoke `monday-bravo-part1-watchdog` task (one was built and
then deleted the same day once `HARDENING_STANDARD.md`'s "no new per-task watchdogs" policy and the
existing Guardian/manifest mechanism were found — the manifest entries above are the correct,
consistent fix). This is a detection/self-heal layer on top of this task — it does not explain the
original silent-failure cause, which remains unconfirmed; if it recurs, check whether this task is
being skipped for a platform reason (e.g. a usage-cap "global_limit" skip — see the
`scheduled-task-models` skill) rather than assuming it is this file's logic at fault.

==========================================================================
STEP 0 — Pre-flight check
==========================================================================

Before dropping any trigger, verify the runtime is healthy. If anything is missing, attempt one auto-restart; if that fails, DM Joshua and stop. Do NOT drop triggers if the watcher isn't running.

**Check 1 — Parallels VM running:**
```bash
/usr/local/bin/prlctl list --all | grep -E 'running.*Windows 11'
```
Expected: `running  -  Windows 11`. If absent, DM Joshua and stop.

**Check 2 — bravo_watcher.ahk process alive:**
```bash
/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user wmic process where 'name="AutoHotkey64.exe"' get ProcessId,CommandLine
```
Expected: one AHK process has `bravo_watcher.ahk` in its command line. If missing, run `_restart_watcher.ps1` to relaunch (Y:-aware as of 2026-05-29). If still missing, DM Joshua and stop.

**Check 3 — BravoAutoLogin.ahk process alive:**
Same `wmic` check; look for `BravoAutoLogin.ahk`. If missing, relaunch with `cmd /c start "" /B "C:/Program Files/AutoHotkey/v2/AutoHotkey64.exe" "C:/Users/joshuadavis/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/BravoAutoLogin.ahk"`. Continue even if missing — watcher's RecoverFromAutoLock handles most cases.

**Check 4 — watcher.last_started.txt is recent:**
```bash
cat '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/watcher.last_started.txt'
```
If timestamp >7 days old, run `_restart_watcher.ps1` to refresh.

**Check 5 — Trigger queue empty:**
```bash
ls '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/' | grep -v -E '^(processed|claimed|killed|payloads|staging)$'
```
If a trigger is sitting unprocessed, the previous run hung. DM Joshua, dump the filename, stop.

Only if all five checks pass, proceed to Step 1.

==========================================================================
STEP 1 — Drop the combined multi-report trigger
==========================================================================

Drop the single combined multi-report trigger below. (As of 2026-06-22 the 5
per-store EOM triggers are NO LONGER dropped here — they run in the separate
`monday-store-rankings` task. See the note after the trigger.)

**Main multi-report trigger** at `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/monday-bravo-combined-YYYY-MM-DD.json`:

```json
{
  "id": "monday-bravo-combined-YYYY-MM-DD",
  "requested_at": "YYYY-MM-DDTHH:MM:SS-04:00",
  "reports": [
    {"name": "aged-inventory-summary", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "<TODAY>"},
    {"name": "loans-75-days-past-due", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "<TODAY>"},
    {"name": "layaways",               "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "<TODAY>"},
    {"name": "employee-activity",      "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "<FIRST_OF_MONTH>"},
    {"name": "chekkit-invites",        "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "<TODAY>"},
    {"name": "fpd-cohort",             "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "<TODAY>"}
  ]
}
```

> **FPD added 2026-07-22 (per Joshua + expert board).** The standalone `weekly-fpd-ranking`
> task stalled after 2026-05-18 (repeated Bravo access failures running in its own session).
> Its `fpd-cohort` pipeline cell now rides inside this combined trigger — same healthy
> pipeline window, no separate session needed. The compile task posts the FPD ranking to
> #first-payment-default (see monday-bravo-combined-compile STEP 4.5). `fpd-cohort` is a
> proven pipeline cell (handler `reports/FpdCohort.ahk`, saved report "Claude First Payment
> Default") — nothing else in this trigger changed.

> **EOM / store-rankings is NOT dropped here anymore (2026-06-22).** The 5
> per-store end-of-month triggers moved to the separate `monday-store-rankings`
> task. Keep this task to the single combined trigger above. Do NOT re-add EOM here.

Date conventions:
- `<TODAY>` = current date YYYY-MM-DD in ET
- `<FIRST_OF_MONTH>` = YYYY-MM-01 of current month

==========================================================================
STEP 1.5 — Write completion heartbeat (added 2026-08-21)
==========================================================================

Immediately after the trigger file in Step 1 is successfully written to disk (drop confirmed —
you do not need to wait for the watcher to claim/process it), write a heartbeat file as a fast
local self-check (Fleet Guardian's own detection is the authoritative safety net — see the
2026-08-21 changelog note above — but this costs one line and helps any session diagnosing this
task quickly):

```bash
echo "<TODAY>T<HH:MM:SS>-04:00 trigger=monday-bravo-combined-<TODAY>" > '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/monday-bravo-combined-run.last_success'
```

If the trigger write in Step 1 failed (see ESCAPE HATCH below), do NOT write this heartbeat —
its absence/staleness is a useful diagnostic signal even though Guardian's own check is via the
Step 3 DM marker, not this file.

==========================================================================
STEP 2 — (REMOVED 2026-08-21 — compile now runs on its own cron, not scheduled by this task)
==========================================================================

**Prior to 2026-08-21, this step called `update_scheduled_task` to re-arm `monday-bravo-combined-compile`
as a one-time `fireAt` for the next Monday 8 AM.** That made PART2 (the actual Slack-posting task,
covering all 5 ops channels including #employee-performance, #layaway-review, #first-payment-default)
entirely dependent on THIS task successfully reaching this step every single week. It last succeeded
2026-08-03; PART1 kept firing on its Sunday cron afterward but for at least the week of 8/16 produced
no result.json, no trigger file, and no DM — a silent failure whose cause was never confirmed — which
left PART2 disabled with no future fire time. All 5 ops channels went dark for 2+ weeks as a result.

**Fix: `monday-bravo-combined-compile` now has its own independent recurring cron (`0 8 * * 1`).**
It no longer needs anything from this task to know when to run. This task's ONLY job is now Steps
0-1.5 (preflight + drop the trigger + write the heartbeat) and Step 3 (DM Joshua). **Do not add a
Step 2 back that calls `update_scheduled_task` on `monday-bravo-combined-compile`** — that would
silently convert it back to a one-time task and reintroduce this exact bug (see that task's own
SKILL.md header for the full incident note).

**Also note (fixed 2026-08-21 in the compile task):** because this task computes `<TODAY>` as ITS
OWN run date (Sunday) when naming the trigger/result.json/CSVs, and `monday-bravo-combined-compile`
fires the next day (Monday), the compile task now treats "yesterday" as the pipeline date for all
file lookups rather than assuming same-day. No change needed here — just don't rename this task's
own trigger-id/date convention without checking that downstream assumption.

==========================================================================
STEP 3 — DM Joshua the start notice
==========================================================================

DM Joshua (`U03BB52MDSA`) on Slack. **This exact DM (marker: "Sunday Bravo pull dispatched") is
what Fleet Guardian's expected_outputs.json entry checks for — do not reword it below the marker
line without also updating that manifest entry.**

```
🚦 Sunday Bravo pull dispatched — YYYY-MM-DD
1 multi-report trigger dropped (30 cells: aged-inv, loans, layaways, employee, chekkit, fpd × 5).
Compile task scheduled for a fixed 8:00 AM ET Monday publish (moved off Monday morning 2026-08-10 — see BRAVO_HEALTH_RUNBOOK.md section 0).
EOM / store-rankings runs separately in monday-store-rankings (~10:30 AM Monday, unchanged for now).
Pipeline running overnight in the watcher meanwhile — no action needed.
```

Then exit. This task is done.

==========================================================================
ESCAPE HATCH — IF DROPS FAIL
==========================================================================

If a trigger drop fails (write permission, disk full, etc.), DM Joshua immediately with what failed and stop. Don't try to recover — Joshua can re-trigger manually. Do NOT write the Step 1.5 heartbeat in this case.

==========================================================================
LEGACY DESIGN — preserved for reference
==========================================================================

The pre-2026-05-29 version of this task waited inline for ~30 min for the pipeline to complete, then ran 5 chained SKILLs' compile+post phases. That worked when the Cowork session could survive a 30+ min wait — but on 2026-05-29 the session timed out before reaching compile/post. The full pipeline DID complete (25/25 cells, 0 errors) but the Slack posts never went up.

The split (this task = drop-and-exit, `monday-bravo-combined-compile` = post-and-DM) keeps each scheduled task under ~10 min wall time and removes the long-context-window risk.

Pre-split version backed up at `SKILL.md.bak-pre-split-2026-05-29`.

<!-- migrated to working model 2026-06-15 -->
<!-- heartbeat + Fleet Guardian coverage added 2026-08-21 -->
