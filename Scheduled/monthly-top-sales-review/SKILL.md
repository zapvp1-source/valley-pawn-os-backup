---
name: monthly-top-sales-review
description: Monthly Valley Pawn top-sales review: export prior month's sales from Bravo POS per store, compute top 5 categories and top 20 items (per-store + company-wide), save a Google Doc report and XLSX, and post summary to #store-performance.
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


> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

Run Valley Pawn's monthly top-sales review for the prior calendar month. This is a recurring scheduled task — execute end-to-end without user input unless a step is blocked.

OBJECTIVE
Export sales data from Bravo POS for every Valley Pawn store, then publish the Top 5 Sales Categories and Top 20 Items Sold for (a) each individual store and (b) the company as a whole. Deliver a Slack summary and a Google Doc report, and archive an XLSX with the raw rankings.

REPORTING WINDOW
- Cover the FULL prior calendar month (1st through last day). Compute this from today's date at runtime.
- Example: if today is 2026-05-01, the window is 2026-04-01 through 2026-04-30.

STEPS

1. LOAD CONTEXT
   - Invoke the valley-pawn-context skill to get the canonical store list, store IDs, and brand details.
   - Confirm the 5 Valley Pawn stores and their Bravo identifiers.

2. PULL SALES DATA FROM BRAVO (per store)
   - Invoke the bravo-store-cycle skill to log into each of the 5 stores in the Bravo POS desktop app (running in Parallels).
   - In each store, navigate to Reports → Sales (or the equivalent "Items Sold" / "Category Sales" report) and run for the prior-month date range.
   - Export the report to CSV/XLSX. Save each export to /sessions/optimistic-loving-sagan/mnt/outputs/monthly-top-sales/<YYYY-MM>/raw/<store-slug>.xlsx (or .csv).
   - If a store's report cannot be exported after two attempts, note the failure and continue — include the gap in the final summary.

3. COMPUTE RANKINGS
   - For each store: Top 5 categories by gross sales $, and Top 20 items by gross sales $ (include units sold as a secondary column).
   - For the company: aggregate all 5 stores, then Top 5 categories and Top 20 items by combined gross sales $.
   - Columns to include per ranking row: rank, name (category or item), gross sales $, units sold, % of store (or company) total.

4. BUILD THE XLSX ARCHIVE
   - Follow the xlsx skill.
   - Create /sessions/optimistic-loving-sagan/mnt/outputs/monthly-top-sales/<YYYY-MM>/valley-pawn-top-sales-<YYYY-MM>.xlsx with sheets:
     • "Company Top 5 Categories"
     • "Company Top 20 Items"
     • One "<store> Top 5 Cats" sheet per store
     • One "<store> Top 20 Items" sheet per store
     • "Raw" sheet with the combined line-item data used for the rollups.

5. BUILD THE GOOGLE DOC REPORT
   - Use the Google Drive MCP (mcp__2ce817f2-5038-4cde-a6ab-8dedbe8abd84__*) to create a Google Doc named "Valley Pawn — Top Sales Review — <Month YYYY>" in the appropriate monthly-reports folder (search for an existing "Monthly Reports" or "Sales Reports" folder; if none, create at Drive root).
   - Structure:
     • Header: month + reporting window + "Top Sales Review"
     • Section: Company Top 5 Categories (table)
     • Section: Company Top 20 Items (table)
     • For each store: Top 5 Categories table + Top 20 Items table
     • Notes: any stores with missing/partial exports, any anomalies worth a manager's eye (sharp category drops, one-off big-ticket items skewing the list, etc.)

6. POST SLACK SUMMARY
   - Channel: #store-performance (ID C03CGTN3KN1).
   - Use mcp__f92ce7c6-0353-4419-8491-f0843b182ff2__slack_send_message.
   - Format (Slack mrkdwn):
     • Title line: ":chart_with_upwards_trend: *Valley Pawn — Top Sales — <Month YYYY>*"
     • Company Top 5 Categories (rank, name, $ gross)
     • Company Top 20 Items (rank, name, $ gross, units)
     • A single-line highlight per store: top category + top item
     • Link to the Google Doc
     • Link to the XLSX in the outputs folder (computer:// link)
     • Flag any export failures

7. VERIFY
   - Re-open the Google Doc and confirm all 5 stores + company tables are present and non-empty.
   - Confirm the Slack message posted successfully (check the response ts).
   - If anything is missing, fix and re-post / re-edit.

CONSTRAINTS & PREFERENCES
- Prefer MCP connectors (Slack, Google Drive) over browser automation and computer use. Only use computer-use for Bravo POS itself (it has no API/MCP).
- Keep the Slack message readable on mobile — use short lines and Slack mrkdwn, not full Markdown.
- Currency in USD, rounded to whole dollars in Slack; full precision in the XLSX.
- If the prior month had any store openings/closings, note it in the doc's Notes section.

SUCCESS CRITERIA
- XLSX archive saved under /sessions/optimistic-loving-sagan/mnt/outputs/monthly-top-sales/<YYYY-MM>/
- Google Doc created and populated with company + per-store rankings
- Slack message posted to #store-performance with both links
- Any data gaps or failures explicitly called out rather than silently dropped