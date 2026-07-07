---
name: weekly-payroll-to-qbo
description: Pull processed payroll from Gusto after each weekly pay run, build journal entries by store class, save to Google Drive, and DM Joshua on Slack.
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are automating the weekly payroll journal-entry pipeline for Valley Pawn (Full Circle Finance Inc). The goal is to pull the most recently processed payroll from Gusto, break it down by store location (QBO class), and produce a journal entry CSV that Joshua can import into the new QBO company "Valley Pawn – Cowork Books."

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

## Context
- Valley Pawn has 5 store locations that map to QBO Classes: Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke
- Gusto is connected to the OLD bookkeeper's QBO — NOT the new Cowork Books QBO
- This task bridges the gap by pulling payroll data from Gusto's API and formatting it for manual import into the new QBO
- Joshua's Slack user ID: U03BB52MDSA

## Steps

### 1. Get the latest processed payroll
Use `list_payrolls` with `processing_statuses=processed`, `sort_order=desc`, `include=totals` to find the most recently processed regular payroll. Grab its UUID and check_date.

If the most recent payroll check_date is older than 10 days, skip this run and DM Joshua on Slack: "No new payroll found this week — skipping journal entry generation."

### 2. Get payroll details
Use `get_payroll` with the payroll UUID to get the full breakdown of employee compensations including:
- Gross pay (wages/salaries by type)
- Employee taxes withheld
- Employer taxes
- Employee deductions (benefits, retirement, etc.)
- Employer benefit contributions
- Net pay

### 3. Map employees to store locations
Use `list_employees` to get all active employees. For each employee in the payroll, use `get_employee` (with include=all_compensations) or `list_employee_work_addresses` to determine their work location. Map each work location city/address to the correct QBO class:
- Culpeper, VA → Culpeper
- Waynesboro, VA → Waynesboro
- Harrisonburg, VA → Harrisonburg
- Lexington, VA → Lexington
- Roanoke, VA → Roanoke
If an employee's location doesn't match any of these, flag them as "Unassigned" for Joshua to review.

### 4. Build journal entry by class
Aggregate the payroll data by class (store location). For each class, calculate:
- Debit: Payroll Expenses (wages, employer taxes, employer benefit contributions)
- Credit: Payroll Liabilities (employee taxes withheld, employee deductions)
- Credit: Cash/Bank (net pay — map to WF Checking 2797 which is the payables account)

Format as a QBO-importable journal entry CSV with columns:
*Date, Journal Entry No, Account, Debits, Credits, Description, Class*

Use the payroll check_date as the journal entry date. Use "PR-" plus the check_date (e.g., "PR-2026-04-09") as the journal entry number.

### 5. Save to Google Drive
Save the CSV file to the Google Drive Bookkeeping folder. The file should be named: `Payroll JE - YYYY-MM-DD.csv` (using the check_date).

To save to Google Drive, write the file to the workspace folder at:
`/sessions/relaxed-quirky-pascal/mnt/Claude 4 back up/Payroll JE - YYYY-MM-DD.csv`

Also save a human-readable summary as a markdown file alongside it:
`/sessions/relaxed-quirky-pascal/mnt/Claude 4 back up/Payroll Summary - YYYY-MM-DD.md`

The summary should include:
- Pay period dates and check date
- Total gross pay, total taxes, total deductions, total net pay
- Breakdown by store class
- Any employees flagged as "Unassigned"

### 6. Notify Joshua on Slack
Send a DM to Joshua (U03BB52MDSA) on Slack with a brief summary:
- "Payroll JE ready for [check_date]"
- Total gross pay and net pay
- Per-store breakdown (one line each)
- Note if any employees couldn't be mapped to a store
- Remind him to import the CSV into QBO Cowork Books

## Error Handling
- If Gusto API times out, retry once after 30 seconds. If it fails again, DM Joshua: "Gusto API is down — I'll retry next run."
- If employee location mapping fails for more than 3 employees, DM Joshua to review the mapping manually.
- Never modify any data in Gusto or the existing QBO — this is read-only.

## Success Criteria
- CSV file saved to workspace folder
- Summary markdown saved alongside it
- Slack DM sent to Joshua with the summary
