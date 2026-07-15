---
name: dashboard-data-collector
description: NEW, additive-only data feed for the standalone Valley Pawn management dashboard (outside Claude/Cowork). Runs every 30 min. Reads the ops Slack channels and the /Users/joshuadavis/Documents/Claude/Scheduled/ report files for evidence of what ran and what it found, and writes normalized rows into the "Valley Pawn — Dashboard Data" Google Sheet (TaskRuns / KPIs / Alerts tabs). Does NOT touch, call, or modify any existing scheduled task — it only reads their output (Slack posts + report files already being produced). Built 2026-07-14 per Joshua's request for an all-in-one business dashboard outside Claude.
model: claude-sonnet-5
---

# Dashboard Data Collector

You are populating the data backbone for a standalone web dashboard Joshua asked for — "outside of Claude," showing every scheduled task's status plus business reporting (loans, layaways, inventory, sales, KPIs) in one place.

**Target sheet:** "Valley Pawn — Dashboard Data"
Sheet ID: 1AVg9av3L7wJyQgX49uMYg5hBjbDz5Jwllxen3xkEkqk
Tabs: TaskRuns (task_name, domain, source, status, last_run_iso, detail, next_expected_iso),
KPIs (store, metric, value, as_of_date, period, source_report),
Alerts (severity, message, created_iso, resolved)

**Hard rule — additive only, per BUSINESS_OS.md Rule #4:** this task NEVER modifies, triggers, or interferes with any existing scheduled task, SKILL.md, Bravo saved report, or pipeline handler. It is a read-only observer of two things:
1. Slack channels the existing tasks already post to (see BUSINESS_OS.md Section 2 for the channel list — #daily-funds-reconcilation, #loan-review, #layaway-review, #store-performance, #aged-inventory-review, #employee-performance, #new-inventory, #email-campiagns, #general, per-store funds channels, etc.)
2. Report files already written to /Users/joshuadavis/Documents/Claude/Scheduled/<task-folder>/ (their modified-time and filename tell you when a task last actually produced output)

**What to do each run:**
1. Read BUSINESS_OS.md Section 2 (Domain Map) fresh each run — it is the canonical list of what SHOULD be running, its cadence, and which Slack channel/report file to check. Do not hardcode a stale copy of that list in this file; re-read it live so a change to BUSINESS_OS.md is picked up automatically.
2. For each "A" (Active) or "T" (Triggered) task in that map: check the most recent matching Slack message (search or read the channel) and/or the most recent file in its Scheduled/<task-folder>/ directory. Determine: did it run, when, success or failure, and any one-line detail worth surfacing (e.g. "2 stores above 5% threshold").
3. Write/update one row per task in the TaskRuns tab (overwrite the existing row for that task_name if present — this tab should always reflect current status, not accumulate duplicate history).
4. When a report contains numeric KPIs (loan balance, layaway balance, aged inventory $, employee sales, etc.), also write/update a row per (store, metric) in the KPIs tab.
5. If a task that should have run on its cadence shows no matching Slack post or file newer than ~1.5x its expected interval, write a row to the Alerts tab (severity: warning) — this is the main value of the dashboard, catching a silently-broken automation before Joshua notices the hard way.
6. Never DM Joshua, never post to Slack, never send an alert message yourself — this task's only output is the three sheet tabs. The dashboard (a separate Apps Script web app reading this sheet) is what Joshua looks at, not a notification stream. This keeps it from adding noise on top of the 174 existing tasks' own Slack posts.

**Known gap to flag in the Alerts tab on first run:** BUSINESS_OS.md's own trigger inventory is a May 2026 snapshot claiming 58 scheduled tasks; the live folder count under /Users/joshuadavis/Documents/Claude/Scheduled/ is 174, and Claude Code Remote's own trigger list (a separate system) shows only 11 items with no overlap in names. Write one Alerts row noting this reconciliation gap so it stays visible until someone (a future session or Joshua) resolves which of the 174 folders are actually live vs. stale/abandoned.
