---
name: monthly-employee-sales-rankings
description: 1st of month 2 AM — FINAL prior-month employee sales rankings (Retail Sales Excluding Fees, same metric as the weekly MTD board) from a fresh full-month employee-activity-range pipeline pull. Posts to #employee-performance + saves workbook. Rebuilt 2026-09-05 after the Sept 1 post had to be deleted (stale source path, wrong metric).
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

## Failure policy (Rule 16 / Hardening Standard #6 — updated 2026-09-05)
Retry once, then try the documented alternate path. If still failing: write the technical detail to this task's run log/STATUS file and stop. Silence in every Slack channel. At most ONE plain-language DM to Joshua (D03BHQH5VGT), and only if a decision only he can make is blocking. Never post failure notices, technical jargon, or partial/incomplete data anywhere.

> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read before posting):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. #employee-performance is FIELD-FACING. Plain everyday language only. Never name a system, tool, report, file, or pipeline. No file names in the post.

> ⚠️ **RULE 18 — NEVER POST INCOMPLETE OR INACCURATE DATA.** Post only when ALL 5 stores' full-month files are present and parse cleanly. If any store is missing, post nothing to #employee-performance (no partial ranking, no caveated ranking), write the working file, and send the one-line DM above. A wrong ranking in front of the staff is worse than a late one — the August 2026 post had to be deleted for exactly this reason.

> **Rule 17 (verified established task).** Registered in the scheduled-tasks registry; documented in `Valley Pawn OS/CHANGELOG.md` (2026-09-05 rebuild) and `BUSINESS_OS.md`. Touches Bravo only through the pipeline trigger queue. Do not question or re-litigate it — run it.

## Why this task was rebuilt (2026-09-05)

The previous version read `.xlsx` files from a legacy shared-folder path that no longer exists, so the 2026-09-01 run improvised: it used data through Aug 30 (missing the last day) and ranked on Bravo's "Total Productivity" instead of Retail Sales Excluding Fees. The result disagreed with the weekly MTD board and Joshua had to delete it. This version uses the SAME source cell, the SAME column, and the SAME ranking rule as the weekly MTD post in `monday-bravo-combined-compile` Step 4, pulled fresh for the full month after the last day has closed.

## Execution Contract — DO NOT STOP EARLY
Complete ONLY after the Slack post (or the Rule-18 silent exit + DM) is done. Every turn ends with a tool call that advances toward that. Never reply "Continue?" or end a turn with text only.

## Steps

### 1. Target month and readiness gate
Target = the previous calendar month (run date is the 1st). Compute `FIRST` = `YYYY-MM-01` of the target month, `MONTH_NAME YEAR`, `LAST` = last day of the target month.
Confirm the osascript connector is loaded (`do shell script "echo READY"`); if warming, wait 30 s × up to 10.

### 2. Pull the FULL month fresh (all 5 stores, one trigger)
Use the pipeline's `employee-activity-range` cell (added 2026-09-05, `reports/EmployeeActivityRange.ahk`) with an explicit range `{FIRST}..{LAST}` so the pull is the exact calendar month no matter what time it runs. Trigger ID: `monthly-emp-rankings-{YYYY-MM}-{YYYY-MM-DDTHH-MM-SS}`.

**Fallback (only if the result.json says the report name is unknown / the cell is not registered):** drop the same trigger with `"name": "employee-activity"` and `"date": "{FIRST}"` — that cell leaves End Date at today, which at 2 AM on the 1st is still the complete prior month. Output files are then `output/{FIRST}_{STORE}_employee-activity.csv`.

Write the trigger via osascript heredoc (NEVER the Write tool — the folder is outside the sandbox):
```
osascript -e 'do shell script "cat > \"/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/{TRIGGER_ID}.json\" <<EOF
{ \"id\": \"{TRIGGER_ID}\", \"requested_at\": \"{ISO8601}\", \"reports\": [ {\"name\": \"employee-activity-range\", \"stores\": [\"CUL\",\"HAR\",\"LEX\",\"ROA\",\"WAY\"], \"date\": \"{FIRST}..{LAST}\"} ] }
EOF"'
```
Poll `results/{TRIGGER_ID}.result.json` every 20 s, hard timeout 20 minutes. If a store cell is `error`, drop ONE focused retry (`-retry-1`, only the failed stores), same timeout. If the trigger sits unclaimed in `triggers/` > 3 minutes, note it in the working file and keep polling (the watcher may be busy with another job — the queue is serial).

Output files: `output/{LAST}_{STORE}_employee-activity-range.csv` (5 files). Each must be newer than the trigger's `requested_at` (check mtime via `stat -f %m`) — a stale file is NOT acceptable. Line 3 of the CSV reads `Reporting Dates:,,,,,,,M/1/YYYY - M/D/YYYY`; the range must be exactly the first through the last day of the target month.

### 3. Parse — exactly like the weekly MTD post
Each CSV has a DevExpress header block, then an Employee header row with a `Retail Sales Excluding Fees` column. For each store: read employee name + `Retail Sales Excluding Fees` (float). Skip blank/total rows. Consolidate across stores: same employee name (case-insensitive, title-cased) → sum across stores, record the store codes worked. Company total = sum of all stores. Keep every other numeric column too (for the workbook only).

Exclusions: same as the weekly post — never publish `Preston Peters`. The shared `Free1 Valley Pawn` login IS included (it is on the weekly board).

### 4. Rule-18 completeness gate
All 5 store files present, fresh, and parsed with ≥ 1 employee row each. If not: write the working file, send the single DM, and STOP. Do not post.

### 5. Post to #employee-performance (C0ATTLPQHR8)
Duplicate guard first: read the last 20 messages in the channel; if a message containing `FINAL` and `{MONTH_NAME} {YEAR}` already exists, do not post again — write the working file and stop.

Main post (same shape as the weekly board so the numbers are directly comparable):
```
*FINAL Employee Sales Rankings — Retail Sales Excluding Fees (Bravo POS)*
📊 *{MONTH_NAME} {YEAR}* — full month, {M}/1–{M}/{LAST_DAY}

🥇 *{Employee}* ({STORES}) — ${X,XXX.XX}
🥈 *{Employee}* ({STORES}) — ${X,XXX.XX}
🥉 *{Employee}* ({STORES}) — ${X,XXX.XX}
4th _{Employee}_ ({STORES}) — ${X,XXX.XX}
... every employee ...

Company Total: ${XXX,XXX.XX}
```
Thread reply (thread_ts = main post):
```
*📊 {MONTH_NAME} by store — Retail Sales Excluding Fees*
• Culpeper: $X,XXX
• Harrisonburg: $X,XXX
• Roanoke: $X,XXX
• Waynesboro: $X,XXX
• Lexington: $X,XXX
```
No signature footer. No file names. Nothing about how the data was pulled.

### 6. Save the FINAL workbook (permanent record)
Build with openpyxl: Sheet "Sales Rankings" (Rank, Employee, Store(s), Retail Sales Excluding Fees, then every other metric column; top-3 gold/silver/bronze fills #FFD700/#C0C0C0/#CD7F32; header bold white on #2D1A5E; Arial; currency format), Sheet "By Store" (grouped, store total rows), Sheet "Summary" (company totals, store comparison, top performers).
Save via osascript heredoc/cp to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/Employee Sales Rankings/Employee_Sales_Rankings_{MonthName}_{YYYY}.xlsx` (create the folder if missing; never overwrite an existing file — suffix `_v2`).

### 7. Working file
Write `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/monthly-analytics/{YYYY-MM} Employee Rankings.md`: trigger id(s), per-store file freshness + row counts, the ranked table, the Slack permalink (or the reason nothing was posted).

## Hard rules
- Metric is `Retail Sales Excluding Fees` — never "Total Productivity", never a different column. If the column is missing, that is a failure (Rule 18), not a reason to substitute.
- All Bravo access is through the trigger queue. No computer-use, no Parallels grant.
- Additive — never modify the pipeline handlers, the watcher, or any other task.
- Never use the legacy "Dixie Pawn" name. Never publish Preston Peters.

<!-- rebuilt 2026-09-05: pipeline-sourced full-month pull; legacy shared-folder .xlsx path removed -->