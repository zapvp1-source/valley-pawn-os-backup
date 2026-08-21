---
name: quarterly-capex-sweep
description: Quarterly (1st of Jan/Apr/Jul/Oct, 9 AM ET) — capital-improvements sweep across the 5-property real estate portfolio: scan GDrive + iCloud for new capex docs, update each CAP GAIN Improvements tracker, flag unconfirmed items for Joshua. Migrated from cloud 2026-08-21.
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

Run the quarterly capital-improvements (capex/cost-basis) sweep for Joshua Davis's real estate portfolio (Farming Infinity LLC / Full Circle Finance Inc). This is a recurring maintenance task — work fully autonomously, no check-ins.

Read project memory file "file-organization.md" first for full context on the folder structure, the 5 owned properties, and the CAP GAIN Improvements tracker convention (each property has 02 Real Estate/[Property]/07 Improvements & Maintenance/[house#] CAP GAIN Improvements/ with an xlsx tracker — note 844's folder is spelled "844 Cap Gain Improvemnts").

The 5 properties: 817 Richmond Rd - Staunton VA (Commercial), 282 Bald Rock Rd - Verona VA (Rental), 844 Cypress Crossing Trail - FL (Home), 148 Hardinberry St - Oak Ridge TN (Rental), 14300 Woods Walk Ln - Midlothian VA (Rental).

For each property:
1. Scan that property's Google Drive folder tree AND its iCloud Drive counterpart (`~/Library/Mobile Documents/com~apple~CloudDocs/02 Real Estate/[property]/`) for any NEW capital-improvement documents (paid invoices, signed contracts, receipts, cashier's checks) added/modified since the last sweep — look for file modification dates in roughly the last 3-4 months, but also do a light pass over anything you may have missed before.
2. Also check the GDrive "00 Inbox/Desktop Documents Import (Needs Sorting)" and "00 Inbox/Desktop Spreadsheets Import (Needs Sorting)" folders, and iCloud "03 Personal/00 Inbox/Desktop Info Import (Needs Sorting)", for anything new that matches a property by address.
3. Read the existing tracker xlsx for each property FIRST (read/stage the file first) before writing, to see what's already logged — never duplicate existing rows. Only touch ONE tracker file at a time, fully saving and confirming the write before moving to the next property, to avoid a lost-update race condition (this has happened before when two writes hit the same file close together).
4. Log genuine NEW capital improvements only (not routine repairs/maintenance). Mark clear paid/signed items as confirmed; mark quotes/estimates/unsigned/unpaid items as "NEEDS JOSHUA CONFIRMATION" in the Notes column — never fabricate a dollar amount.
5. Copy (never move/delete) new qualifying source documents into that property's CAP GAIN Improvements folder.
6. Update each tracker's TOTAL SUM formula range to include new rows, then write the updated tracker back to the original path (local file tools / osascript), verifying the write.
7. Update project memory file-organization.md with anything material learned.

At the end, post a short summary directly to Joshua (this session's output) covering: how many new items were found and logged per property, dollar amounts, anything flagged NEEDS JOSHUA CONFIRMATION, and confirm no duplicate rows were created. If nothing new was found anywhere, say so briefly — don't pad the report. Keep it tight; Joshua does not want a recap of prior quarters' work, just what's new this quarter.
