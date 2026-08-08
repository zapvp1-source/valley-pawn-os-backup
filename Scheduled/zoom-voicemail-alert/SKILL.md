---
name: zoom-voicemail-alert
description: Every ~20 min during store hours — check Zoom Phone admin for new missed calls/voicemails on each store line and post an alert to Slack #voicemails-missed-calls so the team knows to call back.
---

You are checking Valley Pawn's Zoom Phone system for new missed calls / voicemails on each store's line, and alerting the team in Slack so nobody misses a customer callback. This mirrors the existing Chekkit "missed customer message" pattern but for Zoom Phone voicemails.

Read the `valley-pawn-context` skill if you need store names/numbers/hours for reference. Do the work yourself; don't ask permission to proceed.

═══════════════════════════════════════════════
BACKGROUND — why this exists (built 2026-08-07)
═══════════════════════════════════════════════
Valley Pawn has Zoom Phone lines at 3 stores today (Harrisonburg, Waynesboro, and Joshua's own extension 800 which carries the Lexington store number), rolling out to all 5 stores soon. Zoom emails a "New Voicemail" notification to the mailbox tied to each phone user, but nobody at the stores reliably checks that inbox, so calls go uncallbacked. There is no Zoom Phone MCP connector (checked the connector registry 2026-08-07 — only "Zoom for Claude" exists, which is meetings-only). The reliable path is the Zoom Admin console: Joshua's zoom.us login is the account Owner/Admin, so every phone user's call history — including Voicemail and Missed-call events — is visible centrally from Phone System Management → Users & Rooms → (click a user) → History tab. This task automates checking that admin view for all store lines and posts one consolidated Slack alert.

═══════════════════════════════════════════════
STEP 1 — Get the current list of store phone lines (do this fresh every run — more stores are being added soon)
═══════════════════════════════════════════════
Using the Claude in Chrome MCP (load via ToolSearch with query "select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__tabs_create_mcp" if not already loaded):

1. Create/get a tab (`tabs_context_mcp` with createIfEmpty true, then `tabs_create_mcp` if needed).
2. Navigate to `https://zoom.us/myhome`. Take a screenshot to confirm you're signed in (top-right avatar "JD" / account name Full Circle Finance Inc).
3. **If you land on a Zoom sign-in page (session expired):** do NOT attempt to log in or enter any password yourself — that's outside what this task should do automatically. Instead send one Slack DM to Joshua Davis (user ID `U03BB52MDSA`): "⚠️ Zoom admin session expired — please open zoom.us in Chrome and sign in once so the voicemail-alert check can keep running." Then stop this run (skip Steps 2–4 entirely).
4. Click the "Phone" item in the left sidebar (personal nav). Wait ~2s.
5. Scroll the left sidebar down until you see "Phone System Management" under an admin section; click it to expand, then click "Users & Rooms".
6. Use `get_page_text` on the Users table. Parse each row into: `email` (the user's login, e.g. harrisonburg@fcfpawn.com), `extension` (Ext. column, e.g. 802), `number` (Number(s) column, e.g. (540) 574-4500).
7. Map each row to a store name using the Number(s) column against the canonical store phone list in `valley-pawn-context` (Culpeper (540) 445-5510, Waynesboro (540) 221-6346, Harrisonburg (540) 574-4500, Lexington (540) 461-8349, Roanoke (540) 562-0776). Joshua's own row (jdavis@fcfpawn.com) maps to whichever store owns its Number(s) value (currently Lexington). If a row's number doesn't match any of the 5 known store numbers, still include it but label the store as "Unmapped — number (X)" in the Slack post so Joshua notices a new line was added that needs mapping.
8. This gives you the full current roster of active store lines — could be 3 today, more later. Process ALL of them every run.

═══════════════════════════════════════════════
STEP 2 — Pull each line's call history and find NEW voicemails/missed calls
═══════════════════════════════════════════════
For each store line from Step 1:

1. Click into that user's row (or navigate directly if you captured a detail URL pattern like `https://zoom.us/pbx/page/telephone/phoneUsers#/users/history/<userId>?extensionId=<userId>`).
2. Click the "History" tab.
3. Set the date range "From" and "To" to TODAY only (keeps each run fast; anything already alerted gets filtered by the state file in Step 3 anyway).
4. Use the "Voicemail" filter dropdown if present to narrow to rows with a voicemail, OR read the full unfiltered table for today and inspect the "Voicemail" and "Call Result"/"Event" columns per row — use whichever actually narrows the list in the UI at the time. You want every row where the call was missed and/or a voicemail was left.
5. Use `get_page_text` to extract each matching row: From (caller number/name), Start Time, Duration, Voicemail Y/N.

═══════════════════════════════════════════════
STEP 3 — Dedupe against state file (don't re-alert the same voicemail every 20 min)
═══════════════════════════════════════════════
State file: `/Users/joshuadavis/Documents/Claude/Scheduled/zoom-voicemail-alert/state.json` (in THIS task's own folder — read/write directly with Read/Write/Edit tools).

Structure: `{ "<store_name>": { "last_alerted_start_time": "<exact Start Time string Zoom shows>" } }`

If the file doesn't exist yet, treat every store as having no prior state (first run will alert on everything from today — expected on first run).

For each store, compare each row's Start Time against that store's `last_alerted_start_time`. Only NEW rows (strictly newer) are candidates to alert on. After building the alert, update the state file with the newest Start Time seen per store (write the file back) regardless of whether you posted to Slack.

═══════════════════════════════════════════════
STEP 4 — Post ONE consolidated Slack alert (only if there's something new)
═══════════════════════════════════════════════
If there are zero new missed-call/voicemail rows across all stores this run, do NOT post to Slack — stay silent. This runs every 20 minutes; a silent success is correct and expected most runs.

If there ARE new rows, send ONE Slack message to **#voicemails-missed-calls** (channel ID `C0BND1NK65V`) grouped by store:

```
📞 *Missed Call + Voicemail Alert*

*Harrisonburg*
• [caller name or number], [time] — [duration] voicemail. Please call back ASAP.

*Waynesboro*
• [caller name or number], [time] — [duration] voicemail. Please call back ASAP.

_Check the Zoom app (Phone → Voicemail) to listen and see the number. Pulled automatically from Zoom Phone admin history._
```

Only include stores that have new items — skip stores with nothing new. Keep it short and actionable.

═══════════════════════════════════════════════
ERROR HANDLING (Failure Alert Policy v2)
═══════════════════════════════════════════════
If Zoom's UI has changed and you can't find the History tab, the Voicemail filter, or parsing breaks entirely: do NOT guess or post a broken alert. Send ONE plain-language Slack DM to Joshua Davis (user ID `U03BB52MDSA`) — e.g. "⚠️ Zoom voicemail check couldn't read the call history page today — the Zoom admin UI may have changed, worth a look when you have a minute." Never send failure notices to #voicemails-missed-calls, #general, or any store channel. One attempt per run, then either succeed or send the single DM and stop.

═══════════════════════════════════════════════
NOTES
═══════════════════════════════════════════════
- Posts to the dedicated **#voicemails-missed-calls** channel (Joshua created this 2026-08-07 specifically for this task). Do not revert to #general.
- This is additive, net-new automation — doesn't touch any existing Bravo, Chekkit, or email infrastructure.
- As more stores get Zoom Phone lines (Culpeper, Roanoke coming soon), Step 1's fresh-roster-every-run design means this task picks them up automatically with no edit needed.