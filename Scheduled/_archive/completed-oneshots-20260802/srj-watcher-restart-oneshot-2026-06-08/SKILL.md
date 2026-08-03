---
name: srj-watcher-restart-oneshot-2026-06-08
description: One-shot watcher restart to activate SafeRegisterJournal CS-toggle patch (mirrors monday-bravo-combined-run preflight Check 2 path).
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


> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


One-shot job: restart the Bravo watcher so it picks up the patched SafeRegisterJournal.ahk handler, then verify it took.

CONTEXT
- Patched handler is on disk at /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/reports/SafeRegisterJournal.ahk. Backup at SafeRegisterJournal.ahk.bak-pre-cs-toggle-2026-06-08.
- The running watcher has the OLD code in memory (#Include compiles at script start).
- A prior session tried prlctl exec from an interactive osascript shell and it hung on terminal grab (BRAVO_KNOWN_ISSUES.md). Scheduled-task sessions run prlctl successfully (monday-bravo-combined-run Check 2 does this every Monday).

STEPS
1. Read /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/logs/watcher.last_started.txt and remember the timestamp on line 1.
2. Run via osascript do shell script:
   /usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_restart_watcher.ps1'
   This is the canonical restart pattern from Scheduled/monday-bravo-combined-run/SKILL.md Check 2. The .ps1 creates Windows scheduled tasks to map Y: and launch AHK in joshuadavis's interactive session, so the AHK process runs in the right context.
3. Sleep 15 seconds, then read watcher.last_started.txt again. The line-1 timestamp should be NEWER than what you saw in step 1. If not, sleep another 15s and try once more. If still unchanged, post failure to Slack DM U03BB52MDSA with the prlctl output and stop.
4. On success: drop a single-store smoke trigger at /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/srj-cs-fix-postrestart-2026-06-08T14-50-00.json with body:
   {"id": "srj-cs-fix-postrestart-2026-06-08T14-50-00", "requested_at": "2026-06-08T14:50:00-04:00", "reports": [{"name": "safe-register-journal", "stores": ["WAY"], "date": "2026-06-07"}]}
5. Poll every 30s for up to 8 min for /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/srj-cs-fix-postrestart-2026-06-08T14-50-00.result.json.
6. When result lands, read the corresponding log file at logs/srj-cs-fix-postrestart-2026-06-08T14-50-00.log and grep for "[pre-export] Continuous Scrolling". Two outcomes worth reporting:
   - SUCCESS WITH CS LINE: post to Slack DM U03BB52MDSA — "SRJ CS-toggle patch is LIVE — saw '[pre-export] Continuous Scrolling ... post-toggle state = 0' in the log, cell SUCCESS." Patch confirmed.
   - SUCCESS WITHOUT CS LINE: rare — means CS was already off. Still a working cell. Note that the post-toggle line was absent.
   - FAILURE: include the last 20 lines of the log + the result.json.
7. Also: delete the leftover trigger /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/srj-cs-fix-smoke-2026-06-08T14-27-00.json if it's still sitting unclaimed at top-level (a prior session dropped it before the watcher died). Use osascript do shell script "rm -f '...'" — never the Write tool, the pipeline folder is outside this task's sandbox.

OUTPUT
Post the final result as a Slack DM to U03BB52MDSA. Single message, concise — what happened, whether the patch is live, what to do next if not.