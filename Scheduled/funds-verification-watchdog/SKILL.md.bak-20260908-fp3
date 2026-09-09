---
name: funds-verification-watchdog
description: 6:45 PM daily watchdog — checks if daily-funds-verification posted to #daily-funds-reconcilation today. If no post found, silently iterates to fix (re-runs the verification flow); never DMs and never posts failure notices to Slack.
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



> ⚠️ **FAILURE POLICY — STRICT, SET BY JOSHUA 2026-06-08.**
> 1. **Never DM Joshua. Never DM anyone.** No "watchdog alert," no escalation, no "the 6 PM task failed silently."
> 2. **Never post failure to Slack.** No "no post detected today," no error notices. Slack only ever sees the SUCCESS markdown table from the actual verification run.
> 3. **On a missing post, silently iterate to fix.** Trigger a re-run of the verification logic (drop a fresh trigger, restart the watcher if needed, retry until success or budget exhausted), and post the SUCCESS table only when 5 stores reconcile cleanly.
> 4. If iteration exhausts the budget without success: exit silently with no notification of any kind.

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
You are a watchdog for the `daily-funds-verification` scheduled task. Your job: confirm a verification report posted today, and if not, run the verification yourself silently.

**Time budget:** ~25 minutes total from task start.

---

# Step 1 — Check Slack for today's post

Use `slack_read_channel` on `C0B3R9B3S8H` (#daily-funds-reconcilation):
- `oldest` = today's midnight Unix timestamp (`do shell script "date -v0H -v0M -v0S +%s"`)
- `limit` = 10
- `response_format` = concise

Look for any message posted today containing `Daily Funds Verification`, `funds verification`, `Matched`, or `all clear`.

**If a matching post IS found today:** Exit silently. Everything is fine.

**If NO matching post is found today:** Proceed to Step 2.

---

# Step 2 — Silent iterate-to-fix

The 6 PM `daily-funds-verification` did not complete to a posting state. Re-run its work yourself, following the same flow defined in `/Users/joshuadavis/Documents/Claude/Scheduled/daily-funds-verification/SKILL.md`:

1. Slack scan of the 5 funds channels for today's window (same channel IDs / store codes as the main task).
2. Drop a Bravo trigger for `safe-register-journal` across all 5 stores for today's date. Trigger ID prefix `watchdog-funds-verification-`.
3. Poll the result JSON (10 min timeout).
4. If the watcher appears hung (trigger not claimed within 2 min, or all-cells-error result): silently restart the watcher via a one-shot Cowork scheduled task that runs `_restart_watcher.ps1` through `prlctl exec` (the same pattern documented in the main task's Step 2e). Re-drop the trigger after the restart.
5. Iterate the retry loop until either (a) all 5 stores have a verified result, OR (b) total time budget is exhausted.
6. On full success: post the reconciliation table to `#daily-funds-reconcilation` (`C0B3R9B3S8H`) and save the markdown report at `/Users/joshuadavis/Documents/Claude/Projects/Daily Funds Verification/<YYYY-MM-DD> Funds Verification.md`.
7. On budget exhaustion: save the partial markdown report and **exit silently** — no DM, no Slack post.

---

# Hard rules (recap)

- **No DMs ever.** This watchdog used to DM Joshua on no-post. That behavior is removed.
- **No Slack posts on failure.** Only post on full reconciliation success.
- **Iterate silently.** A missing 6 PM post means do the work yourself; don't tell anyone it was missing.
- **Markdown file always saved.** The file is the only audit trail.

---

# Background

This task runs at 6:45 PM ET daily, 45 minutes after the main verification.

2026-06-08 policy rewrite: the original behavior (DM Joshua if no post) is replaced with silent iterate-to-fix. Per Joshua's explicit direction: "i dont want any DMS, i need it fixed, do not DM on fails or anyone else. Post nothing if it fails and then iterate to fix it."

<!-- migrated to working model 2026-06-15 -->