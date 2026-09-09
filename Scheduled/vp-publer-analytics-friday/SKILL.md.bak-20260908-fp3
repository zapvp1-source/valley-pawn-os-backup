---
name: vp-publer-analytics-friday
description: Friday 4 PM ET — Publer API weekly performance digest: top/bottom 20% by engagement, writes weekly-adjustments.json for Monday's batch, DMs Joshua a one-line digest. Replaces the broken Meta Graph analytics loop.
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


> ⚠️ **FAILURE HANDLING (Rule 16, supersedes the 2026-07-22 v2 DM policy — updated 2026-09-06).** Failure notices NEVER go to Slack — not to a team channel, not to a store manager, and not to Joshua's DM. If this run fails or cannot complete its core work, append one dated plain-language line plus the technical detail to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/STATUS.md` under a `## Run holds` heading and stop. The next session picks it up from there. Anything that does go to the field stays in plain everyday language — no error codes, no tool or file names. This replaces every 'DM Joshua that it did not complete' and every 'stay silent on Slack' instruction elsewhere in this file.


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
This is an automated run of a scheduled task. The user is not present. Execute autonomously. End with <run-summary>one or two sentences</run-summary>.


## Job
Close Valley Pawn's weekly content loop using PUBLER's analytics API (the Meta Graph API path is retired/blocked — never use it, never browser-fallback to instagram.com/facebook.com).

## Steps
1. Run the digest via the Control-your-Mac osascript tool:
   `do shell script "cd ~/Documents/Claude/Projects/'Refine Social Media' && python3 publer_weekly_digest.py 2>&1 | tail -15"`
2. The script pulls last-7-day post-level insights across all connected Publer accounts, ranks by engagement, identifies top/bottom 20%, classifies content types, and writes:
   - `friday_digests/friday_digest_{date}.md` (full report)
   - `weekly-adjustments.json` (Monday's vp-content-batch-weekly reads this — the adjust loop)
   - appends to `adjustments_log.jsonl` and `~/.vp-studio/lessons.md`
3. Its LAST stdout line starts with "DIGEST:". DM exactly that line (minus the "DIGEST: " prefix) to Joshua Davis on Slack (find him via user search), prefixed with "📊 Weekly social digest — ".
4. If the line says no insights were available (Publer analytics can lag 24-48h), do NOT DM Joshua — note it in run-summary only.
5. Sanity check: confirm weekly-adjustments.json was updated today (osascript: `do shell script "stat -f '%Sm' ~/Documents/Claude/Projects/'Refine Social Media'/weekly-adjustments.json"`). If not, treat as failure (silent).

Guardrails: Publer API only. No Meta Graph API. No instagram.com/facebook.com browsing. Do not modify the digest script during a run — if it errors, report in run-summary and let interactive Claude fix it.


## ADDENDUM 2026-09-06 — the DM text comes from the engine

Keep running `publer_weekly_digest.py` (it still writes `friday_digests/`, `weekly-adjustments.json`,
`adjustments_log.jsonl` and `~/.vp-studio/lessons.md`, which the Monday planner reads).

Then, before DMing Joshua:
`do shell script "cd '/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media' && python3 -m vp_social digest --days 7 2>/dev/null"`
- exit 0 → that stdout **is** the DM. Send it verbatim.
- exit 2 → send no DM; append the reason to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/STATUS.md`.

**WHY:** the old digest counted posts the same broken way the recap did — it reported 57 posts for
Aug 29-Sep 4 when 89 published, and 64 vs 93 the week before. The engine's counts come from the
ledger; the engagement figures still come from Publer's insights endpoint.
