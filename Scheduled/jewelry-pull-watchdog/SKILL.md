---
name: jewelry-pull-watchdog
model: claude-haiku-4-5-20251001
description: Morning watchdog 9:15 AM (Tue-Sun): verify last night's jewelry-onhand CSVs exist; if missing, DM Joshua one plain-language alert.
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
Watchdog for the jewelry-onhand-nightly-pull task (runs 8:30 PM Mon-Sat). You run the following morning.

1. Get yesterday's date: via mcp__Control_your_Mac__osascript run `date -v-1d '+%Y-%m-%d %A'`.
2. If yesterday was Sunday: stores closed, no pull expected — end silently.
3. Check for last night's output: `ls ~/Documents/Claude/Projects/'Bravo Data Extraction'/output/ | grep '<YESTERDAY>_.*jewelry-case-counts'` via osascript.
4. If at least one store CSV exists for yesterday: healthy — end silently, post nothing.
5. If ZERO CSVs exist for yesterday: send ONE plain-language Slack DM to Joshua (channel_id D03BHQH5VGT) via the Slack connector, e.g.: "Heads up — last night's jewelry count pull didn't run (no data for <date>). Most common cause: the Claude app wasn't open at 8:30 PM. Open the app and I can run it manually, or it'll fire at the next 8:30 PM." Nothing technical, no team channels, no other messages.

Never touch Bravo. Never create triggers. Read-only check + one DM at most.