---
name: weekly-employee-sales-rankings
description: Monday 1:30 AM (overnight) — compile MTD employee sales rankings using "Retail Sales Excluding Fees" from Bravo's Employee Activity report. Pipeline-driven — no Parallels grant required. Schedule Slack post to #employee-performance for 9 AM Monday.
model: claude-sonnet-5
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


> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

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
You are running as an overnight background task at 1:30 AM Monday. Compile MTD employee sales rankings for all 5 Valley Pawn stores via the Bravo Data Extraction pipeline, then schedule a ranked Slack post to #employee-performance for 9:00 AM Monday.

**STANDING RULE — DATA ONLY in the Slack post.** The operations team reads `#employee-performance`. They do not need a source footer, multi-store-summed disclaimer, or pipeline commentary. Post the title, period line, ranked list, and stop. Strip the `_Source: Bravo POS · Employee Activity report. Multi-store employees summed across stores._` footer. If multi-store totals are unusual that week, mention it in the DM to Joshua, not the channel.

**RANKING FILTER (revised 2026-05-13 per Joshua).** Exclude these employees from the ops-channel ranking:
- **Preston Peters** — always excluded by name, regardless of which stores or what amount.
- **Any employee with $0.00 Retail Sales Excluding Fees** — drop them entirely. Zeros add noise without action value.

After filtering, re-number the ranking from 1 so the medals and "Nth" labels are dense (no gaps).

The data file (xlsx saved to `/Users/joshuadavis/Documents/Claude/Scheduled/`) should still include EVERYONE — Preston, the zeros, the full population — so the chain-internal record is complete. Only the Slack post is filtered. Note the filter at the top of Sheet 1 with a small italic line like `Filtered for #employee-performance: Preston Peters and $0.00 employees excluded.`

============================================================
CRITICAL — WHICH METRIC TO USE
============================================================
The metric for this ranking is **"Retail Sales Excluding Fees"** from Bravo's Employee Activity report.

DO NOT use "Total Productivity." Total Productivity includes fees and other non-retail activity and is the WRONG number.

If the CSV doesn't expose "Retail Sales Excluding Fees" as a column header, locate the closest equivalent (retail sales with fees subtracted out). NEVER fall back to Total Productivity.

============================================================
STEP 1 — Drop the Bravo trigger and wait
============================================================

Generate a trigger ID like `employee-activity-YYYY-MM-DDTHH-MM-SS`. Write to `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/<id>.json`:

```json
{
  "id": "employee-activity-2026-05-12T01-30-00",
  "requested_at": "2026-05-12T01:30:00-04:00",
  "reports": [
    {
      "name": "employee-activity",
      "stores": ["CUL", "HAR", "LEX", "ROA", "WAY"],
      "date": "2026-05-01"
    }
  ]
}
```

The `date` field is the **Start Date** for the report — first of the current month. End Date defaults to today.

Poll `results/<id>.result.json`. Full 5-store cycle takes ~3-5 minutes. Time out at 10 minutes.

============================================================
STEP 2 — Parse the CSVs
============================================================

For each successful cell, read its CSV from `output_path`. The Employee Activity CSV is a DevExpress export. The data table has rows per employee with columns like:
- Employee Name | Retail Sales Excluding Fees | (various other metrics)

Extract per-employee:
- Name
- Store (from filename: `_<STORE>_employee-activity.csv`)
- Retail Sales Excluding Fees (the column whose header exactly matches; if not present, use the retail-sales-minus-fees column)

Filter out:
- SYSTEM rows
- Header repetitions in the CSV
- Empty rows

============================================================
STEP 3 — Aggregate across stores
============================================================

- Sum across stores for multi-store employees (Preston Peters, Martin Dowden, Chadd McClintic, etc.)
- Rank highest-to-lowest by total Retail Sales Excluding Fees (MTD)
- Include zero and negative figures at the bottom; negatives reflect canceled layaways/returns exceeding sales

============================================================
STEP 4 — Slack post (canonical format from 2026-05-04)
============================================================

Channel: `#employee-performance` (`C0ATTLPQHR8`)

- Before 9:00 AM Monday → `slack_schedule_message` for 9:00 AM Monday.
- At or after 9:00 AM Monday → `slack_send_message` (post immediately).

**Use this exact format.** Use medal emoji for ranks 1-3, then "4th", "5th", "Nth" for the rest. Italicize the metric in the footer.

```
*MTD Employee Sales Rankings — Retail Sales Excluding Fees (Bravo POS)*
📊 Period: [start–end]

🥇 *[Employee Name]* ([STORE]) — $X,XXX.XX
🥈 *[Employee Name]* ([STORE]) — $X,XXX.XX
🥉 *[Employee Name]* ([STORE]) — $X,XXX.XX
4th *[Employee Name]* ([STORE]) — $X,XXX.XX
5th *[Employee Name]* ([STORE]) — $X,XXX.XX
...
Nth *[Employee Name]* ([STORE]) — $X,XXX.XX

_Source: Bravo POS · Employee Activity report. Multi-store employees summed across stores._
```

- Multi-store employees show all their stores in parens with a `+`, e.g., `(HAR + LEX)`.
- Include $0.00 and negative figures at the bottom — don't filter them.
- List ALL non-SYSTEM employees who appeared, even if their value is $0.00.

============================================================
STEP 5 — Save the spreadsheet
============================================================

Save to `/Users/joshuadavis/Documents/Claude/Scheduled/employee-sales-rankings-YYYY-MM-DD.xlsx` with two sheets:
- **Sheet 1 "Employee Sales Rankings"** — overall ranked list (Rank, Employee, Store(s), Retail Sales Excluding Fees). Gold/silver/bronze fill on top 3. Brand colors: Purple `#2D1A5E`, Blue `#0099DD`. Arial throughout.
- **Sheet 2 "Per Store"** — store-by-store breakdown with employees sorted highest-to-lowest within each store.

============================================================
VERIFY BEFORE POSTING
============================================================
- Numbers came from "Retail Sales Excluding Fees," NOT "Total Productivity."
- The Slack header says "Retail Sales Excluding Fees" so the team can see which metric.
- Multi-store employees summed once across stores (no double-counting).

## If something goes wrong
- **Pipeline failure (any store)**: include the store in the rankings if you got any data; note the failure in a footer line.
- **All 5 cells failed**: DM Joshua and stop; he'll restart the watcher.

## Background
This SKILL was rewritten 2026-05-12 to use the Bravo Data Extraction pipeline instead of driving Bravo via computer-use.
