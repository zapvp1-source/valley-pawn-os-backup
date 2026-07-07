---
name: weekly-timekeeping-analysis
description: Monday 2 AM (overnight) — pull Gusto Time Tracking via Chrome (MCP returns empty), post a CONCISE store-by-store summary to #timekeeping-summary at 9 AM Monday.
model: claude-sonnet-5
---


> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

Pull last week's timekeeping data from Gusto and post a store-by-store summary WITH per-employee breakdown and call-outs to Slack #timekeeping-summary, scheduled for 9 AM Monday.

Steps:
1. Determine the prior work week. Gusto's pay period runs Monday–Sunday. Use the most recent completed Mon–Sun period (the week that ended yesterday). Label the report with that exact date range.

2. Pull Gusto Time Tracking data via Chrome browser (the Gusto MCP `list_time_sheets` returns empty for Time Tracking, so use claude-in-chrome). Navigate Gusto → Time & attendance → Time tracking → click "Review" on the most recent pay period. The Timesheets page lists every employee with Total hrs, Regular hrs, Overtime, PTO, Approval status, and flags like "Break violations". Capture all of them via `get_page_text`.

3. Map each employee with hours to a store. The Timesheets page does NOT show location, so for each employee in the table call the Gusto MCP `list_employee_work_addresses` (parallel batch). Use the entry where `active: true` — that location_uuid maps to one of Valley Pawn's 5 stores (Harrisonburg, Culpeper, Roanoke, Waynesboro, Lexington). Corporate employees (Joshua, Hillary) and salaried managers with 0h tracked can be noted briefly or omitted from per-store totals.

4. Build the Slack message. REQUIRED structure — do NOT drop any of these:
   a. Header line with date range (e.g. "*Weekly Timekeeping — Mon May 11 – Sun May 17, 2026*") and a one-line subtitle with total approved timesheets and total tracked hours across all stores.
   b. One block per store, sorted by total hours desc. Each block:
      - Bold store name + total hours + employee count
      - **Per-employee breakdown** — every employee listed by name with their hours, OT in parens, and any flag (⚠️ break violations, missed clock-outs, "new hire, started M/D", "mgr, salaried", etc.). One bullet per employee.
   c. A "*Heads-up:*" / call-outs block at the bottom summarizing anomalies across stores:
      - Total break violations and who
      - OT count (how many of the hourly staff hit OT)
      - Coverage gaps (stores with only 1 person clocked in all week)
      - New hires that started this week
      - Anything else worth a manager's eye
   Keep formatting tight (bullets, bold headers, no walls of text) but do NOT collapse the per-employee detail or the call-outs — Joshua wants both every week.

5. Use `slack_schedule_message` to post it to #timekeeping-summary (channel ID C0AN6TNA4ES) at 9:00 AM Monday local time. Do not post elsewhere and do not DM Joshua.

6. If Gusto is inaccessible or data is missing, post a short note to #timekeeping-summary explaining what failed so the team knows the report is delayed.

Channel: #timekeeping-summary (C0AN6TNA4ES) — NOT #claude-updates (that was the old destination).

<!-- migrated to working model 2026-06-15 -->