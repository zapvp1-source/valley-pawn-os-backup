---
name: nics-weekly-mtd-ranking
description: Every Monday 9:30 AM: pull month-to-date FFL transfers for all 5 stores from Bravo, rank stores by transfers + revenue, and post the MTD ranking to #ffl-transfer-performance.
model: claude-sonnet-5
---

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
Weekly MONTH-TO-DATE FFL transfer ranking, RANKED BY REVENUE. Pull MTD nics-transfers for all 5 stores, rank by revenue, post to #ffl-transfer-performance. BOUNDED — reuse the pipeline; do not modify the handler, do not touch the display, do not re-enable scrap.

CONTEXT: Read skills enterprise-map, valley-pawn-context, bravo-context. Bravo folder access via mcp__Control_your_Mac__osascript `do shell script` only. PROJECT: /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction. CSVs: <DIR>/output/<start>_to_<end>_<STORE>_nics-transfers.csv. Stores WAY,CUL,HAR,LEX,ROA.

STEP 0 — dates (python): MTD range: start = first day of CURRENT month, end = TODAY. YYYY-MM-DD.

STEP 1 — contention guard: watcher idle (no <DIR>/logs/*.log modified ~2 min; nothing in <DIR>/triggers or triggers/claimed). If busy, wait up to 10 min; if still busy, DM Joshua (U03BB52MDSA) that it was busy and skip this week.

STEP 2 — pull: drop ONE trigger nics-mtd-<ts>.json, reports [{"name":"nics-transfers","stores":["WAY","CUL","HAR","LEX","ROA"],"date":"<start>..<end>"}]. Poll ~12-15 min. Verify all 5 store CSVs for the range exist; re-run any missing store ONCE (single-store trigger). NOTE: a store that legitimately returns 0 for the period is valid — label a store "pending" ONLY if its pull errored/produced no csv, never imply a real 0 is a failure.

STEP 3 — tally + RANK BY REVENUE: per store COUNT = data rows, REVENUE = sum of the Amount column (last field; python csv to handle quoted commas). Rank stores by REVENUE descending (transfer count as the tiebreak).

STEP 4 — post to Slack #ffl-transfer-performance (id C0BPH5T1NFL): a markdown table titled "FFL Transfers — Month-to-Date (<Month> 1–<day>)" with columns Rank | Store | Revenue | Transfers, rows ordered by revenue, plus a company Total row. One line calling out the revenue leader and any store lagging. If a store is pending/failed, say so explicitly. Concise. If the pull wholly failed, DM Joshua what went wrong instead of posting.

Never present partial data as complete. Done after this run.