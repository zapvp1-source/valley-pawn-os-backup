---
name: zoom-voicemail-eod-review
description: Daily 5:45 PM close-out — re-review every missed call/voicemail from today across all Zoom Phone store lines and post which ones still never got a callback, so nothing carries into tomorrow unresolved.
---

This is an automated scheduled task run. The user (Joshua) is not present to answer questions — execute autonomously, make reasonable choices, and note them in your output. Only take Slack-posting ("write") actions as described below; nothing else.

## Purpose

This is the END-OF-DAY companion to the `zoom-voicemail-alert` task (which runs every 20 min, Mon–Sat 9am–7:59pm, and alerts on each NEW missed call/voicemail as it happens, suppressing anything already resolved). That task is intraday and incremental — it dedupes against a state file so it never re-alerts on the same event twice.

THIS task is different: at 5:45 PM every day, it re-reviews EVERY missed call/voicemail from TODAY (not just new ones since the last check) and publishes a final list of whatever, as of right now, still has NOT received a callback — a last-chance catch before the day closes, independent of the intraday dedupe state. A call could have been correctly skipped intraday only because a callback attempt looked in-progress, or an alert could have been posted but never acted on — this is the safety net that catches both.

Read the `valley-pawn-context` skill first for store names/numbers if needed.

## STEP 1 — Get the live store phone line roster (same as zoom-voicemail-alert)

Using the Claude in Chrome MCP (load via ToolSearch with query "select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__tabs_close_mcp" if not already loaded):

1. Create a tab, navigate to `https://zoom.us/myhome`. Confirm signed in (top-right avatar "JD" / Full Circle Finance Inc).
2. **If you land on a Zoom sign-in page (session expired):** do NOT log in yourself. Send one Slack DM to Joshua Davis (user ID `U03BB52MDSA`): "⚠️ Zoom admin session expired — please open zoom.us in Chrome and sign in once so the end-of-day voicemail review can run." Then stop this run entirely (skip everything below).
3. Navigate to `https://zoom.us/pbx/page/telephone/phoneUsers#/users/phone-users/assigned`. Use `get_page_text` on the Users table. Parse each row into `email`, `extension`, `number`.
4. Map each row to a store name using the Number(s) column against the canonical store phone list in `valley-pawn-context` (Culpeper (540) 445-5510, Waynesboro (540) 221-6346, Harrisonburg (540) 574-4500, Lexington (540) 461-8349, Roanoke (540) 562-0776). Joshua's own row (jdavis@fcfpawn.com) maps to whichever store owns its Number(s) value (currently Lexington). If a row's number doesn't match any of the 5, still include it labeled "Unmapped — number (X)".
5. Process ALL rows found — the roster grows as more stores get Zoom Phone lines, no edit needed here when that happens.

## STEP 2 — Pull EVERY row from TODAY for each store line (not just new ones)

For each store line's user detail page, click "History", set both From and To date fields to TODAY, and read the full table (page through if more than one page). Capture Direction, From, To, Start Time, Event, Call Result, Voicemail, Duration for every row — Inbound AND Outbound. You need Outbound too, for the resolution check in Step 3.

## STEP 3 — Identify today's missed-call/voicemail candidates and check resolution

1. Candidates = Inbound rows where Call Result is not `Answered` (e.g. Busy, Ring Timeout, Abandoned) and/or Voicemail = Y.
2. For each candidate, normalize the caller's number to its last 10 digits and check BOTH:
   - **Staff callback:** a later Outbound row from the same store user, to the same 10-digit number, with Start Time after the missed call's Start Time, and Call Result = `Connected`. If found → resolved, exclude.
   - **Customer reconnected:** a later Inbound row FROM that same 10-digit number, Start Time after the missed call's Start Time, Call Result = `Answered`. If found → resolved, exclude.
3. Anything with neither → still needs a callback as of 5:45 PM today. This is a fresh full-day sweep — do NOT consult or write the `zoom-voicemail-alert` dedupe state file (`~/Documents/Claude/Projects/Valley Pawn OS/.zoom_voicemail_alert_state.json`); that file belongs to the other task only. This task is stateless — it always re-evaluates the whole day fresh.
4. Note the same honest limit as the intraday task if ever asked: this only sees activity on the Zoom-provisioned store line pulled — a callback from a personal cell or a different number is invisible to it.

## STEP 4 — Post ONE end-of-day summary to Slack, always (unlike the intraday task, this one posts every run — it's the daily close-out record, not a noisy per-event alert)

Post to **#voicemails-missed-calls** (channel ID `C0BP4M3B99R` — if this returns an "is_archived" or invalid-channel error, run `slack_search_channels` for "voicemail" with `include_archived: true` to find the live channel, post there instead, then update THIS task's own prompt via `mcp__scheduled-tasks__update_scheduled_task` to replace the stale channel ID so the next run doesn't repeat the failure — same recovery pattern the intraday task uses).

If there ARE still-unresolved rows, post:
```
🌙 *End-of-Day Voicemail/Missed Call Close-Out — {today's date}*

The following still have NOT been called back today — please handle before close or first thing tomorrow:

*Harrisonburg*
• [caller name or number], [time] — 🔴 VOICEMAIL LEFT, no callback yet.
• [caller name or number], [time] — missed (no voicemail), no callback yet.

*Waynesboro*
• [caller name or number], [time] — missed (no voicemail), no callback yet.

_Pulled from Zoom Phone admin history, full-day sweep. Calls already resolved (staff callback or customer reconnected) are excluded._
```
Only list stores with outstanding items.

If EVERYTHING from today was resolved (or there were no missed calls/voicemails today at all), post a short all-clear instead:
```
🌙 *End-of-Day Voicemail/Missed Call Close-Out — {today's date}*

All clear — every missed call/voicemail today was called back or the customer reconnected. Nothing outstanding heading into tomorrow.
```

## ERROR HANDLING (same Failure Alert Policy v2 as zoom-voicemail-alert)

If the Zoom UI has changed and you can't read the History tab or parsing breaks: do NOT guess or post a broken summary. Send ONE plain-language Slack DM to Joshua Davis (user ID `U03BB52MDSA`) — e.g. "⚠️ End-of-day Zoom voicemail review couldn't read the call history page today — worth a look when you have a minute." Never send failure notices to #voicemails-missed-calls, #general, or any store channel. One attempt, then either succeed or send the single DM and stop.

## Notes

- This is additive, net-new automation alongside `zoom-voicemail-alert` — does not touch that task's logic, schedule, or state file.
- As more stores get Zoom Phone lines (Culpeper, Roanoke), Step 1's fresh-roster-every-run design picks them up automatically.
- Close every Chrome tab you opened before finishing.