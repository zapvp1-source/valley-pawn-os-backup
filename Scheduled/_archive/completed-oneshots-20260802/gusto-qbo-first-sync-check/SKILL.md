---
name: gusto-qbo-first-sync-check
description: One-time Friday 6/12 check: verify the first Gusto→QBO synced payroll JE landed in the new Store/Corp Payroll accounts
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


One-time verification task for Joshua's Valley Pawn books (read the qbo-context skill first; work ONLY in the jdavis@fcfpawn.com QBO account, NEVER zapvp1).

Context: On 6/11/26 the chart of accounts was restructured (Store Level Expenses / Corporate Expenses parents) and the Gusto↔QBO connector was fully mapped (wages → Store Level Expenses:Store Payroll:Wages & Salaries, etc.). Gusto auto-sync is ON, JE consolidation by employee. The 6/12 payroll (~$13,496.50, debit from WF 2797) is the first pay run under the new mapping.

Do: Open QBO (jdavis account) via Claude in Chrome. Find the Gusto payroll journal entry dated ~6/12 (search recent journal entries / recent transactions). Verify: (1) it synced at all; (2) wage/tax/benefit lines hit the NEW accounts under Store Level Expenses:Store Payroll (not old Payroll Expenses accounts); (3) whether lines carry Classes (likely not yet — per-employee class overrides in Gusto are still pending due to a Gusto UI bug).

Report findings as a Slack DM to Joshua (U03BB52MDSA): synced yes/no, accounts correct yes/no, classes present yes/no, plus the JE total. If the JE did NOT sync or hit wrong accounts, say exactly what's wrong — do not attempt fixes.