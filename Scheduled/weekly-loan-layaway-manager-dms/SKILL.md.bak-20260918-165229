---
name: weekly-loan-layaway-manager-dms
description: Monday 9 AM — DM each store's loan & layaway results to their team in Slack
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

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


> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, do NOT message Joshua, Preston, or anyone else, in any medium. Instead append ONE row to the fleet failure ledger `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` (use `mcp__Control_your_Mac__osascript` `do shell script "printf ... >> file"` if file tools cannot reach it) in exactly this form: `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or: yes, <the single thing only Joshua can do>> | OPEN |`. The `fleet-guardian` task reads this ledger twice a day, re-runs whatever is safe to re-run, rolls anything that truly needs Joshua into `Life OS/HUMAN_QUEUE.md`, and sends Joshua at most ONE consolidated plain-language DM per day. Individual tasks never DM about failures. All technical detail goes in the run output/log/STATUS file for the next Claude session to pick up. Never send failure notices to any team channel, store manager, employee, or Preston. FIELD COMMUNICATION RULE (unchanged): anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This v3 supersedes both the v2 one-line-DM rule and any older rule in this file.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. **TIER-1 FIX (2026-08-03): Step 1's old fallback posted a missing-results-file notice to #claude-updates, and Step 5 posted a run-confirmation there too. Both are internal/operational facts and now route to Joshua's DM only — #claude-updates is not used by this task anymore.** If anything later in this file conflicts with this standard, this standard wins.



> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do.

You are sending the weekly loan and layaway results to each Valley Pawn store team via Slack DM. The results were collected Sunday night and saved to `/Users/joshuadavis/Documents/Claude/loan-layaway-results-latest.json`.

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

## Step 1 — Read the results file
Read `/Users/joshuadavis/Documents/Claude/loan-layaway-results-latest.json` to get each store's loan and layaway numbers.

If the file doesn't exist or is more than 2 days old, DM Joshua (U03BB52MDSA) a plain-language line: "⚠️ Weekly loan & layaway results weren't ready this morning — the Sunday review may not have completed." Then stop. Do not post anything about this to any channel.

## Step 2 — Send store-specific DMs

Use `slack_send_message` to DM each person below with ONLY their store's results. Each message should be friendly, direct, and actionable — this lands in their inbox Monday morning before the store opens.

### Store teams and Slack user IDs:

**CUL — Culpeper**
- Sandi Cole: `U04C5DL5EKH`

**HAR — Harrisonburg**
- Walker Tapley: `U09UTFT4P7X`
- Andrew Clark: `U03BFDJH31B`

**LEX — Lexington**
- Uriah: `U09H9ES2LKA`
- Martin D.: `U05TV57FH0B`

**ROA — Roanoke**
- Benjie Moore: `U0631AECK4K`
- Cristofer Lopez: `U063E87TM70`

**WAY — Waynesboro**
- Chadd: `U04U136MF6V`

Also DM the operations manager with the full company summary:
- Preston Peters: `U03BWMEM9GR`

## Step 3 — Message format per store employee

Use this template for each DM (fill in their store's actual numbers):

```
Good morning! Here's your store's weekly loan & layaway snapshot for [Date]:

📊 *[STORE NAME] — Loan Health*
• Items past 75 days: [X]
• $ past 75 days: $[amount]
• % of loan balance: [X.X]% [✅ Within threshold / 🚨 Above 5% — needs attention]

🏷️ *[STORE NAME] — Layaways*
• Overdue layaways: [X]
• Items needing location: [X] [🔴 ACTION NEEDED if > 0]
• No payment in 30 days: [X]

[If any issues]: ⚠️ *Action needed:* [describe the specific issue — e.g., "You have 3 loans above the 75-day threshold exceeding 5% of your loan balance. Please review and pull tickets." or "You have layaways that need to be physically located in Bravo — please resolve ASAP."]

Have a great week!
```

## Step 4 — DM to Preston Peters (full summary)

Send Preston the full 5-store summary (same format as the #performance Slack post from Sunday night) plus any stores flagged for attention.

## Step 5 — Confirm with Joshua
DM Joshua (U03BB52MDSA) a brief one-line confirmation when all DMs are sent:
`✅ Weekly loan & layaway results delivered to all store teams. [X] stores flagged for attention.`
Do not post this confirmation to #claude-updates or any other channel — it's an internal status note for Joshua only.