---
name: monthly-analytics-watchdog
description: 1st of month at 7 AM — check whether monthly-analytics-report posted to #company-performance. If not, DM Joshua with diagnostics (which CSVs landed, which didn't, last working file). This is the ONE notification path for monthly analytics failures.
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.



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
---
name: monthly-analytics-watchdog
description: Verify that `monthly-analytics-report` posted to #company-performance overnight. If not, DM Joshua with a concise diagnostic. This is the ONE notification path for monthly analytics failures.
---

You are the watchdog for the monthly analytics pipeline. The main `monthly-analytics-report` task should have posted to #company-performance (`C0B26GD8D2R`) between 3 AM and now (7 AM). If it didn't, Joshua needs to know.

# Step 0 — Connector readiness gate

Confirm `mcp__f92ce7c6-0353-4419-8491-f0843b182ff2__slack_read_channel`, `mcp__f92ce7c6-0353-4419-8491-f0843b182ff2__slack_send_message`, and `mcp__Control_your_Mac__osascript` are loaded. Warming up = wait 30 s × up to 12 min before giving up. Warmup is NOT failure.

# Step 1 — Compute the report month

Report month = today minus 1 month. E.g. if today is July 1, 2026, report month = "June 2026". Format both the month name (`June`) and `YYYY-MM` (`2026-06`) for later use.

# Step 2 — Scan #company-performance for today's post

Read the most recent ~10 messages from `C0B26GD8D2R` (use `oldest=<today midnight unix>` to scope to today only).

Look for a message that:
- Contains the string `Monthly Analytics — {Month Name} {Year}` matching the report month
- Was posted today (current calendar day in ET)

If found → exit silently. No DM needed. The main task did its job.

# Step 3 — If the post is MISSING, gather diagnostics

Use osascript to inspect:

1. **Pre-stage status:** `cat /Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/monthly-analytics/{YYYY-MM} Prestage.md` if it exists. Capture the Status line and any error notes.

2. **Sidecar inventory:** `ls -la "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/{YYYY-MM}/"` and count how many of the 30 expected CSVs (6 windows × 5 stores) are present and ≥ 2 KB.

3. **Main task working file:** `cat /Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/monthly-analytics/{YYYY-MM} Monthly Analytics.md` if it exists. Capture the Status line and any error notes.

4. **Recent pipeline triggers state:** `ls -la "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/claimed/" | grep monthly-analytics` — anything stuck claimed means the watcher hung mid-run.

# Step 4 — DM Joshua (this is the ONE DM path for monthly analytics)

DM user `U03BB52MDSA` (Joshua) with this format:

```
⚠️ *Monthly Analytics — {Month Year}: NO POST FOUND IN #company-performance BY 7 AM*

*Pre-stage status:* {COMPLETE / PARTIAL X/30 / FAILED / FILE MISSING}
*Sidecar CSVs:* {N}/30 present (≥ 2 KB)
*Main task working file:* {found / missing}
*Stuck triggers in claimed/:* {N if any, list IDs}

*Likely cause:* {best guess from the above — pipeline offline, watcher hang, partial CSVs, or main task ran but post failed}

*To recover:* run /Users/joshuadavis/Documents/Claude/Scheduled/monthly-analytics-report manually once the underlying issue is fixed. If the sidecar already has 30/30 CSVs, the main task can complete in ~1 minute.
```

If the underlying problem is clearly the pipeline being offline (e.g. all 30 sidecar CSVs missing, plus pre-stage file says FAILED or doesn't exist), add a second sentence to "Likely cause" pointing at `daily-funds-verification` recent posts as the canonical check for pipeline health.

# Step 5 — Always save a working file

Save `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/monthly-analytics/{YYYY-MM} Watchdog.md` with the diagnostics gathered (or note "post found, watchdog exited clean" if Step 2 found it).

# Hard rules

- One DM, only when the post is missing. Never DM on success.
- Read-only Slack reads + one outbound DM. No edits to anything in Bravo or the pipeline.
- All `Bravo Data Extraction/` access goes through `osascript do shell script`.
- Additive — does not touch any other task or production infra.

<!-- migrated to working model 2026-06-15 -->