---
name: fpd-history-backfill
description: One-time bootstrap of the 12-month FPD history archive. Runs the saved Bravo report 'Claude FPD 12-month Lookback' across all 5 stores via the Bravo Data Extraction pipeline, merges every row into /Users/joshuadavis/Documents/Claude/Scheduled/_fpd-archive/fpd-history.csv deduped by Ticket Number, and DMs Joshua a summary. Use this once after creating the saved report in Bravo to seed the chronic-risk view in weekly-fpd-ranking. Safe to run again later as a quarterly/monthly refresh.
---

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard, added 2026-08-02).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed with the task.
> 3. If it errors (no such tool available, not connected, tool-not-found): wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **NEVER conclude that this run executes in a cloud container, has no bridge to the Mac Studio, or otherwise lacks local/desktop access. That conclusion is false** and is the single most common cause of a false failure on this platform. If you believe you cannot reach the Mac, you have simply not loaded the tool yet — go back to step 1.
>
> **Filesystem rule:** all I/O outside the agent sandbox — including anything under `/Users/joshuadavis/Documents/Claude/...` — goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s inside one call; poll in short increments across separate calls. Guard any command that may exit nonzero with a trailing || true.


> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


You are running Joshua Davis's one-time (or periodic refresh) backfill of the FPD history archive. This skill seeds `_fpd-archive/fpd-history.csv` with every loan that has defaulted in the last 365 days, so the weekly-fpd-ranking skill's chronic-risk sections show meaningful data starting from week 1 instead of after a year of weekly accumulation.

**Prerequisite — saved Bravo report must exist.** Before running this skill, Joshua must create a saved Bravo report named exactly **"Claude FPD 12-month Lookback"** in any one store (saved reports are company-wide). Criteria:
- Loan Date in last 365 days (today minus 365 → today)
- Last Payment Date IS NULL
- Columns: Ticket Number, Category, Full Description, Loan Amount (same as "Claude First Payment Default")

If the report does not exist, every store cell will fail with a `SelectSavedReport` error. DM Joshua and stop.

═══════════════════════════════════════════════
STEP 1 — Drop the Bravo trigger
═══════════════════════════════════════════════

Generate a trigger ID and JSON, write via osascript:

```applescript
set triggerId to "fpd-history-backfill-2026-05-18T17-40-00"
set triggerJson to "{\"id\": \"" & triggerId & "\", \"requested_at\": \"2026-05-18T17:40:00-04:00\", \"reports\": [{\"name\": \"fpd-lookback-12mo\", \"stores\": [\"CUL\",\"HAR\",\"LEX\",\"ROA\",\"WAY\"], \"date\": \"2026-05-18\"}]}"
set triggerPath to "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/" & triggerId & ".json"
do shell script "echo " & quoted form of triggerJson & " > " & quoted form of triggerPath
return "dropped " & triggerPath
```

═══════════════════════════════════════════════
STEP 2 — Poll for completion (LONG)
═══════════════════════════════════════════════

A 12-month lookback grid can have hundreds of rows per store. The grid walker pages through them all. Budget **5–15 minutes per store**, **30–75 minutes for all 5**. Timeout at **90 minutes** (180 polls × 30s).

```applescript
do shell script "test -f '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/" & triggerId & ".result.json' && echo READY || echo PENDING"
```

If timeout fires, DM Joshua at `U03BB52MDSA` with the trigger ID and stop.

═══════════════════════════════════════════════
STEP 3 — Read each CSV and merge into the archive
═══════════════════════════════════════════════

For each successful cell, read its CSV via osascript. CSV shape:

```
Ticket Number,Category,Full Description,Loan Amount
BT-VAP015231,Gold-Stone Ring,4.2DWT 14K-Y/G ROUND CUT,$140.00
...
```

**Archive path:** `/Users/joshuadavis/Documents/Claude/Scheduled/_fpd-archive/fpd-history.csv`

**Archive columns:**
```
first_seen_date,store,ticket_number,category,full_description,loan_amount
```

**Merge logic:**
1. Create the `_fpd-archive` folder if it doesn't exist.
2. If `fpd-history.csv` doesn't exist, create it with the header row above.
3. Load existing ticket numbers from the archive into a set.
4. For each new row from this run, if `ticket_number` is not already in the archive set, append:
   - `first_seen_date` = today (YYYY-MM-DD)
   - `store` from the CSV filename
   - other fields from the row
5. Sum the new-row count and totals per store as you go.

Use real CSV parsing (Python `csv` module via osascript, or any library that handles quoted fields with embedded commas).

═══════════════════════════════════════════════
STEP 4 — Summarize and DM Joshua
═══════════════════════════════════════════════

Compute and DM Joshua (`U03BB52MDSA`) on Slack:

```
*FPD history backfill complete — [today]*

Loans added to archive:
• CUL — [N] loans • $[exposure]
• HAR — [N] loans • $[exposure]
• LEX — [N] loans • $[exposure]
• ROA — [N] loans • $[exposure]
• WAY — [N] loans • $[exposure]
*Total:* [ΣN] loans • $[Σexposure] now in fpd-history.csv

Top 3 chronic categories (12-month):
1. [CATEGORY] — [N] loans • $[exposure]
2. [CATEGORY] — [N] loans • $[exposure]
3. [CATEGORY] — [N] loans • $[exposure]

Top 10 chronic items (12-month, by Category + first-3-words-of-description):
1. [CATEGORY] / [CANONICAL DESCRIPTION] — [N] occurrences • $[exposure]
... (10 total)

Archive: /Users/joshuadavis/Documents/Claude/Scheduled/_fpd-archive/fpd-history.csv
```

Do NOT post to `#first-payment-default` — this is a backfill/maintenance action, not a weekly ops update. The ops channel stays clean.

═══════════════════════════════════════════════
If something goes wrong
═══════════════════════════════════════════════

- **Saved report not found** (cells fail with `SelectSavedReport` or `Claude FPD 12-month Lookback`): the saved Bravo report doesn't exist yet. DM Joshua and stop — he needs to create it in Bravo first.
- **Watcher not running** (no result JSON after 90 min): DM Joshua with the trigger ID and stop.
- **Some stores succeeded, others failed**: merge what you have, DM Joshua a partial summary noting which stores need a retry. Re-running the skill is safe — the archive dedupes by Ticket Number.
- **Archive file exists but header doesn't match expected**: stop and DM Joshua. Don't append potentially-misaligned rows.

═══════════════════════════════════════════════
Cadence
═══════════════════════════════════════════════

Run this once after the saved report is created in Bravo. Optionally re-run monthly or quarterly to capture loans that defaulted in the prior month that the weekly cohort (60–90 day rolling window) might have under-captured. The dedupe-by-ticket logic makes re-running a no-op if no new data is found.
