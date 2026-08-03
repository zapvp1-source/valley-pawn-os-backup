---
name: sunday-checklist-summary
description: Every Sunday 8 PM: summarize Preston's #in-store-checklists notes by store for the prior Mon–Sat and log TODOs into Apple Reminders.
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


You are running an automated weekly review for Joshua Davis (CEO of Valley Pawn / Full Circle Finance Inc). This runs every Sunday at 8:00 PM ET. Be fully autonomous — do not ask questions, just complete the work.

GOAL
Review the past week of the Valley Pawn "in-store checklists" Slack channel, summarize by store what Preston Peters (Operations Manager) talked about, identify any TO-DOs, and log those TO-DOs into Apple Reminders.

STEP 1 — Determine the date window.
The window is LAST WEEK, Monday through Saturday (the most recent Mon–Sat that just ended before this Sunday run). Use a bash `date` call to compute the exact dates. Example: if today is Sunday 2026-06-28, the window is Mon 2026-06-22 through Sat 2026-06-27. Note the window explicitly in your summary.

STEP 2 — Read the Slack channel.
Channel: #in-store-checklists, channel ID `C0B5Q65QZUJ` (private). Use the Slack MCP tool `mcp__f92ce7c6-0353-4419-8491-f0843b182ff2__slack_read_channel` to read messages in the window, and `slack_read_thread` to expand any threaded replies. Focus on messages from Preston Peters (Slack user `U03BWMEM9GR`, preston@fcfpawn.com) — what he flagged, asked for, instructed, or noted. Include relevant replies/context from store employees when they clarify a Preston item.

STEP 3 — Summarize by store.
Group Preston's notes under each of the 5 stores:
- Culpeper
- Waynesboro
- Harrisonburg
- Lexington
- Roanoke
For each store, write a short bullet summary of what Preston discussed that week. If a note is company-wide (not store-specific), put it under a "Company / All Stores" heading. If a store had nothing, say "No notes this week."

STEP 4 — Extract TO-DOs and classify each.
For every actionable item Preston raised, classify it as either:
  (A) CORPORATE / COMPANY deliverable — something Joshua or the corporate office owns (e.g., order signage company-wide, fix a policy, vendor/payroll/marketing/IT items, anything not a single-store floor task).
  (B) STORE / EMPLOYEE deliverable — a task a specific store or its employees must do (e.g., "Lexington needs to redo the jewelry case," "Roanoke clean the back room").
Write a clear, action-oriented reminder title for each (start with a verb; include the store name in store items, e.g. "Lexington: re-merchandise jewelry case"). If a due date is implied, include it.

STEP 5 — Log TO-DOs into Apple Reminders (via `mcp__Control_your_Mac__osascript`).
First enumerate the existing Reminders lists so you use exact names:
  `tell application "Reminders" to get name of lists`
- CORPORATE deliverables → add to the list named exactly **"Preston Joshua"**.
- STORE deliverables → add to that store's own sub-list (under the "Stores" group). Match the store name (Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke) to the closest existing list name. If you cannot find a matching store list, add it to "Preston Joshua" instead with the store name prefixed in the title, and note this fallback in your summary.

To add a reminder, use AppleScript like:
  tell application "Reminders"
    set theList to list "Preston Joshua"
    make new reminder at end of theList with properties {name:"<title>", body:"From #in-store-checklists week of <window>. <context>"}
  end tell
(Substitute the correct list name per item.) Add a body note referencing the source channel and week so the item has context.

IMPORTANT — Reminders permission: this Mac may need automation access granted for the Reminders app the first time. If the osascript calls error with a permissions/automation failure, DO NOT silently fail. Instead: (a) still produce the full summary and the complete TODO list (clearly grouped into Corporate vs each store) in your output so nothing is lost, and (b) state clearly at the top of the output that reminders could not be written because Reminders automation access needs to be approved on the Mac, and the listed items should be added manually or the task re-run once access is granted.

STEP 6 — Output.
Produce a clean summary report with: the date window; per-store sections of what Preston discussed; a "TO-DOs Logged" section listing each reminder created and which Reminders list it went into (Corporate vs store sub-list); and any fallback/permission notes. This output is delivered to Joshua as the run notification.

Do not post anything back into the Slack channel. Do not message employees. The only writes you perform are to Apple Reminders.