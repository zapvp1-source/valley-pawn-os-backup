---
name: chekkit-new-review-alert
description: Hourly business-hours check (9 AM–9 PM ET) for new Chekkit review notifications; post immediately to Slack #google-reviews if in business hours, otherwise schedule for 10 AM next day.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> ⚠️ **FAILURE ALERT POLICY (still binding):** If this run fails, errors out, or cannot complete its core work, do NOT message Joshua, Preston, or anyone else, in any medium. Instead append ONE row to the fleet failure ledger `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` (use `mcp__Control_your_Mac__osascript` `do shell script "printf ... >> file"` if file tools cannot reach it) in exactly this form: `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or: yes, <the single thing only Joshua can do>> | OPEN |`. The `fleet-guardian` task reads this ledger twice a day, re-runs whatever is safe to re-run, rolls anything that truly needs Joshua into `Life OS/HUMAN_QUEUE.md`, and sends Joshua at most ONE consolidated plain-language DM per day. Individual tasks never DM about failures. All technical detail goes in the run output/log/STATUS file for the next Claude session to pick up. Never send failure notices to any team channel, store manager, employee, or Preston. FIELD COMMUNICATION RULE (unchanged): anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This v3 supersedes both the v2 one-line-DM rule and any older rule in this file.
>
> ⚠️ **FIELD COMMUNICATION STANDARD v3 (binding — read in full before posting anything to a team channel or employee DM):** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/FIELD_COMMUNICATION_STANDARD.md`. Summary: run the routing test (is this something a clerk needs to know/act on today — if no, it's internal, it does not go to the field); plain everyday language only, no tool/system/pipeline names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "pipeline," "handler," "watchdog," "sync," "CSV," "export"); no file paths, doc IDs, task IDs, or spreadsheet cell/column refs in the posted text; no meta-commentary about the automation itself ("verified against," "supersedes," "this is a manual test run," "pulled automatically from"); lead with the one-line takeaway; ~100 words max for a routine post; no signature footers. **This task's celebratory one-liner is already a good model — keep it exactly this short and plain.** If anything later in this file conflicts with this standard, this standard wins.



> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do.

You are monitoring Gmail for new Chekkit review notification emails and posting a quick celebratory message to the Slack #google-reviews channel.

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

## Steps

1. **Search Gmail** for recent Chekkit review emails:
   - Search query: `from:support@chekkit.io subject:"You got a new review" newer_than:1d`
   - If no results, stop — nothing to do.

2. **For each email found**, extract:
   - **Store name**: from the subject line (e.g. "You got a new review for Valley Pawn - Waynesboro" → "Waynesboro")
   - **Star rating**: from the snippet/body (e.g. "You got a new 5 star review from...")
   - **Reviewer name**: from the snippet/body (e.g. "...review from Miriam Brown.")

3. **Check Slack for duplicates BEFORE posting.** For each review, search the #google-reviews channel to see if a message about that reviewer has already been posted:
   - Use `slack_search_public` with query: `"[Reviewer Name]" in:<#C04NDE52U2G>` (use the exact reviewer name in quotes)
   - If a matching message is found, **skip this review** — it was already posted.
   - Only proceed to post if NO matching message is found.

4. **Determine whether to post immediately or schedule for 10 AM next day.**

   Check the current local time (US Eastern):
   - **Business hours = 9:00 AM to 9:00 PM Eastern**
   - If the current time is within business hours → **post immediately** using `slack_send_message`
   - If the current time is outside business hours (9 PM–9 AM) → **schedule the message for 10:00 AM the next morning** using `slack_schedule_message`

5. **Post or schedule a Slack message** to the #google-reviews channel (channel ID: C04NDE52U2G) for each NEW (not yet posted) review. Keep it super short and celebratory:

   Format: `Nice job Team [Store Name]! You just got a new [X] star review from [Reviewer Name]! ⭐`

   Examples:
   - "Nice job Team Waynesboro! You just got a new 5 star review from Miriam Brown! ⭐"
   - "Nice job Team Lexington! You just got a new 5 star review from Shane Gilliam! ⭐"
   - "Nice job Team Culpeper! You just got a new 4 star review from John Smith! ⭐"

   For the store name, use the short city name only (Waynesboro, Lexington, Culpeper, Harrisonburg, Roanoke). The subject line format is "You got a new review for Valley Pawn - [City]" or "You got a new review for Valley Pawn-[City]" (with or without spaces around the dash).

## Important
- **ALWAYS check Slack before posting** to prevent duplicate messages. The Gmail MCP does not support marking emails as read, so the duplicate check in Slack is the primary safeguard.
- Use `newer_than:1d` in the Gmail search since the task runs hourly — keeps the email window small and manageable while still catching anything missed in a prior run.
- If there are multiple new reviews, handle each one separately (check for duplicates, then post or schedule individually).
- Do NOT DM anyone — only post to #google-reviews.
- Keep messages short and fun. No extra commentary or formatting beyond the single line.