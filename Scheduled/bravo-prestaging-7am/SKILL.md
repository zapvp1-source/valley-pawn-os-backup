---
name: bravo-prestaging-7am
description: Bravo pre-staging relaunch + verification before the 7 AM pipeline exports
---

Run Bravo pre-staging for the 7 AM pipeline exports. This task runs on the user's computer and has full access to Parallels and osascript (use the mcp__Control_your_Mac__osascript tool, or equivalent osascript MCP tool if the name differs).

Steps:
1. Execute the relaunch script via prlctl. Use an AppleScript "do shell script" call (NOT a shell command that itself invokes osascript -e with nested quoting — just pass the shell command directly as the script argument to the osascript tool, escaping double quotes as \" and backslashes as \\ within the AppleScript string). The shell command to run is:
/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_relaunch_bravo_and_watcher.ps1'
Wrap it as: do shell script "<command with internal double quotes escaped as \" and backslashes escaped as \\>" with timeout 120
2. Wait 90 seconds for Bravo to launch.
3. Verify both Bravo.exe and dfsvc.exe are running via prlctl. Shell command:
/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'Bravo.exe' -or $_.Name -eq 'dfsvc.exe' }"
Wrap similarly as a "do shell script ... with timeout 60" AppleScript call, being careful with the nested double quotes around the PowerShell -Command argument (escape them as \" ) and the $_ variable references (no special AppleScript escaping needed for $, but make sure the PowerShell single/double quote structure survives — using \" for the outer PowerShell string boundaries).
4. If both processes are running → SILENT SUCCESS (do not post to Slack, do not message Joshua).
5. If NOT running → wait 60 seconds, retry the relaunch exactly once (repeat step 1), then verify again (step 3).
6. If still not running after the retry → send a Slack DM to Joshua (channel_id D03BHQH5VGT) via the Slack MCP send-message tool:
"⚠️ Bravo pre-staging failed — 2 relaunch attempts did not bring up Bravo.exe/dfsvc.exe. Today's 7 AM pipeline exports and daily-loan-inventory-text may fail. Check the VM desktop directly. (This matches the 2026-07-21 and 2026-07-23 failure mode — not yet understood.)"
7. Do not modify any files. This task only runs the existing _relaunch_bravo_and_watcher.ps1 script and reports outcome. Follow the Valley Pawn Failure Alert Policy v2: on failure, send ONE plain-language Slack DM to Joshua (D03BHQH5VGT) only — never post to any team/store channel. On success, do nothing (no Slack post).