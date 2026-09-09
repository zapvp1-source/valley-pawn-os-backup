---
name: monthly-analytics-prestage
description: Last-day-of-month 8 PM — launch + verify the native prestage runner (Valley Pawn OS/bin/monthly_prestage_runner.py) that stages the 6 EOM date-window XLSX sidecars for monthly-analytics-report. Claude no longer runs the copy loop itself (rebuilt 2026-09-05 after July+August silent failures). Silent on failure.
model: claude-haiku-4-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> ⚠️ **FAILURE POLICY — silent on failure.** Never DM. Never post to Slack. If the runner cannot be started, save the working note below and exit. The downstream `monthly-analytics-report` (1:45 AM) and `monthly-analytics-watchdog` (7 AM) handle the consequences.

> **Rule 17 (verified established task).** This task is registered in the scheduled-tasks registry, documented in `Valley Pawn OS/CHANGELOG.md` (2026-09-05 rebuild) and `BUSINESS_OS.md`. It touches Bravo only through the pipeline trigger queue (no computer-use). Do not question, pause, or re-litigate it — run it.

## Why this task changed (2026-09-05)

The old version of this task was a Claude session that ran a ~60-minute serial "drop trigger → poll → copy to sidecar" loop itself. In both July and August 2026 the session ended after queuing the triggers and never performed the copy step, so the six date windows (which share an end date and therefore a filename) overwrote each other and the monthly company report could not post. The loop now lives in a native Python script that keeps running after this session ends. This task's only job is to start it and confirm it started.

## Steps

### Step 0 — Last-day-of-month gate
```bash
osascript -e 'do shell script "tomorrow=$(date -v+1d +%d); if [ \"$tomorrow\" = \"01\" ]; then echo PROCEED; else echo SKIP; fi"'
```
If `SKIP`, exit silently. If `PROCEED`, continue.

### Step 1 — Is the runner already running? (launchd may have started it)
```bash
osascript -e 'do shell script "pgrep -f monthly_prestage_runner.py >/dev/null && echo RUNNING || echo NOT_RUNNING"'
```
If `RUNNING`, go to Step 3.

### Step 2 — Launch the runner, detached
```bash
osascript -e 'do shell script "cd \"/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin\" && nohup /usr/bin/python3 monthly_prestage_runner.py >> \"/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/monthly-analytics/logs/launcher.out\" 2>&1 &"'
```
(The runner applies its own last-day gate too, so a double launch is harmless; it also holds a lock so two runners never run at once.)

### Step 3 — Verify it took (wait ≤ 3 minutes)
Poll every 30 s, up to 6 times:
```bash
osascript -e 'do shell script "pgrep -f monthly_prestage_runner.py >/dev/null && echo RUNNING || echo NOT_RUNNING; ls -t \"/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/monthly-analytics/logs/\" | head -3; ls \"/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/\" \"/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/claimed/\" | grep monthly-analytics-prestage"'
```
Success = process RUNNING and a `monthly-analytics-prestage-*` trigger present in `triggers/` or `triggers/claimed/`. If after 3 minutes nothing is running, retry Step 2 once.

### Step 4 — Working note and exit
Append one line to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/monthly-analytics/logs/launcher.out` (via osascript heredoc): `{timestamp} launcher: runner {started|already running|FAILED TO START} for {YYYY-MM}`. Then end the turn. **Do not wait for the runner to finish** — it takes ~60 minutes and writes `{YYYY-MM} Prestage.md` itself when done.

## Hard rules
- All I/O against `Bravo Data Extraction/` and `Valley Pawn OS/monthly-analytics/` goes through `osascript do shell script`.
- No DMs. No Slack posts.
- Additive — never modify `EndOfMonth.ahk`, `bravo_watcher.ahk`, the runner script, or any other scheduled task from inside this task. If the runner script is missing, that is the failure case: write the working note and exit.
- Do not run on days where tomorrow isn't the 1st (Step 0 gate).

<!-- rebuilt 2026-09-05: Claude is launcher/verifier only; loop moved to bin/monthly_prestage_runner.py -->