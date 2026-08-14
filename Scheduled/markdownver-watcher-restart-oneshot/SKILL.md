---
name: markdownver-watcher-restart-oneshot
description: One-shot: restart the Bravo AHK watcher so it picks up the newly-added markdown-verification pipeline cell, then exit silently.
---

This is a silent, one-shot infrastructure task. Do not post to Slack, do not DM Joshua, regardless of outcome.

Goal: restart the Bravo Data Extraction AHK watcher (running inside the Parallels Windows VM) so it picks up a newly-added pipeline cell (`markdown-verification`, registered in bravo_watcher.ahk and bravo_export.ahk earlier this session by adding a new #Include and REPORT_HANDLERS line — purely additive, no existing lines touched).

Steps:
1. Via `mcp__Control_your_Mac__osascript`, run: `do shell script "cat '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/watcher.last_started.txt'"` and capture the current "Watcher started:" timestamp as BEFORE_TS.
2. Run: `do shell script "/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\\Documents\\Claude\\Projects\\Bravo Data Extraction\\_restart_watcher.ps1'"`.
3. Sleep 15s, then re-read `logs/watcher.last_started.txt` as AFTER_TS. If AFTER_TS did not advance past BEFORE_TS, wait 15s and re-check once more (watcher startup can take a few seconds).
4. Confirm the restarted watcher's handler list (also printed in watcher.last_started.txt) includes `markdown-verification`. If it does not, the #Include did not load — check for an AHK syntax error; do NOT attempt to fix or touch any other file, just log what you found.
5. Exit silently either way — no Slack post, no DM. This task's only job is to log what happened to its own run output for the parent session to read.