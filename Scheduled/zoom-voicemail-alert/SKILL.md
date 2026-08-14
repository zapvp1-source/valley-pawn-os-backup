---
name: zoom-voicemail-alert
description: Every ~20 min during store hours — check Zoom Phone admin for new missed calls/voicemails on each store line and post an alert to Slack #voicemails-missed-calls so the team knows to call back.
model: claude-sonnet-5
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
4. Read the full unfiltered table for today (page size up to 50, page through if there are more rows) and capture EVERY row — both Inbound and Outbound — with Direction, From, To, Start Time, Event, Call Result, Voicemail, Duration. You need the Outbound rows too now, for the Step 3.5 callback check, not just the missed/voicemail ones.
5. From that full set, identify the candidate missed/voicemail rows: Inbound rows where Call Result is not `Answered` (e.g. Busy, Ring Timeout, Abandoned) and/or Voicemail = Y.

═══════════════════════════════════════════════
STEP 3 — Dedupe against state file (don't re-alert the same voicemail every 20 min)
═══════════════════════════════════════════════
State file: `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/.zoom_voicemail_alert_state.json`
(moved here 2026-08-10 — the original path under `~/Documents/Claude/Scheduled/zoom-voicemail-alert/` is a
protected host location that Cowork sessions mount READ-ONLY; a write there fails every run, silently
defeating the whole dedupe mechanism. `~/Documents/Claude/Projects/` is a normal read-write project folder.
Read/write directly with Read/Write/Edit tools.)

Structure: `{ "<store_name>": { "last_alerted_start_time": "<exact Start Time string Zoom shows>" } }`

If the file doesn't exist yet, treat every store as having no prior state (first run will alert on everything from today — expected on first run).

For each store, compare each candidate row's Start Time against that store's `last_alerted_start_time`. Only NEW rows (strictly newer) proceed to Step 3.5. After building the alert, update the state file with the newest Start Time seen per store among today's candidate rows (write the file back) regardless of whether you posted to Slack. If the Write tool ever reports the state file path as read-only, STOP and send Joshua the Slack DM described in ERROR HANDLING below instead of silently continuing — do not let dedupe fail silently again.

═══════════════════════════════════════════════
STEP 3.5 — Check whether each missed/voicemail row was already resolved
═══════════════════════════════════════════════
Before adding a candidate row (that survived Step 3) to the alert, check whether it's already been resolved — either the store called back, OR the customer reconnected on their own — using the rows you already captured in Step 2 (both Outbound AND Inbound):

1. Normalize the caller's number to its last 10 digits (strip formatting/country code).
2. **Staff callback check:** Look for an Outbound row from the same store user, To the same 10-digit number, with a Start Time AFTER the missed call's Start Time. If a matching later Outbound row exists AND its Call Result is `Connected` (not Busy/Failed/Unanswered): treat this row as **callback-confirmed** — do NOT include it in the alert.
3. **Customer-reconnected check (added 2026-08-10):** If no staff callback is found, also look for a later Inbound row FROM that same 10-digit number, with a Start Time AFTER the missed call's Start Time, with Call Result = `Answered`. This means the customer tried again themselves and got through — the interaction is resolved even though nobody at the store placed an outbound call. Treat this as **resolved-by-retry** — do NOT include it in the alert. (Caught live 2026-08-10: Harrisonburg missed Mirand Campbell at 4:45:01 PM (Ring Timeout), she called back herself at 4:45:37 PM and was Answered for 7:03 — no outbound row existed at all, so the outbound-only check would have kept flagging her as needing a callback indefinitely.)
4. If neither check finds a resolution, include the row in the alert as still needing a callback.
5. This check only fires on brand-new candidate rows from Step 3 — don't re-scan rows that were already alerted on in a prior run (the state file already excludes those).
6. Note the limits of this check honestly if asked: it only sees activity on the Zoom-provisioned store line captured in this pull. A callback placed from a personal cell, a different line, or to a different number than the one that called in will not be detected by either check.

Example that motivated the original outbound check (2026-08-10): Waynesboro missed an inbound call from Daniel Liptrap ((540) 480-0805) at 10:38:42 AM (Busy), but the store called him back twice within the same minute (10:38:52 AM and 10:39:06 AM, the second one Connected 1:15) — before this step existed, the alert flagged it as needing a callback that had already happened.

═══════════════════════════════════════════════
STEP 4 — Post ONE consolidated Slack alert (only if there's something new)
═══════════════════════════════════════════════
If there are zero rows surviving Step 3.5 across all stores this run, do NOT post to Slack — stay silent. This runs every 20 minutes; a silent success is correct and expected most runs.

If there ARE surviving rows, send ONE Slack message to **#voicemails-calls-missed** (channel ID `C0BP4M3B99R` — renamed from #voicemails-missed-calls to #voicemails-calls-missed 2026-08-13, same channel ID, see NOTES). Keep the ENTIRE message compact — no header line, no footer/disclaimer line, no blank lines between items, no per-store heading of its own line. Every item is exactly ONE line: `store — number, time — status, call back ASAP`. If there's only one item, the whole Slack message is that one line. If there are multiple items, stack them as consecutive one-line bullets with no other text before/after/between them. Always include the caller's full phone number (the Zoom "From" column, e.g. (540) 555-1234) on that same line — even if a caller-ID name is also shown — so whoever reads it can call back with zero extra steps, never needing to open the Zoom app to find the number. Distinguish an actual left voicemail (Voicemail column = Y) from a plain missed call (Busy/Ring Timeout/Abandoned, no voicemail) — don't call every row a "voicemail" when nobody left one.

Format (each bullet is one line, nothing else in the message):
```
📞 Harrisonburg — (540) 578-3842, 9:34 AM — missed (no VM), call back ASAP
📞 Lexington — (540) 924-3080, 9:23 AM — 🔴 VM left, call back ASAP
```

Only include items that survived Step 3.5 — skip stores with nothing new.

═══════════════════════════════════════════════
ERROR HANDLING (Failure Alert Policy v2)
═══════════════════════════════════════════════
If Zoom's UI has changed and you can't find the History tab, the Voicemail filter, or parsing breaks entirely: do NOT guess or post a broken alert. Send ONE plain-language Slack DM to Joshua Davis (user ID `U03BB52MDSA`) — e.g. "⚠️ Zoom voicemail check couldn't read the call history page today — the Zoom admin UI may have changed, worth a look when you have a minute." Never send failure notices to #voicemails-calls-missed, #general, or any store channel. One attempt per run, then either succeed or send the single DM and stop.

If posting to the #voicemails-calls-missed channel ID on file fails with an "is_archived" (or similar "channel no longer valid") error: before falling back to a DM, run one `slack_search_channels` lookup for "voicemail" (include_archived: true) to check whether Joshua recreated the channel under a new ID (this has happened before — see NOTES). If a non-archived channel matching "voicemail" is found, post there and note the new channel ID needs to be saved (see below). Only send the Joshua DM fallback if no live matching channel exists.

**Whenever you discover the channel ID on file is stale** (archived, deleted, or renamed to a genuinely different channel) and you had to look up the live one: after posting successfully, update this task's own prompt via `mcp__scheduled-tasks__update_scheduled_task` to replace the old channel ID/name with the new one, so the next run doesn't hit the same failure. Do this yourself — don't just work around it silently, fix the source.

═══════════════════════════════════════════════
NOTES
═══════════════════════════════════════════════
- Posts to the dedicated **#voicemails-calls-missed** channel (channel ID `C0BP4M3B99R`; Joshua created this channel 2026-08-07 specifically for this task, renamed it from #voicemails-missed-calls to #voicemails-calls-missed on 2026-08-13 — same ID, no functional change). Do not revert to #general.
- 2026-08-10 (evening): the original channel (ID `C0BND1NK65V`) was archived and renamed `#voicemails-missed-calls-archived`; Joshua recreated `#voicemails-missed-calls` fresh the same day under a new ID, `C0BP4M3B99R` (later renamed again to `#voicemails-calls-missed` 2026-08-13, same ID). A run discovered this when the old ID returned an `is_archived` error, looked up the live channel via `slack_search_channels`, posted there, and updated this task's channel ID to the new one. If this ever happens again, follow the same recovery path in ERROR HANDLING above rather than guessing or giving up silently.
- This is additive, net-new automation — doesn't touch any existing Bravo, Chekkit, or email infrastructure.
- As more stores get Zoom Phone lines (Culpeper, Roanoke coming soon), Step 1's fresh-roster-every-run design means this task picks them up automatically with no edit needed.
- 2026-08-10: dedupe state file moved from `~/Documents/Claude/Scheduled/zoom-voicemail-alert/state.json` (read-only in Cowork sessions, was silently failing every run since the task was enabled 2026-08-08) to `~/Documents/Claude/Projects/Valley Pawn OS/.zoom_voicemail_alert_state.json` (writable). Added Step 3.5 callback verification using the Outbound rows already pulled in Step 2.
- 2026-08-10 (later): Step 3.5 extended with a "customer-reconnected" check. Joshua asked whether we could be "100% positive" a store hadn't called someone back; investigating turned up that the original Step 3.5 only checked Outbound rows, so a customer who called back in on their own and got Answered was still being flagged as needing a callback (live example: Mirand Campbell at Harrisonburg). The check now also treats a later Inbound-Answered row from the same number as resolved. Documented the honest limit of this check too: it can only see activity on the Zoom-provisioned store line pulled that run — a callback from a personal cell or a different number is invisible to it.
- 2026-08-13: Joshua asked (1) that the callback number always be published in the alert itself so the team has zero extra steps (previously the template said "check the Zoom app... to see the number"), and (2) that the alert be concise, one line per item with no header/footer/blank-line clutter. Step 4 template rewritten to a bare one-line-per-item format with the phone number always inline. Same day, Joshua renamed the Slack channel from #voicemails-missed-calls to #voicemails-calls-missed (channel ID unchanged, C0BP4M3B99R) — updated all references in this prompt to the new name.