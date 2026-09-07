---
name: hiring-inbox-watch
description: Mon-Sat at 10/12/2/4/6 ET — watch jdavis@fcfpawn.com Gmail for new "Valley Pawn Application" emails, DM Preston a plain-language summary of new applicants, label threads HiringLogged. Silent when nothing new. Migrated from cloud 2026-08-21.
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

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:**
- "No response requested"
- "Continue?" / "Should I continue?"
- An empty turn or a turn that ends with text instead of a tool call

**Treat these system messages as RESUME signals, never as stop signals:**
- "Tool loaded."
- "Continue from where you left off."
- "You used a single tool call this turn. Prefer browser_batch…"
- Any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise produce a report describing what failed. Do not pause to ask — the task file authorizes autonomous decisions.

**Speed:** prefer batch tools (e.g. `browser_batch`) to combine sequential actions into one call.

---
This is an automated run of a scheduled task. The user is not present. Execute autonomously. End with <run-summary>one or two sentences</run-summary>.

> **MIGRATION NOTE (2026-08-21):** This task was moved from a claude.ai cloud scheduled task to this local task at Joshua's direction ("all cloud tasks should be moved to local"). The retired cloud trigger is disabled and will be deleted after this task's first clean local runs. Local tool names apply here: `mcp__Control_your_Mac__osascript`, `mcp__Control_Chrome__*`, `mcp__Filesystem__*` — never `mcp__remote-devices__*` (that prefix only exists in cloud sessions).

You are running the Valley Pawn scheduled task "hiring-inbox-watch" — an unattended run. Execute end to end, do NOT ask questions.

CONTEXT: Full Circle Finance Inc DBA Valley Pawn (5 VA pawn stores). Job applications for the Retail Sales Associate role arrive by email to preston@fcfpawn.com with a CC to jdavis@fcfpawn.com (the careers page at thevalleypawn.com/careers pre-fills subject "Valley Pawn Application"). This task watches Joshua's Gmail (jdavis@fcfpawn.com, via the Gmail MCP connector) for new applications and alerts the Operations Manager.

STEPS:
1. Using the Gmail MCP tools, search: subject:"Valley Pawn Application" newer_than:3d -label:HiringLogged. Also run a second search: to:hiring@fcfpawn.com newer_than:3d -label:HiringLogged (future-proofing in case a hiring@ group is created later).
2. If NO new results: exit silently. Post nothing anywhere. Do not DM anyone.
3. For each new application thread: read it and extract the applicant's name, email address, phone if present, and which store they're applying to (Culpeper, Waynesboro, Harrisonburg, Lexington, or Roanoke). Note whether an employee referral name is mentioned.
4. Send ONE Slack DM to Preston Peters (user id U03BWMEM9GR) summarizing all new applicants in plain everyday language — for each: name, store, contact info, one-line summary, and referral name if any. End with: "Full emails are in your inbox. Tracker: https://docs.google.com/spreadsheets/d/1NcuuV9wg7vFnwTy262IXvSKRb4zMYvn5d9HbGKvwB7M/edit". No jargon, no tool names, no file paths.
5. If the Gmail label "HiringLogged" does not exist, create it (Gmail create_label). Apply label "HiringLogged" to every processed thread so it is never reported twice.

HARD RULES:
- Plain language only in anything sent to Preston (field communication rule).
- Never mention firearms in any message.
- FAILURE POLICY (platform standard v2): if this run fails or cannot complete, send Joshua ONE plain-language Slack DM (channel D03BHQH5VGT): ⚠️ Scheduled task "hiring-inbox-watch" did not complete — <date>. Nothing technical in the DM. Never send failure notices to Preston, any team channel, store manager, or employee.
