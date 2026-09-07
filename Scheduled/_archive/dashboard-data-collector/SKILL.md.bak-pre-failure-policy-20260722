---
name: dashboard-data-collector
description: Additive-only data feed for the standalone Valley Pawn management dashboard (outside Claude/Cowork). Runs hourly. Reads the ops Slack channels and the /Users/joshuadavis/Documents/Claude/Scheduled/ report files for evidence of what ran and what it found, and writes normalized rows into the "Valley Pawn — Dashboard Data" Google Sheet (TaskRuns / KPIs / Alerts tabs) via a single authenticated HTTP POST — NOT by clicking through the Sheets UI. Does NOT touch, call, or modify any existing scheduled task — it only reads their output (Slack posts + report files already being produced). Rebuilt 2026-07-15 after the original UI-automation version silently died after one run; rebuilt again 2026-07-16 to move the ingest secret out of this file and into macOS Keychain.
model: claude-sonnet-5
---

# Dashboard Data Collector

You are populating the data backbone for a standalone web dashboard Joshua asked for — "outside of Claude," showing every scheduled task's status plus business reporting (loans, layaways, inventory, sales, KPIs) in one place.

**Live dashboard (human-facing, domain-restricted):**
https://script.google.com/macros/s/AKfycbwIxN4zSsw6eGrItAwT8ICsDzomn7jVS0OcqKBmgWDEiMAIH65FsHOYNV3eIYbNo8_h/exec

**Ingest endpoint (this task writes here — machine-to-sheet, secret-gated, NOT for browsing):**
https://script.google.com/macros/s/AKfycby5QyYAqHFYEr8MsSeoSokqD0Kp6L0OvuYXLq9ld8l-1dkH5UbqbDz8841FFT5ranFY/exec

**Ingest secret:** stored in the local macOS Keychain, NOT in this file. Retrieve it at runtime with:
```bash
SECRET=$(security find-generic-password -a 'dashboard-collector' -s 'valley-pawn-ingest-secret' -w)
```
Never print this value in chat, Slack, reports, or any other file — only use it inline in the POST command below. If the Keychain lookup fails, stop and write an Alerts row (severity: warning) reporting that the credential could not be retrieved — do not fall back to any other secret source.

**Target sheet (for reference only — do NOT open the Sheets UI to write to it, use the POST endpoint above):**
"Valley Pawn — Dashboard Data", ID 1AVg9av3L7wJyQgX49uMYg5hBjbDz5Jwllxen3xkEkqk
Tabs: TaskRuns (task_name, domain, source, status, last_run_iso, detail, next_expected_iso),
KPIs (store, metric, value, as_of_date, period, source_report),
Alerts (severity, message, created_iso, resolved)

**Hard rule — additive only, per BUSINESS_OS.md Rule #4:** this task NEVER modifies, triggers, or interferes with any existing scheduled task, SKILL.md, Bravo saved report, or pipeline handler. It is a read-only observer of two things:
1. Slack channels the existing tasks already post to (see BUSINESS_OS.md Section 2 for the channel list — #daily-funds-reconcilation, #loan-review, #layaway-review, #store-performance, #aged-inventory-review, #employee-performance, #new-inventory, #email-campiagns, #general, per-store funds channels, etc.)
2. Report files already written to /Users/joshuadavis/Documents/Claude/Scheduled/<task-folder>/ (their modified-time and filename tell you when a task last actually produced output)

**What to do each run:**
1. Read BUSINESS_OS.md Section 2 (Domain Map) fresh each run — it is the canonical list of what SHOULD be running, its cadence, and which Slack channel/report file to check. Do not hardcode a stale copy of that list in this file; re-read it live so a change to BUSINESS_OS.md is picked up automatically.
2. For each "A" (Active) or "T" (Triggered) task in that map: check the most recent matching Slack message (search or read the channel) and/or the most recent file in its Scheduled/<task-folder>/ directory. Determine: did it run, when, success or failure, and any one-line detail worth surfacing (e.g. "2 stores above 5% threshold").
3. Build a JSON array of row objects for the TaskRuns tab — one object per task, keys matching the header row exactly (task_name, domain, source, status, last_run_iso, detail, next_expected_iso).
4. Write it with a single shell command (use the two-step pattern below — do NOT just `curl -L`, Google's redirect target rejects a followed POST and some curl versions mishandle the auto-downgrade-to-GET; the two-step pattern below is verified working):

```bash
INGEST_URL="https://script.google.com/macros/s/AKfycby5QyYAqHFYEr8MsSeoSokqD0Kp6L0OvuYXLq9ld8l-1dkH5UbqbDz8841FFT5ranFY/exec"
SECRET=$(security find-generic-password -a 'dashboard-collector' -s 'valley-pawn-ingest-secret' -w)

post_rows() {
  # $1 = tab name, $2 = keyField or empty, $3 = json rows array
  local tab="$1" keyfield="$2" rows="$3"
  local body
  if [ -n "$keyfield" ]; then
    body=$(printf '{"secret":"%s","tab":"%s","keyField":"%s","rows":%s}' "$SECRET" "$tab" "$keyfield" "$rows")
  else
    body=$(printf '{"secret":"%s","tab":"%s","rows":%s}' "$SECRET" "$tab" "$rows")
  fi
  LOC=$(curl -sS -D - -o /dev/null -X POST "$INGEST_URL" -H "Content-Type: application/json" -d "$body" | grep -i '^location:' | awk '{print $2}' | tr -d '\r')
  if [ -n "$LOC" ]; then curl -sS "$LOC"; else echo '{"ok":false,"error":"no redirect location returned"}'; fi
}

post_rows "TaskRuns" "task_name" '[{"task_name":"...", "domain":"...", "source":"...", "status":"...", "last_run_iso":"...", "detail":"...", "next_expected_iso":"..."}]'
```

   Always pass `keyField: "task_name"` for TaskRuns so re-running overwrites the existing row for that task rather than accumulating duplicates.

5. When a report contains numeric KPIs (loan balance, layaway balance, aged inventory $, employee sales, etc.), also POST rows to the KPIs tab the same way — omit `keyField` there (KPIs tab accumulates history, one row per observation).
6. If a task that should have run on its cadence shows no matching Slack post or file newer than ~1.5x its expected interval, POST a row to the Alerts tab (severity: warning), omitting `keyField` — this is the main value of the dashboard, catching a silently-broken automation before Joshua notices the hard way.
7. Never DM Joshua, never post to Slack, never send an alert message yourself — this task's only output is the three sheet tabs via the POST endpoint. The dashboard (a separate Apps Script web app reading this sheet) is what Joshua looks at, not a notification stream. This keeps it from adding noise on top of the 174 existing tasks' own Slack posts.
8. Check the response JSON from each `post_rows` call (`{"ok":true,"written":N}` or `{"ok":false,"error":"..."}`). If any call returns `ok:false` or an unexpected empty response, POST a single Alerts row (severity: warning) noting which tab failed and the error, so a broken ingest doesn't fail silently the way the old UI-automation version did.

**Known gap already flagged in the Alerts tab (do not re-add unless it's been cleared):** BUSINESS_OS.md's own trigger inventory is a May 2026 snapshot claiming 58 scheduled tasks; the live folder count under /Users/joshuadavis/Documents/Claude/Scheduled/ is 174, and Claude Code Remote's own trigger list (a separate system) shows only 11 items with no overlap in names. This reconciliation gap stays visible in the Alerts tab until someone (a future session or Joshua) resolves which of the 174 folders are actually live vs. stale/abandoned.
