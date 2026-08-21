---
name: weekly-timekeeping-analysis-mcp
description: Monday 2 AM (overnight) — pull last week's Gusto time data headlessly via the Gusto MCP (list_time_records + list_employees), post a CONCISE store-by-store summary to #timekeeping-summary at 9 AM Monday. Additive replacement candidate for weekly-timekeeping-analysis (Chrome-based) — built and proven 2026-07-08, not yet scheduled live. Chrome fallback preserved as PATH B for parity with daily-clockin-checks proven pattern.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do.

## Why this file exists
`weekly-timekeeping-analysis` (the live production task) still drives Gusto Time Tracking via Chrome because its SKILL.md was written before 2026-06-10, when `daily-clockin-check` proved the Gusto MCP's `list_time_records` returns full native shift data headlessly (that task's own doc previously said the same "MCP returns empty" thing, for the wrong tool — `list_time_sheets` — not the one that actually works, `list_time_records`).

Proven live 2026-07-08: `list_time_records(start_date=2026-06-29, end_date=2026-07-05)` returned `source: "native"` with a full week of shifts (breaks, clock-in/out timestamps, durations) for every employee, identity-tagged with `firstName`/`lastName`/`employeeUuid`. `list_employees` additionally returns each employee's `department` field, which is already their store name (e.g. "Lexington", "Harrisonburg", "Waynesboro", "Culpeper", "Roanoke", "Corporate Support") — no per-employee `list_employee_work_addresses` lookup is needed at all, which is simpler than the crosswalk-table approach `daily-clockin-check` uses for the daily check.

**This task is additive — it does NOT modify or schedule over `weekly-timekeeping-analysis`.** It is a parallel, unscheduled, proven candidate. Cut over (disable the Chrome-based task, enable this one on the same Monday 2 AM cadence) only when Joshua says go.

---

## PATH A — Headless via Gusto MCP (PRIMARY)

1. Determine the prior work week: Gusto's pay period runs Monday–Sunday. Use the most recent completed Mon–Sun period (the week that ended yesterday). `start_date` = that Monday, `end_date` = that Sunday.
2. Call `list_time_records(start_date, end_date)`. Confirm `source == "native"`; if not, or `shifts` is empty/missing, fall through to PATH B.
3. Call `list_employees(terminated=false)` once. Build a `employeeUuid -> department` map directly from the response — no work-address lookup required.
4. Exclude: Hillary Davis, Joshua Davis, Sandi Cole, Preston Peters (same exclusion list as `daily-clockin-check`) — these are corporate/salaried, not per-store hourly staff.
5. Group shifts by `department` (store), then by employee. Per employee, per day:
   - Regular minutes = `durationInMinutes` minus break minutes (breaks are already excluded from `durationInMinutes` per the API's shift model — verify against a known day's total before trusting this if the parser disagrees).
   - Flag: a break with a null/missing `endTime` on a day that's fully in the past is an unclosed break — note it as a data quality flag, not a live status (this is a weekly retrospective, not `daily-clockin-check`'s live status check).
   - Flag: any single shift's total on-clock span exceeding ~9 hours as a possible missed clock-out.
6. Sum to weekly totals per employee: total hours, OT (hours beyond 40/week), and any flags (missed clock-outs, notably short/long shifts).
7. Aggregate to per-store totals: total hours, employee count, OT count, coverage gaps (only 1 distinct employee clocked in all week).

## PATH B — Gusto website via Chrome (FALLBACK ONLY)
Identical to the fallback already documented in `weekly-timekeeping-analysis`'s live SKILL.md — reuse that flow verbatim if PATH A's `source` isn't `native` or shifts are empty. Do not duplicate that logic here; read it from the live task file at run time if this candidate is ever promoted.

## Build & Send (same output contract as the live task — do not change the Slack shape)
Post the identical structure `weekly-timekeeping-analysis` already produces:
- Header line with date range + total approved timesheets/hours across all stores.
- One block per store (sorted by total hours desc): bold store name + total hours + employee count, then one bullet per employee with hours, OT in parens, and any flags.
- A trailing "*Heads-up:*" block: total flags, OT count, coverage gaps, new hires (first week seen in the data), anything else worth a manager's eye.

Post via `slack_schedule_message` to `#timekeeping-summary` (`C0AN6TNA4ES`) at 9:00 AM Monday local time — same destination and cadence as the live task. Do not post elsewhere; do not DM Joshua.

## Verification before any cutover is proposed
Run this task's PATH A for 1-2 real Mondays in parallel with the live Chrome-based task (both write to a scratch file instead of posting, or one is renamed temporarily) and diff the two outputs employee-by-employee and store-by-store. Only propose cutover once the totals match — the same bar `monthly-analytics-report`'s `parse_eom.py` was held to against `monday-store-rankings` (matched to the penny) before it was trusted.

## Status
Built and API-proven 2026-07-08 (One Data Source consolidation audit, finding #4). Not scheduled. Not live. No existing task modified.
