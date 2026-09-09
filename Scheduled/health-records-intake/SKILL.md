---
name: health-records-intake
description: Nightly 9 PM — file anything dropped in Health Optimization/_inbox, parse lab values into the master CSV, and scan email for new result notices.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Run Joshua's nightly health records intake. Domain 3 (Personal / Health). Silent on an empty night.

> ⚠️ FAILURE ALERT POLICY (platform standard, v2): if this run cannot complete its core work, send Joshua ONE plain-language Slack DM (channel D03BHQH5VGT): ⚠️ Scheduled task "health-records-intake" did not complete — <date>. Nothing technical in the DM. Technical detail goes in the run output and Health Optimization/STATUS.md.

RUN ON THE HOST via `mcp__Control_your_Mac__osascript` + `do shell script`. Never the workspace Bash tool, never a `/sessions/*/mnt/` path.

STEP 1 — file the inbox:
do shell script "cd '/Users/joshuadavis/Documents/Claude/Projects/Health Optimization' && python3 scripts/inbox_ingest.py 2>&1 | tail -20"

It extracts text, detects the source and collection date, appends parsed results to All_Lab_Results_MASTER.csv (duplicates skipped), moves the file into records/<year>/ with a .md companion, and logs to _inbox/INTAKE_LOG.md. Files with no readable text land in _inbox/needs_ocr/.

STEP 2 — look for results that arrived by email today. Use the unified-search index (fast, local):
do shell script "export PATH=/opt/homebrew/bin:$PATH; vpfind --mail --since $(date -v-2d +%Y-%m-%d) -n 30 'Labcorp OR Quest OR MyChart OR \"Function Health\" OR Genova OR Vibrant OR \"test result\" OR \"new result\" OR \"records request\" OR \"UF Health\"' 2>&1 | head -60"
Ignore marketing blasts (FHCP newsletters, \"Take Charge of Your Health\", watch-listing alerts, restaurant receipts). You are looking for an actual result notice, a records-request reply, or a visit summary. If you find one with an attachment or a portal link, note it in Health Optimization/STATUS.md under Open threads with the date and what it appears to be — do NOT download from a portal or click links.

STEP 3 — if anything was filed or found, append a dated line to Health Optimization/CHANGELOG.md and update the relevant row in Open_Tests_Tracker.md (status, notes). Use `do shell script` with a python heredoc to edit files; never overwrite a whole file you have not read.

STEP 4 — report. If nothing was filed and no result emails were found, your ENTIRE final message is exactly: "Nothing new." If something was filed, send Joshua ONE short plain-language Slack DM (D03BHQH5VGT) — e.g. "Your Quest labs from the 28th are filed. Two values flagged: platelets 137 (low), glucose 104 (high)." — then a one-line final message.

Never interpret results clinically beyond repeating the lab's own flags. No jargon, no file paths in the DM.