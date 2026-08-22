---
name: vp-publer-analytics-friday
description: Friday 4 PM ET — Publer API weekly performance digest: top/bottom 20% by engagement, writes weekly-adjustments.json for Monday's batch, DMs Joshua a one-line digest. Replaces the broken Meta Graph analytics loop.
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


This is an automated run of a scheduled task. The user is not present. Execute autonomously. End with <run-summary>one or two sentences</run-summary>.

⚠️ FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE. If the digest cannot be produced, stay silent on Slack; explain in the run-summary only (Claude self-heals via completion notification). Joshua gets exactly one DM, and only on success.

## Job
Close Valley Pawn's weekly content loop using PUBLER's analytics API (the Meta Graph API path is retired/blocked — never use it, never browser-fallback to instagram.com/facebook.com).

## Steps
1. Run the digest via the Control-your-Mac osascript tool:
   `do shell script "cd ~/Documents/Claude/Projects/'Refine Social Media' && python3 publer_weekly_digest.py 2>&1 | tail -15"`
2. The script pulls last-7-day post-level insights across all connected Publer accounts, ranks by engagement, identifies top/bottom 20%, classifies content types, and writes:
   - `friday_digests/friday_digest_{date}.md` (full report)
   - `weekly-adjustments.json` (Monday's vp-content-batch-weekly reads this — the adjust loop)
   - appends to `adjustments_log.jsonl` and `~/.vp-studio/lessons.md`
3. Its LAST stdout line starts with "DIGEST:". DM exactly that line (minus the "DIGEST: " prefix) to Joshua Davis on Slack (find him via user search), prefixed with "📊 Weekly social digest — ".
4. If the line says no insights were available (Publer analytics can lag 24-48h), do NOT DM Joshua — note it in run-summary only.
5. Sanity check: confirm weekly-adjustments.json was updated today (osascript: `do shell script "stat -f '%Sm' ~/Documents/Claude/Projects/'Refine Social Media'/weekly-adjustments.json"`). If not, treat as failure (silent).

Guardrails: Publer API only. No Meta Graph API. No instagram.com/facebook.com browsing. Do not modify the digest script during a run — if it errors, report in run-summary and let interactive Claude fix it.
