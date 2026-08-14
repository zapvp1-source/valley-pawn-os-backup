---
name: markdownver-watcher-restart-oneshot-r2
description: Retry: restart the Bravo AHK watcher (with proper LOCAL ACCESS GATE this time) so it picks up the new markdown-verification pipeline cell.
---

This is a silent-to-Slack, one-shot infrastructure task. Never post to Slack and never DM Joshua. Do write a status file at the end (Step 5) so a human/session can check the outcome later — that is NOT a Slack post.

> **LOCAL ACCESS GATE — DO THIS FIRST.** This task runs on Joshua's Mac Studio and DOES have local machine access via `mcp__Control_your_Mac__osascript`. That tool may be deferred (not pre-loaded) at task start — that is NOT the same as unavailable.
> 1. If `ToolSearch` is available, load it first: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe with `do shell script "echo READY"`. If it returns READY, proceed immediately.
> 3. If it errors as not-connected/not-found, wait 30s and re-probe, up to 12 minutes (24 probes) total, before concluding local access is genuinely unavailable.
> 4. NEVER conclude "this runs in a cloud container with no bridge to the Mac" without completing the full 12-minute retry loop first — that false conclusion is the single most common cause of this class of task silently doing nothing.
> **Timeout rule:** the osascript wrapper kills any call over ~25s. Never sleep >18s inside one call — poll in short separate calls.

Goal: restart the Bravo Data Extraction AHK watcher (Windows VM in Parallels) so it loads a newly-added, purely-additive pipeline cell (`markdown-verification` — new #Include + REPORT_HANDLERS line added to bravo_watcher.ahk and bravo_export.ahk this session; nothing existing was touched).

Steps:
1. After the LOCAL ACCESS GATE confirms osascript is live, run: `do shell script "cat '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/watcher.last_started.txt'"`. Capture the "Watcher started:" line as BEFORE_TS.
2. Contention check first: `do shell script "bash '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/_bravo_foreground_guard.sh' check"`. If it prints BUSY, wait 60s and re-check once; if still BUSY, skip to step 6 and write status=BUSY_SKIPPED (do not force through a restart on a busy Bravo).
3. If CLEAR, run: `do shell script "/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\\Documents\\Claude\\Projects\\Bravo Data Extraction\\_restart_watcher.ps1'"`.
4. Sleep 18s (separate call), then re-read `logs/watcher.last_started.txt` as AFTER_TS. If it did not advance past BEFORE_TS, sleep 18s again and re-check, up to 3 total checks (~54s).
5. Check whether AFTER_TS's "Handlers:" line includes `markdown-verification`.
6. Write a plain status file via osascript to `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/_markdownver_restart_status.txt` containing exactly one of: `RESTARTED_OK ts=<AFTER_TS>` / `RESTARTED_BUT_HANDLER_MISSING ts=<AFTER_TS>` / `NOT_RESTARTED before=<BEFORE_TS>` / `BUSY_SKIPPED`. This file write is diagnostic logging, not a Slack post — always do it as the last step regardless of outcome.
7. Exit. No Slack post, no DM, under any circumstance.