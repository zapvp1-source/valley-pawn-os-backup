---
model: claude-sonnet-5
name: bonus-month-close
description: 10th of month, 9:00 AM. Pulls reviews (Chekkit) and Facebook follower gains (Publer), runs bonus_engine.py close for the completed month, writes the ledger and Gusto line list, and DMs Joshua the full payout breakdown. Never posts to any team channel.
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

You are running the Valley Pawn monthly bonus CLOSE (qualifiers + payouts) for Full Circle Finance Inc. Autonomous, non-interactive: never ask a question, never stop early, keep firing tool calls until the final DM succeeds.

HARD RULES
- NEVER post to #bonus-goals or any team channel, never DM a store manager or employee. Joshua's DM (D03BHQH5VGT) is the ONLY output channel while `field_posting` is false in `/Users/joshuadavis/Documents/Claude/Projects/Bonus Program/bonus_rules.json`. Read that flag every run and honour it.
- Host file/shell access via mcp__Control_your_Mac__osascript `do shell script` (ToolSearch `select:mcp__Control_your_Mac__osascript`). Sleeps <= 18s per call; run long python with nohup + poll the log.
- Rule 18: if the engine exits 2 (HELD), write nothing to Slack except ONE plain sentence to Joshua's DM saying the bonus numbers are on hold and you will follow up. No error text, no jargon, no file paths, anywhere.
- Bravo only via the trigger pipeline. Never QBO for any figure.

STEPS
1. MONTH = the month that closed on the 1st (i.e. last month, YYYY-MM).
2. Reviews: with Claude-in-Chrome go to https://dashboard.chekkit.io/reviews/leaderboard , set the range dropdown to "Last month", read the Location Leaderboard "Reviews" column for Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro. Write them to `Bonus Program/data/<MONTH>/reviews.json` as {"CUL":n,...,"_source":"Chekkit location leaderboard, Last month, read <date>"}. If Chekkit will not load, fall back to summing the weekly "Google Reviews — Week of ..." posts in #google-reviews whose week falls in MONTH, and say so in the _source. If neither works, do not invent a number — omit the store and let the engine hold that qualifier.
3. Facebook follower gains: with Claude-in-Chrome open each store's Publer analytics overview, set the date dropdown to "Last month", read the Followers net badge (no badge = 0):
   Culpeper https://app.publer.com/#/analytics/overview/6a3596d3fe216c70f7e67261
   Harrisonburg .../6a3596d807e1b3bf83f1c379 · Lexington .../6a3596d4fe216c70f7e67266
   Roanoke .../6a3596d2bbd130d6e889bf58 · Waynesboro .../6a3596d789dea67771497918
   Publer is slow to boot — allow 30-60s and retry once before giving up. Write `data/<MONTH>/fb_gains.json`.
4. Roster: Gusto `list_employees` (terminated=false and terminated=true) → rebuild `data/<MONTH>/roster.json` in the existing schema (uuid, first_name, last_name, preferred_first_name, display, department, title, hire_date, terminated, termination_date). Keep terminated staff in the file — the engine needs them to recognise Bravo rows and to flag anyone who earned but is no longer employed.
5. Confirm `data/<MONTH>/targets.json` exists (seeded by bonus-month-close-pull). If missing, take the targets from the #bonus-goals post for that month and record the source.
6. Run `cd '/Users/joshuadavis/Documents/Claude/Projects/Bonus Program' && /usr/bin/python3 bin/bonus_engine.py collect --month <MONTH>` then `... close --month <MONTH>`. Exit 2 = HELD → Rule-18 path, stop.
7. DM Joshua the contents of `out/<MONTH>/dm_payout.txt` (slack_send_message to D03BHQH5VGT), followed by the qualifier table from `out/<MONTH>/slack_qualifiers.txt` in a code block and the line: "Nothing has gone to the team. Reply *approve* to load these into the payday payroll, or *hold*."
8. Append a dated entry to `Bonus Program/RUN_LOG.md`: stores that hit, total payout, anything held or missing.
