---
name: weekly-social-media-recap
description: Monday 9 AM ET — posts a team-visible recap of everything published across Valley Pawn's social channels in the last 7 days to #social-media (read-only Publer verification, not a manifest read)
model: claude-sonnet-5
---

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard).**
> This task runs on Joshua's Mac Studio and DOES have local machine access via `mcp__Control_your_Mac__osascript`. That tool may be deferred rather than pre-loaded at task start.
> 1. If `ToolSearch` is available, load it first: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it with a trivial `do shell script "echo READY"`. If it returns, proceed.
> 3. If it errors, wait ~20s and re-probe, up to 12 minutes total (24 probes).
> 4. Only after that full wait may you treat local access as genuinely unavailable — never conclude "no Mac access / cloud sandbox only" before exhausting this probe loop.
> **Filesystem rule:** all reads/writes under `/Users/joshuadavis/Documents/Claude/...` go through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** each osascript call is killed at ~25s. Never sleep longer than ~18s in one call.

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
> ⚠️ **FAILURE HANDLING (Rule 16, supersedes the 2026-07-22 v2 DM policy — updated 2026-09-06).** Failure notices NEVER go to Slack — not to a team channel, not to a store manager, and not to Joshua's DM. If this run fails or cannot complete its core work, append one dated plain-language line plus the technical detail to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/STATUS.md` under a `## Run holds` heading and stop. The next session picks it up from there. Anything that does go to the field stays in plain everyday language — no error codes, no tool or file names. This replaces every 'DM Joshua that it did not complete' and every 'stay silent on Slack' instruction elsewhere in this file.

This is an automated run. The user is not present. Execute autonomously. End with `<run-summary>one or two sentences</run-summary>`.

## Job

Joshua wants a standing, team-visible weekly record of what actually posted across all Valley Pawn social channels — separate from the existing Publer engagement digest (`vp-publer-analytics-friday`, DMs Joshua only) and the publish-verification DM (`vp-content-batch-postflight`, DMs Joshua only). This task is net-new and additive (Rule #4) — it does not modify either of those.

Post to the **#social-media** Slack channel (channel ID `C0BMRC2LN3D`) every Monday: a recap of everything published in the trailing 7 days, verified straight from Publer's API (Rule 12 — verify against actual output, never a manifest or run-log).

## Steps

1. Produce the recap with the deterministic formatter (osascript):
   `do shell script "cd '/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media' && python3 -m vp_social recap --days 7 2>/dev/null"`
   - **exit 0** — stdout IS the Slack message. Post it to `C0BMRC2LN3D` (#social-media) **verbatim**
     via `slack_send_message`. Do not reformat it, do not add a preamble, do not recompute a number.
   - **exit 2** — stdout is empty on purpose (Rule 18: withhold, don't caveat). Post NOTHING and append
     the stderr line to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/STATUS.md` under `## Recap holds`.

2. That is the whole job. There is no marker extraction, no zero-post special case, and no fallback
   to hand-counting: a zero week is itself treated as a withhold condition by the formatter, because
   every real zero week to date has been a read failure, not an actual outage.

**WHY (2026-09-06):** the previous step ran `weekly_social_recap.py`, which called Publer's `/posts`
with no `from`/`to`. Publer silently returns a default slice, so the recap reported 15 posts for
Aug 24-31 when 88 had actually published, and 16 for Aug 17-24 when the real number was 47. The
August month-in-review inherited the error. `python3 -m vp_social recap` reads the local ledger,
which is synced from Publer with explicit date ranges and full pagination. `weekly_social_recap.py`
is left on disk but is no longer the source of the number.

**Timing note:** this task fires Monday 9:40 AM and covers the PRIOR seven days. The weekly content
batch fires later the same day (Mon 1:40 PM, postflight 4:40 PM), so this recap never includes
today's batch — that is intended, not a gap.
