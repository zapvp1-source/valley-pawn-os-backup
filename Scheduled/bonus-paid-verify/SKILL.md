---
model: claude-sonnet-5
name: bonus-paid-verify
description: Monday after bonus payday, 10:00 AM. Compares what the bonus ledger says was owed against what Gusto actually paid, and DMs Joshua only if they disagree. Closes the month in the ledger. Never posts to a team channel.
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Valley Pawn bonus PAID verification — the safety net that catches a month whose bonus was computed but never actually paid. Autonomous, non-interactive, read-only.

FIRST: this runs every Monday but only does work on the Monday AFTER a bonus payday (payday = the first Friday after the 15th). Look at `/Users/joshuadavis/Documents/Claude/Projects/Bonus Program/out/*/close.json` (via mcp__Control_your_Mac__osascript) and find the close whose `payday` value is the Friday just gone. If there isn't one, do nothing at all — no DM, no file writes — and end the run.

HARD RULES
- Output ONLY to Joshua's DM (D03BHQH5VGT). Never a team channel, never a manager or employee. Never change anything in Gusto.
- Plain language only — no error text, no jargon, no file paths.

STEPS
1. MONTH = the earning month of that close.
2. Expected: its `total_payout` and per-employee lines (`out/<MONTH>/gusto_lines.csv`), excluding any line marked held=Y.
3. Actual: Gusto `list_payrolls` with processing_statuses=processed covering that payday, include=totals; then `get_employee_earnings_summary` for the same window for per-employee bonus amounts.
4. Compare. If the totals match within a dollar, DM one short line: "<Month> bonuses paid — $X to N people, matches what we calculated." If they do NOT match — including the case where the expected total is above zero and Gusto shows no bonuses at all — DM Joshua plainly: what was owed, what was paid, and who is short or missing. This is the whole point of the task; never let a mismatch pass silently.
5. Record the result in the ledger workbook's Trend tab row for that month (append a "Paid" note) and append a dated line to `Bonus Program/RUN_LOG.md`.
