---
name: zoom-voicemail-eod-review
description: Daily 5:45 PM close-out — re-review every missed call/voicemail from today across all Zoom Phone store lines and post which ones still never got a callback, so nothing carries into tomorrow unresolved.
model: claude-haiku-4-5
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

For each store line's user detail page, click "History", set both From and To date fields to TODAY, and read the full table (page through if more than one page — note: Zoom's "Next page" button has been observed to silently disable early on some days, short of the true row count; if the displayed row total doesn't match what you've paginated through, spot-check via the search box for a few known caller numbers before trusting the page is complete). Capture Direction, From, To, Start Time, Event, Call Result, Voicemail, Duration for every row — Inbound AND Outbound. You need Outbound too, for the resolution check in Step 3.

## STEP 3 — Identify today's missed-call/voicemail candidates and check resolution

1. Candidates = Inbound rows where Call Result is not `Answered` (e.g. Busy, Ring Timeout, Abandoned) and/or Voicemail = Y.
2. For each candidate, normalize the caller's number to its last 10 digits and check BOTH:
   - **Staff callback:** a later Outbound row from the same store user, to the same 10-digit number, with Start Time after the missed call's Start Time, and Call Result = `Connected`. If found → resolved, exclude.
   - **Customer reconnected:** a later Inbound row FROM that same 10-digit number, Start Time after the missed call's Start Time, Call Result = `Answered`. If found → resolved, exclude.
3. Anything with neither → still needs a callback as of 5:45 PM today. This is a fresh full-day sweep — do NOT consult or write the `zoom-voicemail-alert` dedupe state file (`~/Documents/Claude/Projects/Valley Pawn OS/.zoom_voicemail_alert_state.json`); that file belongs to the other task only. This task is stateless — it always re-evaluates the whole day fresh.
4. Note the same honest limit as the intraday task if ever asked: this only sees activity on the Zoom-provisioned store line pulled — a callback from a personal cell or a different number is invisible to it.
5. Keep a running per-store tally as you go: `candidates` (total instances), `resolved` (count), `unresolved` = candidates − resolved. You'll need these totals for Step 5.

## STEP 4 — Post ONE end-of-day summary to Slack, always (unlike the intraday task, this one posts every run — it's the daily close-out record, not a noisy per-event alert)

Post to **#voicemails-calls-missed** (channel ID `C0BP4M3B99R` — renamed from #voicemails-missed-calls to #voicemails-calls-missed 2026-08-13, same channel ID. If posting returns an "is_archived" or invalid-channel error, run `slack_search_channels` for "voicemail" with `include_archived: true` to find the live channel, post there instead, then update THIS task's own prompt via `mcp__scheduled-tasks__update_scheduled_task` to replace the stale channel ID/name so the next run doesn't repeat the failure — same recovery pattern the intraday task uses).

Keep the message compact — one line per outstanding item, no extra header/footer clutter. Always include the caller's full phone number (the Zoom "From" column, e.g. (540) 555-1234) on the same line as the caller name, if a name is shown — never just a name alone — so nobody has to open the Zoom app to find the number.

If there ARE still-unresolved rows, post (each bullet exactly one line, nothing else in the message besides the title line):
```
🌙 End-of-Day Close-Out — {today's date} — still need a callback:
📞 Harrisonburg — (540) 578-3842, 9:34 AM — 🔴 VM left, no callback yet
📞 Waynesboro — (540) 000-0000, 4:10 PM — missed (no VM), no callback yet
```

If EVERYTHING from today was resolved (or there were no missed calls/voicemails today at all), post a short all-clear instead (one line):
```
🌙 End-of-Day Close-Out — {today's date} — all clear, nothing outstanding.
```

## STEP 5 — Log today's per-store counts to the trend report, then regenerate it (added 2026-08-13)

This step feeds Joshua's "Missed Calls & Voicemails" trend report. It runs after Step 4 regardless of whether today had any unresolved items — the report tracks every day, not just bad days.

Data store: `~/Documents/Claude/Projects/Communcations/Trend Reports/Missed Calls & Voicemails/daily_log.csv` — columns `date,store,candidates,resolved,unresolved,callback_pct` (one row per store per day; `callback_pct` = `resolved/candidates*100` rounded to 1 decimal, or `0` if candidates is 0).

1. For every store in today's live roster (from Step 1) — including ones with zero candidates today — write one row using today's date and the tallies from Step 3.5.
2. This task is stateless and may occasionally be re-run for the same day — before writing, drop any existing rows in the CSV where `date` equals today's date, then append the fresh rows. Never duplicate a day. Do this with a short Python script (`csv` module) via bash, not by hand-editing.
3. Regenerate the report by running (no arguments needed — it resolves both files relative to its own location):
   ```
   python3 "~/Documents/Claude/Projects/Communcations/Trend Reports/Missed Calls & Voicemails/generate_report.py"
   ```
   This rewrites `report.html` in the same folder from the CSV's full history (daily-by-store chart, monthly-by-store chart, running YTD cumulative total, callback % trend, and a data table).
4. If this step fails (CSV write error, script error, missing file), do not let it block or retry Step 4 — that Slack post already happened. Instead send one brief Slack DM to Joshua Davis (`U03BB52MDSA`), e.g. "⚠️ Today's voicemail trend log/report update failed — worth a look when you have a minute. The Slack close-out post above is unaffected." Do not post this to #voicemails-calls-missed.

## ERROR HANDLING (same Failure Alert Policy v2 as zoom-voicemail-alert)

If the Zoom UI has changed and you can't read the History tab or parsing breaks: do NOT guess or post a broken summary. Send ONE plain-language Slack DM to Joshua Davis (user ID `U03BB52MDSA`) — e.g. "⚠️ End-of-day Zoom voicemail review couldn't read the call history page today — worth a look when you have a minute." Never send failure notices to #voicemails-calls-missed, #general, or any store channel. One attempt, then either succeed or send the single DM and stop. (This applies to Steps 1–4; Step 5's own failure handling is separate, see above.)

## Notes

- This is additive, net-new automation alongside `zoom-voicemail-alert` — does not touch that task's logic, schedule, or state file.
- As more stores get Zoom Phone lines (Culpeper, Roanoke), Step 1's fresh-roster-every-run design picks them up automatically, and Step 5 will start writing rows for them too — no edit needed here.
- Close every Chrome tab you opened before finishing.
- 2026-08-13: matched `zoom-voicemail-alert`'s update — the callback phone number is now always published inline (never just a caller name), and the Slack post format was trimmed to one line per item with no header/footer clutter. Same day, Joshua renamed the destination Slack channel from #voicemails-missed-calls to #voicemails-calls-missed (channel ID unchanged, C0BP4M3B99R) — updated all references in this prompt to the new name.
- 2026-08-13 (later): added Step 5 — daily trend logging to `Communcations/Trend Reports/Missed Calls & Voicemails/daily_log.csv` and regeneration of `report.html` via `generate_report.py`. Backfilled with 2026-08-13's data (Harrisonburg 24/22 resolved, Waynesboro 3/2, Lexington 8/3) as the first tracked day. Pagination note added to Step 2 after that same first run hit a Zoom grid bug where "Next page" disabled itself 6 rows short of the true total — caught only by spot-checking via search.