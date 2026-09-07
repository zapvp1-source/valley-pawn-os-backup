---
name: bonus-payday-prep
description: First Friday after the 15th, 7:00 AM. If Joshua replied "approve" to the month-close DM, stages the bonus amounts on that week's unprocessed Gusto payroll for him to submit. Never submits payroll, never posts to a team channel. Bravo type — none (no Bravo contact).
model: claude-sonnet-5
schedule_suggestion: "0 7 * * 5"  # every Friday; the task itself no-ops unless today is the first Friday after the 15th
---

> NOT REGISTERED — creating this task autonomously was blocked by the permission classifier on
> 2026-09-06 (it stages amounts on a payroll). Joshua registers it with one click, or tells a
> session to try again. Until it exists, `bonus-month-close` still produces
> `out/<MONTH>/gusto_lines.csv` and Joshua enters the bonus lines in Gusto himself.

Valley Pawn bonus payday prep. Autonomous, non-interactive.

HARD RULES
- Output goes ONLY to Joshua's DM (D03BHQH5VGT). Never a team channel, never a manager, never an employee.
- NEVER submit or process payroll. You may only stage bonus amounts as inputs on an unprocessed payroll. Joshua submits it himself.
- If anything is ambiguous or a required input is missing, touch nothing in payroll and DM Joshua one plain sentence.

STEPS
1. If today is NOT the first Friday after the 15th of the month, end the run silently.
2. MONTH = the month whose bonus is paid today (the month that closed on the 1st, YYYY-MM).
3. Read `/Users/joshuadavis/Documents/Claude/Projects/Bonus Program/out/<MONTH>/gusto_lines.csv` via mcp__Control_your_Mac__osascript. If it does not exist, DM Joshua "The <Month> bonus numbers aren't ready yet, so nothing has been loaded into payroll." and stop.
4. Check for approval: read the DM history with Joshua (slack_read_channel on D03BHQH5VGT, last ~40 messages) for a reply of "approve" (or an unmistakable equivalent) AFTER the month-close DM for <MONTH>. No approval, or "hold" → load NOTHING and DM: "Reminder — the <Month> bonus of $X is still waiting on your OK. Nothing has been loaded into payroll." Stop.
5. If approved: exclude any line marked held=Y (numbers the engine could not stand behind); name them in the DM.
6. Gusto: `list_payrolls` processing_statuses=unprocessed, find the payroll whose check_date is today. Use `update_payroll` to add each employee's bonus amount as a Bonus earning with the memo from the CSV. Do not touch hours, PTO, or anything else. Do NOT call run_payroll.
7. DM Joshua: the per-employee list staged, the total, anything skipped, and "Loaded into today's payroll as bonus lines — you still have to hit submit in Gusto."
8. Append a dated line to `Bonus Program/RUN_LOG.md`.
