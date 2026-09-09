---
name: oura-daily-import
description: Verify the 8:30 AM launchd Oura import ran and the local database is healthy, mirror its artifacts into the project folder, and run the import as fallback if launchd did not.
model: claude-haiku-4-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22; v3 2026-09-08):** If this run fails, errors out, or cannot complete its core work, do NOT message Joshua, Preston, or anyone else, in any medium. Instead append ONE row to the fleet failure ledger `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` (use `mcp__Control_your_Mac__osascript` `do shell script "printf ... >> file"` if file tools cannot reach it) in exactly this form: `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or: yes, <the single thing only Joshua can do>> | OPEN |`. The `fleet-guardian` task reads this ledger twice a day, re-runs whatever is safe to re-run, rolls anything that truly needs Joshua into `Life OS/HUMAN_QUEUE.md`, and sends Joshua at most ONE consolidated plain-language DM per day. Individual tasks never DM about failures. All technical detail goes in the run output/log/STATUS file for the next Claude session to pick up. Never send failure notices to any team channel, store manager, employee, or Preston. FIELD COMMUNICATION RULE (unchanged): anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This v3 supersedes both the v2 one-line-DM rule and any older rule in this file.


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

## What this task is now (v5.1, 2026-09-06) — VERIFIER + MIRROR, not the primary importer

The Oura import runs as a native launchd agent, `com.healthos.oura-import`, at 8:30 AM with no
Claude involved. Two things matter and are easy to get wrong:

1. **The live database is on LOCAL disk** at `~/Library/Application Support/HealthOS/oura.db`.
   It is never in the project folder — that synced path silently truncated it on 2026-08-14 and
   2026-08-31, destroying years of history both times.
2. **launchd cannot touch `~/Documents` at all** (macOS TCC denies it — "Operation not permitted",
   exit 126). So the agent writes every artifact under HealthOS and CANNOT copy them into the
   project folder. **Mirroring them is this task's job**, because a Cowork session does have that
   access.

Your job: confirm this morning's run happened and was healthy, mirror the artifacts into the
project folder, and report one line.

**RUN ON THE HOST ONLY.** Use `mcp__Control_your_Mac__osascript` with `do shell script` for every
command. Never the workspace Bash tool, never a `/sessions/*/mnt/` path — that mount deadlocks on
this folder.

### Step 1 — read the summary the agent wrote
```
do shell script "cat \"$HOME/Library/Application Support/HealthOS/oura_latest.json\""
```
Healthy = `status` is `ok`, `run_at` is TODAY, `readiness_latest_day` is yesterday or today,
`heartrate_first_day` is 2022-10-02, `heartrate_rows` above 900,000.

### Step 2 — if it is missing, stale (run_at not today), or status is not ok, run it yourself
```
do shell script "/bin/bash \"$HOME/Library/Application Support/HealthOS/bin/run_daily_v5.sh\" 2>&1 | tail -15"
```
A healthy run takes about 20 seconds. The script self-heals: if the live db is missing or has
shrunk below 90% of the backup it auto-restores from `oura.db.gz` first — you'll see a
`WARN: ... auto-restoring seed` line, which is recovery working, NOT a failure. Then re-read the
summary. If launchd itself never fired, check why and note it:
```
do shell script "launchctl print gui/$(id -u)/com.healthos.oura-import | grep -E 'state =|last exit'; tail -5 \"$HOME/Library/Application Support/HealthOS/logs/oura-import.err.log\""
```

### Step 3 — mirror the artifacts into the project folder (the part only you can do)
```
do shell script "H=\"$HOME/Library/Application Support/HealthOS\"; O=\"$HOME/Documents/Claude/Projects/Health Optimization/oura\"; cp \"$H/oura_latest.json\" \"$O/\" && cp \"$H/STATUS_oura_pipeline.md\" \"$O/\" && cp \"$H/oura.db.gz\" \"$O/\" && cp \"$H/bin/oura_import.log\" \"$O/\" && echo mirrored"
```
This keeps the compressed backup inside Time Machine / the synced folder, which is the offsite
copy of the whole history. If it fails, say so plainly in the report — do not retry in a loop.

### Step 4 — refresh the nights ledger
```
do shell script "cd \"$HOME/Documents/Claude/Projects/Health Optimization\" && python3 scripts/night_signature.py 2>&1 | tail -2"
```

### Step 5 — failure conditions
- Status `fail` after you re-ran it, or a message mentioning 401/403 → the Oura Personal Access
  Token expired or the membership lapsed. Send ONE plain DM to D03BHQH5VGT: "Your Oura ring data
  stopped syncing — the Oura login token needs renewing at cloud.ouraring.com/personal-access-tokens
  (ask for the metabolic scope too), then drop the new token into the oura folder." Do not retry.
- Any other failure → the standard one-line failure DM per the policy at the top of this file.
- A `WARN ... auto-restoring seed` line on TWO consecutive days means something is corrupting the
  local db between runs — write the details into `oura/STATUS_oura_pipeline.md` for the next
  session. Not a DM.

### Step 6 — report
One line, e.g. `Oura verified — readiness through 2026-09-05, 924,232 HR rows, launchd ran 08:30,
artifacts mirrored.` If you had to run the fallback, say so. Keep it brief; no JSON, no logs, no
file paths in anything sent to Joshua.