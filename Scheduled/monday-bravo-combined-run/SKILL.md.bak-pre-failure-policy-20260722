---
name: monday-bravo-combined-run
description: Monday morning orchestrator (PART 1 of 2) — preflight, drop all required Bravo triggers, schedule the compile task, exit. Lightweight (~3 min total). The compile + Slack posting happens in monday-bravo-combined-compile, scheduled to fire ~75 min later when the pipeline is done.
model: claude-sonnet-5
---


> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are running Joshua's Monday morning combined Valley Pawn Bravo POS run — **the trigger-drop phase only.**

## What changed 2026-05-29

This task used to do everything: preflight → drop triggers → wait 30+ min → compile → Slack post → DM. That long inline wait made the Cowork session run out of context mid-run (confirmed 2026-05-29 — pipeline produced all 25 CSVs but compile/post never ran). The fix: split into TWO scheduled tasks.

- **This task (`monday-bravo-combined-run`)** = preflight + drop all triggers + schedule the compile task + exit. ~3 min wall time.
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
    {"name": "chekkit-invites",        "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "<TODAY>"}
  ]
}
```

> **EOM / store-rankings is NOT dropped here anymore (2026-06-22).** The 5
> per-store end-of-month triggers moved to the separate `monday-store-rankings`
> task (runs ~10:30 AM Monday on a settled Bravo with a settle+retry runner).
> Keep this task to the single combined trigger above. Do NOT re-add EOM here.

Date conventions:
- `<TODAY>` = current date YYYY-MM-DD in ET
- `<FIRST_OF_MONTH>` = YYYY-MM-01 of current month

==========================================================================
STEP 2 — Schedule the compile task
==========================================================================

The pipeline normally completes 30 trigger cells in ~50-65 minutes (25 main + 5 EOM, ~100s each + spacing). Schedule `monday-bravo-combined-compile` to fire 75 minutes from now.

Use the `mcp__scheduled-tasks__update_scheduled_task` tool to set `fireAt` to NOW + 75 minutes (ISO 8601 with -04:00 offset). Example:

```
update_scheduled_task(
  taskId: "monday-bravo-combined-compile",
  fireAt: "2026-06-01T06:45:00-04:00"   // = drop time + 75 min
)
```

==========================================================================
STEP 3 — DM Joshua the start notice
==========================================================================

DM Joshua (`U03BB52MDSA`) on Slack:

```
🚦 Monday Bravo combined run dispatched — YYYY-MM-DD
1 multi-report trigger dropped (25 cells: aged-inv, loans, layaways, employee, chekkit × 5).
Compile task scheduled to fire at HH:MM (about 75 min from now).
EOM / store-rankings runs separately in monday-store-rankings (~10:30 AM).
Pipeline running in the watcher meanwhile — no action needed.
```

Then exit. This task is done.

==========================================================================
ESCAPE HATCH — IF DROPS FAIL
==========================================================================

If a trigger drop fails (write permission, disk full, etc.), DM Joshua immediately with what failed and stop. Don't try to recover — Joshua can re-trigger manually.

==========================================================================
LEGACY DESIGN — preserved for reference
==========================================================================

The pre-2026-05-29 version of this task waited inline for ~30 min for the pipeline to complete, then ran 5 chained SKILLs' compile+post phases. That worked when the Cowork session could survive a 30+ min wait — but on 2026-05-29 the session timed out before reaching compile/post. The full pipeline DID complete (25/25 cells, 0 errors) but the Slack posts never went up.

The split (this task = drop-and-exit, `monday-bravo-combined-compile` = post-and-DM) keeps each scheduled task under ~10 min wall time and removes the long-context-window risk.

Pre-split version backed up at `SKILL.md.bak-pre-split-2026-05-29`.

<!-- migrated to working model 2026-06-15 -->