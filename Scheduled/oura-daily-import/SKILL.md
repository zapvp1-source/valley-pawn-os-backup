---
name: oura-daily-import
description: Pull the latest Oura Ring data into the local SQLite database each morning.
model: claude-haiku-4-5
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


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
Run Joshua's daily Oura Ring data import. This pulls the last few days of Oura data into a local SQLite database so it stays current.

**RUN ON THE HOST, NOT IN THE SANDBOX (changed 2026-09-01 — read this first).**
Do NOT use the workspace Bash tool or the `/sessions/*/mnt/` FUSE mount for this task. On
2026-09-01 that mount deadlocked ("Resource deadlock avoided", exit 126) on every read and the
run failed. The same mount is the suspected cause of the silent database truncation on
2026-08-31. Use `mcp__Control_your_Mac__osascript` instead — it runs directly on the host with
no FUSE mount, no per-session folder approval, and no sync layer between SQLite and the file.

The oura folder is always at:
`/Users/joshuadavis/Documents/Claude/Projects/Health Optimization/oura`

Steps:

1. Run the import via osascript:

   `do shell script "cd '/Users/joshuadavis/Documents/Claude/Projects/Health Optimization/oura' && /bin/bash run_daily.sh 2>&1 | tail -30"`

   The script seeds a working copy in /tmp (SQLite can't run on the synced folder), runs
   `oura_import.py --days 3`, checkpoints, verifies integrity, and atomically writes oura.db
   back. It reads the Oura Personal Access Token from oura_token.txt next to the script. The
   import is idempotent — re-pulling the last few days never creates duplicates.

   To back-fill a wider window, prefix the command with `OURA_DAYS=10`.

2. Confirm success: the script prints "daily import complete" at the end.

   The script self-heals a truncated database. It computes a health floor at 90% of the
   uncompressed size of the oura.db.gz backup and auto-restores from that backup if oura.db
   falls below it. If you see a `WARN: ... auto-restoring seed` line, the restore fired and the
   run still succeeded — mention it in the report, but do NOT treat it as a failure. If that
   warning fires on consecutive days, something is corrupting the database between runs: write
   the details to a STATUS file in the oura folder for the next session.

3. Report back in ONE short line: the latest day in daily_readiness and the heartrate row
   count. Query a /tmp copy — never open the db on the synced folder directly:

   `do shell script "cp '/Users/joshuadavis/Documents/Claude/Projects/Health Optimization/oura/oura.db' /tmp/oura_check.db && python3 -c \"import sqlite3;c=sqlite3.connect('/tmp/oura_check.db');print('readiness latest:',c.execute('select max(day) from daily_readiness').fetchone()[0],'| heartrate rows:',c.execute('select count(*) from heartrate').fetchone()[0])\""`

   **Sanity-check the numbers before reporting success.** A healthy oura.db is ~220MB, with
   >900,000 heartrate rows and daily_readiness going back to 2022-10-03. If heartrate comes
   back in the low thousands, or readiness only covers recent days, the database is truncated —
   report that plainly instead of passing the number off as normal.

If the import fails with an auth error (HTTP 401/403), the Oura Personal Access Token has expired or membership lapsed — tell Joshua he needs to regenerate the token at cloud.ouraring.com/personal-access-tokens and replace oura_token.txt. Do not retry repeatedly.

Keep the final message to Joshua brief — just confirm it ran and the two numbers, unless something failed.
