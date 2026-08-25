---
name: daily-unopened-email-eval
description: Daily 6:00 PM EOD sweep of all 5 Valley Pawn store email inboxes (Apple Mail) — counts today's arrivals vs. still-unopened, appends to the Missed & Unopened Emails trend log, refreshes the HTML report, posts summary to #emails-missed. Companion to zoom-voicemail-eod-review.
model: claude-sonnet-5
---

Domain: 1 — Valley Pawn. Load the `enterprise-map` skill context first per standing instruction (light touch is fine — this is a narrow, well-understood mechanical task, same class as `store-mail-archive-sweep` and `zoom-voicemail-eod-review`, both of which you should be aware of).

PURPOSE: Daily eval of what emails have been left unopened or missed across Valley Pawn's 5 store inboxes — the email-channel equivalent of the `zoom-voicemail-eod-review` missed-calls sweep, feeding a companion trend report.

DO NOT ask Joshua anything. Execute directly, end to end, every run.

STEPS:

1. For each of these 5 accounts, in this exact order — culpeper@fcfpawn.com, waynesboro@fcfpawn.com, lexington@fcfpawn.com, harrisonburg@fcfpawn.com, roanoke@fcfpawn.com — run a SEPARATE `mcp__Control_your_Mac__osascript` call (one account per call, never combined — combining has caused timeouts on sibling tasks). If Mail.app is not running, launch it first (`open_application` or an osascript `tell application "Mail" to activate`), then proceed.

2. Per-account AppleScript (adjust the account name each time) — this is the proven-safe reference-based technique from `store-mail-archive-sweep`, it never materializes the full message list so it works on the large inboxes (harrisonburg, roanoke) as well as the small ones:

```applescript
tell application "Mail"
	set acct to account "culpeper@fcfpawn.com"
	set inboxMbox to mailbox "INBOX" of acct
	set today0 to (current date)
	set time of today0 to 0
	set totalToday to 0
	set unreadToday to 0
	set i to 1
	repeat 400 times
		try
			set m to message i of inboxMbox
			set dr to date received of m
			if dr < today0 then exit repeat
			set totalToday to totalToday + 1
			if read status of m is false then set unreadToday to unreadToday + 1
			set i to i + 1
		on error
			exit repeat
		end try
	end repeat
	return (totalToday as string) & "," & (unreadToday as string)
end tell
```

This returns "received_today,unread_today" — messages are listed newest-first by default, so the loop naturally stops once it reaches yesterday's mail. If a call errors or times out for an account, treat that account as unreadable for today (log 0,0 and note it — do not fail the whole run), move to the next account, and do not retry more than once.

3. For each account, compute this day's row:
   - `candidates` = received_today
   - `resolved` = received_today - unread_today (i.e. how many of today's arrivals are already read/opened)
   - `unresolved` = unread_today
   - `opened_pct` = round(resolved / candidates * 100, 1) if candidates > 0 else 0.0

4. Map account → store display name: culpeper→Culpeper, waynesboro→Waynesboro, lexington→Lexington, harrisonburg→Harrisonburg, roanoke→Roanoke.

5. Append one CSV row per store to `Communcations/Trend Reports/Missed & Unopened Emails/daily_log.csv` (columns: date,store,candidates,resolved,unresolved,opened_pct — date in YYYY-MM-DD, today's local date). If a row for today+that store already exists (e.g. this task was run twice today, or a manual test run already seeded it), REPLACE that row rather than duplicating it — read the file, drop any existing row matching (today's date, that store), then append the fresh one. This file lives in the user's connected Projects folder — use the Read/Write/Edit tools (not the bash sandbox) so the write lands on the host, matching how the sibling Missed Calls report is maintained.

6. Re-run the generator to refresh the HTML report: `python3 "Communcations/Trend Reports/Missed & Unopened Emails/generate_report.py"` (resolve the actual host path the same way you resolved the CSV path — the script takes no arguments and rewrites report.html in its own folder from the current CSV).

7. Post ONE plain-language summary to the Slack channel **#emails-missed** (channel ID `C0BNN60347M`) — use the Slack MCP `slack_send_message` tool with that channel_id. This mirrors how `zoom-voicemail-eod-review` posts to `#voicemails-calls-missed` for the calls side. Summarize: total emails received across all 5 stores, total still unopened at day's end, and call out any single store where unopened count is high (say, 3+) or opened_pct is notably low relative to the others — that's the actionable signal, same spirit as flagging a store over the missed-calls callback threshold. Keep it short — a few lines, not a wall of text. Post every run (do not go silent by default) until this task has proven itself stable for at least a couple of weeks — after that it's fine to switch to posting only on a notable finding, matching the maturity model of older sibling tasks, but do not make that change unilaterally; just keep posting daily until Joshua says otherwise.

8. Do not touch the existing `zoom-voicemail-eod-review`, `store-mail-archive-sweep`, or any other existing task/file — this is purely additive (Rule #4). Do not modify Mail Rules, do not move or delete any messages — this task is READ-ONLY against the mailboxes (unlike `store-mail-archive-sweep`, which moves mail — this task must never move, delete, or mark messages as read/unread).

9. On the FIRST run only (i.e. `daily_log.csv` has no data rows yet, only the header): after writing today's row, also add a one-line entry to `Life OS/OPEN_ITEMS_REGISTER.md` under the OPEN table noting the task fired successfully for the first time with today's numbers, domain 1, and that it posts to #emails-missed (C0BNN60347M). On every subsequent run, no register update is needed unless something structurally changed (per standard Valley Pawn rules) — the run's own CSV row and Slack post are sufficient history.

10. If any of the 5 osascript calls fails outright (not just times out — actually errors), still complete the run for the other 4 accounts, still write their rows, still regenerate the report, still post to #emails-missed (noting which store(s) couldn't be read today). Never let one account's failure abort the whole run.

11. If the #emails-missed channel post ever fails (e.g. channel archived, ID changed, bot not a member), fall back to a Slack DM to Joshua (user id D03BHQH5VGT) with the same content, and note the channel-post failure in that DM so it gets noticed and fixed.

Do not ask Joshua any questions. Do not wait for confirmation.