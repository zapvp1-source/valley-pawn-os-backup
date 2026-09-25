---
name: zoom-voicemail-alert
description: Every ~20 min during store hours — check Zoom Phone admin for new missed calls/voicemails on each store line and post an alert to Slack #voicemails-missed-calls so the team knows to call back.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN>` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

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
This is an automated run of a scheduled task. The user is not present to answer questions. For implementation details, execute autonomously without asking clarifying questions — make reasonable choices and note them in your output. "write" actions (e.g. MCP tools that send, post, create, update, or delete), only take them if the task file asks for that specific action. When in doubt, producing a report of what you found is the correct output.

You are checking Valley Pawn's Zoom Phone system for new missed calls / voicemails on each store's line, and alerting the team in Slack so nobody misses a customer callback. This mirrors the existing Chekkit "missed customer message" pattern but for Zoom Phone voicemails.

Read the `valley-pawn-context` skill if you need store names/numbers/hours for reference. Do the work yourself; don't ask permission to proceed.

═══════════════════════════════════════════════
BACKGROUND — why this exists (built 2026-08-07)
═══════════════════════════════════════════════
Valley Pawn has Zoom Phone lines at stores today, all 5 stores now provisioned (Culpeper and Roanoke added since 2026-08-14 — see 2026-09-24 UPDATE below). Zoom emails a "New Voicemail" notification to the mailbox tied to each phone user, but nobody at the stores reliably checks that inbox, so calls go uncallbacked. There is no Zoom Phone MCP connector (checked the connector registry 2026-08-07 — only "Zoom for Claude" exists, which is meetings-only). The reliable path is the Zoom Admin console (Joshua's zoom.us login is the account Owner/Admin).

**2026-08-14 UPDATE — jdavis@fcfpawn.com (ext 800) is DISCONTINUED.** Joshua confirmed he discontinued the jdavis@fcfpawn.com extension (ext 800), which previously carried the Lexington store number/queue membership. It may still show as "Active"/"Activated" in the roster (verify fresh each run per Rule #12) — treat **lexington@fcfpawn.com (ext 807) as the primary/canonical Lexington line**. If a future run finds jdavis@fcfpawn.com no longer appears in the roster at all, that confirms full deactivation.

**2026-09-24 UPDATE — ARCHITECTURE CHANGED TO CALL QUEUES; Steps 1–2 below are REWRITTEN. Read this before using the old per-User History approach.**
Starting 2026-08-13 (Harrisonburg first, "built... to replace single-user ring for better burst-call handling," per that Call Queue's own description), Joshua moved store lines off direct-to-user ringing and onto **Zoom Call Queues** (Phone System Management → Call Queues). All 5 stores now have a dedicated "<Store> Store Queue" (Culpeper ext 810, Harrisonburg ext 805, Lexington ext 804, Roanoke ext 812, Waynesboro ext 806) and the store's public number is assigned to the **Queue**, not to the individual `<store>@fcfpawn.com` User anymore. Consequence discovered this run: each User's own History tab (the old Step 2 data source) now returns "No Data" every day, because calls terminate at the Queue, not at the User extension. A run that only checked User History would find nothing and silently stop alerting — this is exactly what happened: the dedupe state file's `last_alerted_start_time` for every store was stuck at 2026-09-22 despite real unanswered calls landing on 2026-09-24 (3 missed calls to Culpeper, all "Overflowed," none called back — caught and alerted by this run using the corrected method below). **Do not revert to the old per-User Step 1/2 method — use the company-wide Calls log instead, per the rewritten steps below.**

Also as of 2026-09-24: Culpeper's number (540) 445-5510 completed its port from Comcast Business and is live on Culpeper Store Queue (ext 810) — Culpeper is now taking real calls. Roanoke Store Queue (ext 812) exists but has no number assigned yet (still "--" in Number(s)) — no calls possible there until a number is ported/assigned; skip it in Step 3.5/4 output if it never appears in the Calls log, no need to flag as an error.

═══════════════════════════════════════════════
STEP 1 — Get the current list of store phone lines (do this fresh every run — more stores may be added)
═══════════════════════════════════════════════
Using the Claude in Chrome MCP (load via ToolSearch with query "select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__tabs_create_mcp" if not already loaded):

1. Create/get a tab (`tabs_context_mcp` with createIfEmpty true, then `tabs_create_mcp` if needed).
2. Navigate to `https://zoom.us/myhome`. Take a screenshot to confirm you're signed in (top-right avatar "JD" / account name Full Circle Finance Inc).
3. **If you land on a Zoom sign-in page (session expired):** do NOT attempt to log in or enter any password yourself. Instead append a FAILURE_LEDGER row per the policy banner at the top of this file (NEEDS_HUMAN: yes — sign in to zoom.us in Chrome once) and stop this run (skip Steps 2–4 entirely).
4. Navigate directly to `https://zoom.us/pbx/page/telephone/groups` (Call Queues list — this is now the canonical roster, NOT Users & Rooms). Wait ~2s for the SPA to render.
5. Use `get_page_text` to read the Call Queues table: Name (e.g. "Culpeper Store Queue"), Ext., Number(s) (may be blank "--" if a port hasn't completed yet — that's expected, not an error), Status.
6. Map each queue to a store name by the name itself (it's literally "<Store> Store Queue") — no separate lookup needed. Cross-check the Number(s) against the canonical store phone list in `valley-pawn-context` (Culpeper (540) 445-5510, Waynesboro (540) 221-6346, Harrisonburg (540) 574-4500, Lexington (540) 461-8349, Roanoke (540) 562-0776) only as a sanity check — if a queue's number doesn't match, still include it but label the store as "Unmapped — number (X)" in the Slack post.
7. This gives you the full current roster of store queues — process ALL of them every run, including any with no number yet (they just won't produce rows in Step 2).
8. Also still worth a quick fresh check on `https://zoom.us/pbx/page/telephone/phoneUsers` for the legacy jdavis@fcfpawn.com (ext 800) row — note in your output whether it's still present/Active or has finally been removed, but don't treat its own History tab as a data source anymore (see 2026-09-24 UPDATE above).

═══════════════════════════════════════════════
STEP 2 — Pull TODAY's calls for all store lines in ONE pass (company-wide Calls log)
═══════════════════════════════════════════════
Use the company-wide call log instead of any single queue/user's own tab — it covers every store number, including Overflowed/Missed events on the queues, in one screen:

1. Navigate directly to `https://zoom.us/pbx/page/telephone/callLog#/call-log-new?page_size=50&page_number=1&from=YYYY-MM-DD&to=YYYY-MM-DD&pt=&aiSummary=` with both `from` and `to` set to TODAY's date (edit the URL directly rather than the date picker widget). Wait ~2s for the SPA to reload.
2. Use `get_page_text` to read the full table (page through with `page_number` if "result(s)" exceeds the page size). Capture every row — both Inbound and Outbound, across ALL stores — with Direction, From (number + CNAM name if shown), To (store queue name + number + Ext), Start Time, Event, Call Result, Voicemail, Duration.
3. From that full set, identify candidate missed/voicemail rows: Inbound rows whose "To" is one of the store queues from Step 1, where Call Result is not `Answered`/`Connected` (e.g. `Overflowed`, `Busy`, `Ring Timeout`, `Abandoned`) and/or Voicemail = Y.
4. Keep the Outbound rows too — needed for the Step 3.5 callback check.
5. If a queue's own Voicemail tab (Call Queues → `<queue>` → Voicemail) shows a voicemail whose caller/time isn't already captured in the Calls log pull above, add it as a candidate too (belt-and-suspenders — the Calls log Voicemail column should normally already flag it, but confirm if anything looks off).

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

For each store, compare each candidate row's Start Time against that store's `last_alerted_start_time`. Only NEW rows (strictly newer) proceed to Step 3.5. After building the alert, update the state file with the newest Start Time seen per store among today's candidate rows (write the file back) regardless of whether you posted to Slack. If the Write tool ever reports the state file path as read-only, append a FAILURE_LEDGER row per the policy banner instead of silently continuing — do not let dedupe fail silently again.

═══════════════════════════════════════════════
STEP 3.5 — Check whether each missed/voicemail row was already resolved
═══════════════════════════════════════════════
Before adding a candidate row (that survived Step 3) to the alert, check whether it's already been resolved — either the store called back, OR the customer reconnected on their own — using the rows you already captured in Step 2 (both Outbound AND Inbound):

1. Normalize the caller's number to its last 10 digits (strip formatting/country code).
2. **Staff callback check:** Look for an Outbound row from the same store, To the same 10-digit number, with a Start Time AFTER the missed call's Start Time. If a matching later Outbound row exists AND its Call Result is `Connected` (not Busy/Failed/Unanswered): treat this row as **callback-confirmed** — do NOT include it in the alert.
3. **Customer-reconnected check (added 2026-08-10):** If no staff callback is found, also look for a later Inbound row FROM that same 10-digit number, with a Start Time AFTER the missed call's Start Time, with Call Result = `Answered`. This means the customer tried again themselves and got through — the interaction is resolved even though nobody at the store placed an outbound call. Treat this as **resolved-by-retry** — do NOT include it in the alert. (Caught live 2026-08-10: Harrisonburg missed Mirand Campbell at 4:45:01 PM (Ring Timeout), she called back herself at 4:45:37 PM and was Answered for 7:03 — no outbound row existed at all, so the outbound-only check would have kept flagging her as needing a callback indefinitely.)
4. If neither check finds a resolution, include the row in the alert as still needing a callback.
5. This check only fires on brand-new candidate rows from Step 3 — don't re-scan rows that were already alerted on in a prior run (the state file already excludes those).
6. Note the limits of this check honestly if asked: it only sees activity on the Zoom-provisioned store line captured in this pull. A callback placed from a personal cell, a different line, or to a different number than the one that called in will not be detected by either check.

Example that motivated the original outbound check (2026-08-10): Waynesboro missed an inbound call from Daniel Liptrap ((540) 480-0805) at 10:38:42 AM (Busy), but the store called him back twice within the same minute (10:38:52 AM and 10:39:06 AM, the second one Connected 1:15) — before this step existed, the alert flagged it as needing a callback that had already happened.

═══════════════════════════════════════════════
STEP 4 — Post ONE consolidated Slack alert (only if there's something new)
═══════════════════════════════════════════════
If there are zero rows surviving Step 3.5 across all stores this run, do NOT post to Slack — stay silent. This runs every 20 minutes (09:00 AM–07:59 PM, Mon–Sat), so a silent success is correct and expected most runs.

If there ARE surviving rows, send ONE Slack message to **#voicemails-calls-missed** (channel ID `C0BP4M3B99R` — renamed from #voicemails-missed-calls to #voicemails-calls-missed 2026-08-13, same channel ID, see NOTES). Keep the ENTIRE message compact — no header line, no footer/disclaimer line, no blank lines between items, no per-store heading of its own line. Every item is exactly ONE line: `store — number, time — status, call back ASAP`. If there's only one item, the whole Slack message is that one line. If there are multiple items, stack them as consecutive one-line bullets with no other text before/after/between them. Always include the caller's full phone number (the Zoom "From" column, e.g. (540) 555-1234) on that same line — even if a caller-ID name is also shown — so whoever reads it can call back with zero extra steps, never needing to open the Zoom app to find the number. Distinguish an actual left voicemail (Voicemail column = Y) from a plain missed call (Overflowed/Busy/Ring Timeout/Abandoned, no voicemail) — don't call every row a "voicemail" when nobody left one.

Format (each bullet is one line, nothing else in the message):
```
📞 Harrisonburg — (540) 578-3842, 9:34 AM — missed (no VM), call back ASAP
📞 Lexington — (540) 924-3080, 9:23 AM — 🔴 VM left, call back ASAP
```

Only include items that survived Step 3.5 — skip stores with nothing new.

═══════════════════════════════════════════════
ERROR HANDLING (Failure Alert Policy v2, overridden by v3 banner at top — write the ledger row, don't DM)
═══════════════════════════════════════════════
If Zoom's UI has changed and you can't find the Calls log, Call Queues list, or parsing breaks entirely: do NOT guess or post a broken alert. Append a FAILURE_LEDGER row per the policy banner at the top of this file. Never send failure notices to #voicemails-calls-missed, #general, or any store channel. One attempt per run, then either succeed or log the ledger row and stop.

If posting to the #voicemails-calls-missed channel ID on file fails with an "is_archived" (or similar "channel no longer valid") error: before falling back to the ledger, run one `slack_search_channels` lookup for "voicemail" (include_archived: true) to check whether Joshua recreated the channel under a new ID (this has happened before — see NOTES). If a non-archived channel matching "voicemail" is found, post there and note the new channel ID needs to be saved (see below). Only log the ledger fallback if no live matching channel exists.

**Whenever you discover the channel ID on file is stale** (archived, deleted, or renamed to a genuinely different channel) and you had to look up the live one: after posting successfully, update this task's own prompt via `mcp__scheduled-tasks__update_scheduled_task` to replace the old channel ID/name with the new one, so the next run doesn't hit the same failure. Do this yourself — don't just work around it silently, fix the source.

═══════════════════════════════════════════════
NOTES
═══════════════════════════════════════════════
- Posts to the dedicated **#voicemails-calls-missed** channel (channel ID `C0BP4M3B99R`; Joshua created this channel 2026-08-07 specifically for this task, renamed it from #voicemails-missed-calls to #voicemails-calls-missed on 2026-08-13 — same ID, no functional change). Do not revert to #general.
- 2026-08-10 (evening): the original channel (ID `C0BND1NK65V`) was archived and renamed `#voicemails-missed-calls-archived`; Joshua recreated `#voicemails-missed-calls` fresh the same day under a new ID, `C0BP4M3B99R` (later renamed again to `#voicemails-calls-missed` 2026-08-13, same ID). A run discovered this when the old ID returned an `is_archived` error, looked up the live channel via `slack_search_channels`, posted there, and updated this task's channel ID to the new one. If this ever happens again, follow the same recovery path in ERROR HANDLING above rather than guessing or giving up silently.
- This is additive, net-new automation — doesn't touch any existing Bravo, Chekkit, or email infrastructure.
- 2026-08-10: dedupe state file moved from `~/Documents/Claude/Scheduled/zoom-voicemail-alert/state.json` (read-only in Cowork sessions, was silently failing every run since the task was enabled 2026-08-08) to `~/Documents/Claude/Projects/Valley Pawn OS/.zoom_voicemail_alert_state.json` (writable). Added Step 3.5 callback verification using the Outbound rows already pulled in Step 2.
- 2026-08-10 (later): Step 3.5 extended with a "customer-reconnected" check. Joshua asked whether we could be "100% positive" a store hadn't called someone back; investigating turned up that the original Step 3.5 only checked Outbound rows, so a customer who called back in on their own and got Answered was still being flagged as needing a callback (live example: Mirand Campbell at Harrisonburg). The check now also treats a later Inbound-Answered row from the same number as resolved.
- 2026-08-13: Joshua asked (1) that the callback number always be published in the alert itself so the team has zero extra steps, and (2) that the alert be concise, one line per item with no header/footer/blank-line clutter. Step 4 template rewritten accordingly. Same day, Joshua renamed the Slack channel from #voicemails-missed-calls to #voicemails-calls-missed (channel ID unchanged, C0BP4M3B99R).
- 2026-08-14: jdavis@fcfpawn.com (ext 800) confirmed discontinued as the Lexington line; lexington@fcfpawn.com (ext 807) is canonical.
- **2026-09-24: Discovered and fixed a live gap — Joshua's move to Call Queue-based routing (started 2026-08-13 with Harrisonburg) had silently broken this task's detection since the old Step 1/2 checked per-User History, which stopped receiving data once calls started terminating at the Queue instead of the User. The dedupe state file showed every store stuck at 2026-09-22 despite 3 real unanswered Culpeper calls on 2026-09-24 (all Overflowed, no callback). Rewrote Steps 1–2 to read the Call Queues roster and the company-wide Calls log (`.../callLog#/call-log-new`) instead of per-User pages — this is now the canonical method, don't revert to Users & Rooms History. Also noted: Culpeper's number ported live this week; Roanoke Store Queue exists but has no number yet.**