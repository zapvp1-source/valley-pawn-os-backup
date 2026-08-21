---
name: bravo-preflight-relaunch
description: Daily 4:00 AM ET — proactively relaunch Bravo POS + watcher to a clean logged-in state ahead of the 6:50 AM pipeline pull, via the proven _relaunch_bravo_and_watcher.ps1. Verify processes, one retry, DM Joshua only on failure. Replaces the redundant cloud pair nightly-bravo-restart / Bravo Pre-Flight Relaunch (merged 2026-08-21).
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

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file.

This is an automated run of a scheduled task. The user is not present. Execute autonomously. End with <run-summary>one or two sentences</run-summary>.

> **MIGRATION NOTE (2026-08-21):** This task was moved from a claude.ai cloud scheduled task to this local task at Joshua's direction ("all cloud tasks should be moved to local"). The retired cloud trigger is disabled and will be deleted after this task's first clean local runs. Local tool names apply here: `mcp__Control_your_Mac__osascript`, `mcp__Control_Chrome__*`, `mcp__Filesystem__*` — never `mcp__remote-devices__*` (that prefix only exists in cloud sessions).

**CONSOLIDATION NOTE (2026-08-21):** This single local task replaces TWO redundant cloud tasks — "nightly-bravo-restart" (created 7/23) and "Bravo Pre-Flight Relaunch" (created 8/3) — which were word-for-word the same job firing at the same time. One relaunch, once, at 4:00 AM ET.

Proactively relaunch Bravo POS and watcher ahead of the 7 AM daily pipeline exports and daily-loan-inventory-text task. This ensures Bravo is fresh, logged in, and ready before those jobs poll it.

## Steps:

1. **Initial relaunch**: Use osascript to execute the proven Bravo relaunch script via Parallels VM.
   - Command: `do shell script "/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_relaunch_bravo_and_watcher.ps1'"`
   - Run this with a non-blocking background approach and a ~60 second timeout on the call.

2. **Wait and verify**: After ~90 seconds, check that both Bravo.exe and dfsvc.exe processes are running.
   - Command: `do shell script "/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -Command 'Get-CimInstance Win32_Process | Where-Object { \$_.Name -eq \"Bravo.exe\" -or \$_.Name -eq \"dfsvc.exe\" }'"` 
   - Run with ~60 second timeout.

3. **Retry logic**: If processes are not confirmed running, wait 60 seconds and retry the relaunch (step 1) and verification (step 2) exactly once more.

4. **Failure alert**: If Bravo and watcher still are not running after the retry:
   - Send a Slack DM to Joshua (channel ID: D03BHQH5VGT) with this message:
     ```
     ⚠️ Bravo Pre-Flight Relaunch Failed
     
     Two relaunch attempts were made, but Bravo.exe and dfsvc.exe did not start. This may cause the 7 AM pipeline exports and daily-loan-inventory-text task to fail.
     
     Action: Please check the Parallels VM desktop directly to investigate. This failure mode (processes never spawn after relaunch) was observed on 2026-07-21 and 2026-07-23 and is still under investigation.
     ```

5. **Success — stay silent**: If Bravo and the watcher are running (whether after the first attempt or retry), do NOT post anything to Slack. This matches the silent-on-success pattern used by bravo-health-watchdog.

## Important notes:
- Do not modify, edit, or touch any files.
- This task only invokes the existing _relaunch_bravo_and_watcher.ps1 script and reports the outcome.
- Use non-blocking/background osascript calls to avoid hangs; poll with timeout.
- If you cannot execute the osascript commands or cannot reach the VM, report that clearly to Joshua via Slack: "Pre-flight relaunch could not be attempted — osascript/Parallels access failed" so he knows the 7 AM jobs are at risk.
