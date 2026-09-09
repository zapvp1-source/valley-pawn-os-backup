---
name: task-hygiene-sweep
description: Monthly audit of scheduled tasks for stale/dead debris — auto-deletes obvious test/smoke junk, DMs Joshua a review list for anything ambiguous. Prevents the 37-task pileup from recurring.
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
You are running the monthly task-hygiene sweep for Full Circle Finance Inc / Valley Pawn's Cowork scheduled-task list. This exists because on 2026-08-10 the list had accumulated 37 dead/debris tasks (old test/smoke tasks, superseded workflows, disabled 75-126 days with no successor) that nobody had cleaned up. This task's job is to make sure that never happens again.

Read the enterprise-map skill first for context, and vp-operating-rules for the hard rules (no diagnosis from metadata, read CHANGELOG before build/fix/diagnosis) if this task ever needs to touch pipeline code (it shouldn't — this is read/report/delete only on the scheduler, not on Bravo).

STEP 1 — Pull the full task list.
Call mcp__scheduled-tasks__list_scheduled_tasks. It is large (1000+ lines) and will likely exceed the inline token limit and get saved to a file — if so, read that file in chunks (or delegate to a general-purpose subagent to read it fully and report back a structured summary) rather than truncating your view of it.

STEP 2 — Classify every task.
For each task, using "today" as this run's actual date:
- LIVE: enabled:true. Never touch these no matter what.
- AUTO-DELETE CANDIDATE (conservative, safe tier): enabled:false AND disabled/stale for 60+ days (no lastRunAt in the last 60 days, or never ran and created 60+ days ago) AND the taskId or description contains an obvious throwaway marker: smoke, test, probe, debug, scratch, verify-once, one-off, backfill-once, firstrun, autofix, watcher-heal, or a literal date stamp in the id (e.g. -2026-06-10) suggesting it was a one-time fix task that already did its job.
- REVIEW CANDIDATE (do NOT auto-delete): enabled:false AND stale 30+ days, but does NOT match the throwaway-marker pattern above. This includes anything that looks like it could be a real business workflow that's just dormant (e.g. named after a report, a store process, a recurring business function) — even if you're fairly confident it's dead, a human should confirm, because dormant-but-still-wanted tasks exist (this happened on 2026-08-10 with monday-store-rankings, which looked dead by every mechanical signal but was actually a paused-pending-migration real workflow).
- Anything with fireAt in the future: always leave alone regardless of enabled state.

STEP 3 — Execute the safe tier only.
Delete every AUTO-DELETE CANDIDATE using mcp__scheduled-tasks__delete_scheduled_task. Keep a list of what you deleted and why (one line each).

STEP 4 — Report, don't act, on the ambiguous tier.
If there are REVIEW CANDIDATEs, do not delete them. Compile a short list: taskId, how long it's been disabled, and a one-line guess at whether it looks safe to remove or worth keeping dormant.

STEP 5 — Notify Joshua.
Send Joshua ONE Slack DM (channel D03BHQH5VGT) in plain everyday language — no jargon, no file paths, no error-code-style text. Cover: how many tasks were auto-deleted (just the count, not a wall of names), and if there are REVIEW CANDIDATEs, name them plainly and ask him to confirm before you remove them next month (or say "reply here if any of these should stay"). If there was nothing to clean up this month, send a short one-liner saying the schedule is clean, no action needed — don't skip the DM entirely, a monthly silent confirmation that the sweep ran is itself useful.

STEP 6 — Log it.
Append a dated entry to /Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/BRAVO_HEALTH_RUNBOOK.md (or if that's not the right home by the time you run, use whatever the current canonical ops log is — check enterprise-map) recording what was auto-deleted and what's pending review, so the next sweep and any human reading the runbook has a paper trail.

Follow the standard failure-DM policy: if this run itself fails or errors out, send Joshua ONE plain-language DM saying the hygiene sweep didn't complete — no technical detail in that DM, put technical detail only in your own run output for the next session to pick up.