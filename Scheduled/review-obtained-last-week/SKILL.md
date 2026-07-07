---
name: review-obtained-last-week
description: Monday 3 AM (overnight) — pull prior-week (Sun–Sat, 7 days) Google review counts from Chekkit for all 5 stores, schedule ranked Slack post to #google-reviews for 9 AM Monday.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are running as an overnight background task at 3 AM Monday. Pull last week's Google review counts for all 5 Valley Pawn locations from Chekkit, then post a ranked Slack summary to #google-reviews — scheduled for 9:00 AM ET the same Monday morning on a normal run, or sent immediately if the task fired late (see Step 7).

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

## Prior-week definition (IMMUTABLE — do not deviate)

The "prior week" is the 7-day window **Sunday through Saturday**, ending on the Saturday immediately before the publish Monday. Always target the NEXT upcoming Monday 9 AM publish — never the day the task actually fires.

Because this task always fires on a Monday at 3 AM, this window is exactly what Chekkit's **"Last week"** preset returns. USE THE PRESET — it matches Sun–Sat last week reliably when the task runs on a Monday.

Examples:
- Publishes Mon Apr 27, 2026 → prior week = Apr 19 (Sun) – Apr 25 (Sat)
- Publishes Mon May 4, 2026 → prior week = Apr 26 (Sun) – May 2 (Sat)
- Publishes Mon May 11, 2026 → prior week = May 3 (Sun) – May 9 (Sat)
- Publishes Mon May 18, 2026 → prior week = May 10 (Sun) – May 16 (Sat)

After selecting "Last week," ALWAYS read back the date label Chekkit displays (e.g. "May 10 - May 16, 2026") and use those exact dates in the post title. If the displayed range is not a Sun–Sat 7-day window ending on the most recent Saturday, ABORT and DM Joshua — something is off.

## Steps

1. Compute the upcoming Monday (next Monday, or today if today is Monday) and from that derive the expected Sun–Sat prior-week range for sanity-checking Chekkit's label.
2. Navigate to dashboard.chekkit.io via Chrome MCP (login is saved in Chrome — do not ask Joshua to log in). The URL is **dashboard.chekkit.io**, NOT app.chekkit.com.
3. Go to Reviews → Leaderboard. Click the date-range dropdown (top-right of "Leaderboard Overview"). Select **"Last week"**. Wait for the page to reload and confirm the displayed range matches the expected Sun–Sat window from Step 1. If it doesn't match, ABORT.
4. Scroll to the Location Leaderboard and record each Valley Pawn store's Reviews count for that window:
   - Valley Pawn – Culpeper
   - Valley Pawn – Harrisonburg
   - Valley Pawn – Lexington
   - Valley Pawn – Roanoke
   - Valley Pawn – Waynesboro
   (Ignore the "Tax Experts" row — not our business.)
5. For the current overall rating, use the per-store Review Overview tab (switch the location in the top-left picker). Record each store's top-line rating.
6. Build a ranked summary post — order stores by reviews received that week, descending. Break ties alphabetically. Include the explicit Sun–Sat date range in the title.
7. Post the ranked summary to #google-reviews (channel ID **C04NDE52U2G**), choosing the method by the current time vs. the 9:00 AM ET publish slot:
   - **Compute the current epoch time** (e.g. `date +%s`) and the Unix timestamp for 9:00 AM ET this Monday.
   - **If 9:00 AM ET is still ≥ ~5 minutes in the future** (normal on-time 3 AM run): use `slack_schedule_message` with `post_at` = the 9:00 AM ET timestamp.
   - **If 9:00 AM ET has already passed or is < 5 minutes away** (the task fired late — e.g. the machine was asleep overnight and caught up later in the day): DO NOT schedule for the past — `slack_schedule_message` rejects past times with `time_in_past`. Instead post the report **for the same correct prior week** right away using `slack_send_message` to the same channel. The data window does not change; only the delivery time does. This guarantees the Monday report still lands today for the right week rather than failing silently or going stale a week later.
   - Before posting, honor the duplicate guard in Notes: if a correct post for this week's range is already scheduled or already in the channel, do not post a second one.

## Message format

*Google Reviews — Week of {start_date} – {end_date}*

Ranked by new reviews received last week:

1. *{Store}* — {N} new reviews ({rating} ★ overall)
2. ...

Total new reviews this week: {sum}

Source: Chekkit

## Notes

- Slack scheduled messages cannot be edited or deleted via API — if a wrong one was scheduled, Joshua has to clear it from Slack's "Scheduled" view.
- Do not schedule more than one post for the same Monday. If a post is already scheduled for that 9 AM slot and you can't verify it's correct, abort and DM Joshua instead.
- This task is intentionally Monday-only. The Sun–Sat preset assumption breaks if the task fires on any other day; if you must run it manually outside Monday, set the date range to the explicit Sun–Sat window for the prior calendar week instead of relying on the preset.
- **Late-firing is handled in Step 7.** Because Monday overnight tasks can fire many hours late when the machine is asleep overnight and catches up later in the day, never assume 9:00 AM ET is still ahead. Always compare against the current time and fall back to an immediate `slack_send_message` if the slot has passed (see Step 7). The earlier `time_in_past` failure on 2026-06-15 was caused by blindly scheduling for a 9 AM slot that had already passed.