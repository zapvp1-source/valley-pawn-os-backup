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
⚠️ **FAILURE ALERT POLICY (platform standard, set by Joshua 2026-07-22, v2):** If this run fails or cannot complete, send Joshua ONE plain-language Slack DM (channel D03BHQH5VGT): `⚠️ Scheduled task "weekly-social-media-recap" did not complete — <date>.` Nothing technical in that DM. Never send failure notices to #social-media or any other team channel. This task's normal weekly output (the recap) always goes to #social-media regardless — that is not a "failure notice," it's the task's job.

This is an automated run. The user is not present. Execute autonomously. End with `<run-summary>one or two sentences</run-summary>`.

## Job

Joshua wants a standing, team-visible weekly record of what actually posted across all Valley Pawn social channels — separate from the existing Publer engagement digest (`vp-publer-analytics-friday`, DMs Joshua only) and the publish-verification DM (`vp-content-batch-postflight`, DMs Joshua only). This task is net-new and additive (Rule #4) — it does not modify either of those.

Post to the **#social-media** Slack channel (channel ID `C0BMRC2LN3D`) every Monday: a recap of everything published in the trailing 7 days, verified straight from Publer's API (Rule 12 — verify against actual output, never a manifest or run-log).

## Steps

1. Run the recap script via osascript:
   `do shell script "cd ~/Documents/Claude/Projects/'Refine Social Media' && python3 weekly_social_recap.py --days 7 2>&1"`
   This is a read-only script (`weekly_social_recap.py`, net-new, added 2026-08-04) that calls `PublerClient.list_posts(state='published')`, filters to the last 7 days by `scheduled_at`, and groups counts by platform and by store/page. It does NOT touch `publer_weekly_digest.py` or `friday_close_engagement.py`.
2. The script's stdout contains the recap text between the marker lines `RECAP_START` and `RECAP_END`. Extract exactly that text (do not include the marker lines themselves, do not include the urllib3/OpenSSL warning line if present).
3. Post that text to Slack channel `C0BMRC2LN3D` (#social-media) via `slack_send_message`. Use it verbatim — it's already Slack mrkdwn-formatted (bold headers, bullet counts).
4. If the script's post count is 0, still post — the recap should say "0 posts published this week" so an actual outage is visible to the team, not silently skipped. Do not suppress a zero result.
5. If the script errors (Publer API failure, missing config, etc.), do NOT post a broken/partial recap to #social-media. Instead follow the Failure Alert Policy above (one plain DM to Joshua) and write the raw error to `weekly_social_recap_error_{date}.log` in the same folder for the next session to diagnose.
6. Optional context check (not required to complete the post): if you want extra confidence before posting, cross-check the total against `#vp-studio-queue`'s last-7-days log-card count — they should be in the same ballpark since that channel logs each item as it's staged. A mismatch is not a failure, just worth noting in the run-summary.

## Cron

Monday 9:00 AM ET (`0 9 * * 1`) — after `vp-content-batch-weekly` (Mon 2:02 AM) and `vp-content-batch-postflight` (Mon 3:30 AM) have both run, so the week's Monday batch is already reflected in Publer by the time this posts.

## Hard rule

This task ONLY posts the weekly recap to #social-media. It never posts approval requests, never posts failure diagnostics to a team channel, and never modifies `vp-content-batch-weekly`, `vp-content-batch-postflight`, `vp-publer-analytics-friday`, or their scripts.