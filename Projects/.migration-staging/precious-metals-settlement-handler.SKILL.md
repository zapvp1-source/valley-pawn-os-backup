---
name: precious-metals-settlement-handler
description: Daily 9:00 AM ET — Precious Metals Settlement handler: follow the OPERATING_GUIDE in the Precious Metals Settlements project exactly (archive CLOSED workbooks, find new Elemetal settlement emails, allocate by Bravo scrap weights, write REVIEW workbook for Joshua). Silent on no-op runs. Migrated from cloud 2026-08-21.
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

You are running the daily Precious Metals Settlement automation for Valley Pawn (Full Circle Finance Inc).

First, read the full operating guide at this path on Joshua's Mac Studio using the local Control your Mac osascript tool (`mcp__Control_your_Mac__osascript`) with a `do shell script "cat '/Users/joshuadavis/Documents/Claude/Projects/Precious Metals Settlements/OPERATING_GUIDE.md'"` command:

/Users/joshuadavis/Documents/Claude/Projects/Precious Metals Settlements/OPERATING_GUIDE.md

Then follow that guide's procedure exactly, step by step, in order. It covers: loading state, checking for any pending CLOSED workbook to archive to Google Drive and notify Slack (#gold-trend-), determining the target settlement month, searching Gmail (jdavis@fcfpawn.com) for new Elemetal settlement emails, downloading and reading settlement PDFs via the local Chrome tools + osascript + the Read tool, classifying each settlement (including detecting blended/combined stones+no-stones settlements using Bravo's Status column), loading Bravo scrap-refining-gold weight data for the relevant store buckets, calculating each store's proportional dollar allocation, writing a REVIEW workbook for Joshua's approval, and updating the state file.

Do NOT do anything related to QuickBooks or the general ledger — that is fully out of scope and handled separately by Joshua's existing monthly Bravo GL pull.

If there is nothing new to do this run (no new settlement emails, no pending CLOSED file to archive), just update the state file if needed and end quietly — do not post Slack noise for routine no-op runs. Only report/notify when there is a new REVIEW workbook generated for Joshua's review, or a CLOSED workbook has been archived and Slack-notified.
