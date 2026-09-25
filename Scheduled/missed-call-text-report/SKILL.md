---
name: missed-call-text-report
description: Slack DM to Joshua: how many missed callers were texted, how many replied, how fast the store answered, and outcomes — daily through Thu 10/1/2026, then Mondays weekly.
model: claude-sonnet-5
---

You are reporting results of Valley Pawn's missed-call → text system to Joshua Davis (CEO). Load the enterprise-map and vp-operating-rules skills first and follow them (no technical jargon to Slack, never post incomplete or inaccurate data, source of record first).

WHAT THE SYSTEM IS: a native agent (com.valleypawn.missed-call-text, live since 2026-09-24 11:54 ET) that texts a caller from the store's own number ~2 minutes after an unanswered call. Every text sent writes one line to ~/Documents/Claude/Projects/Valley Pawn OS/fleet/receipts/missed-call-text.jsonl, e.g. {"ts":"2026-09-24T12:05:01-04:00","target":"chekkit-webhook:WAY","ok":true}. Store codes: CUL Culpeper, HAR Harrisonburg, LEX Lexington, ROA Roanoke, WAY Waynesboro.

CADENCE (decide first, using today's date in America/New_York):
- Fri 2026-09-25 through Thu 2026-10-01: DAILY report covering YESTERDAY (00:00-23:59 ET).
- From Fri 2026-10-02 onward: run ONLY on Mondays, covering the prior Monday-Sunday. On any other day, do nothing and end.
- If a previous daily run was missed (check the ledger file below), include the missed day(s) as well.

STEPS
1. Read the receipts file and count texts sent in the period, by store, with times. ok:false lines = failed sends (count separately).
2. Check the source of record for replies: Chekkit (https://dashboard.chekkit.io, Joshua is signed in) in Chrome via the claude-in-chrome tools. For each store that sent texts, switch location with the top-left location dropdown (screenshot before clicking an option; the list toggles), then look in BOTH the Open and Closed conversation lists for conversations containing a message tagged "Missed call - text from detector" in the period. Open each one and record: did the customer reply (yes/no), minutes from our text to their first reply, minutes from their first reply to the store's first human reply (and which employee), and a few-word outcome (e.g. "selling golf cart - passed on price", "Nintendo DS - coming in", "asked hours"). A STOP reply counts as an opt-out. Match each conversation to a receipt by store + timestamp (within ~1 minute).
3. If Chekkit cannot be read or conversations cannot be matched for every text, DO NOT post partial numbers. Append one plain line to ~/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md describing what failed, and end; the next run will catch up the missed period.
4. Keep a running tally in ~/Documents/Claude/Projects/Valley Pawn OS/fleet/missed_call_text_results.csv (create with header if missing: date,store,text_time,replied,reply_min,store_reply_min,employee,outcome,opt_out). Append one row per text; never duplicate a row already there (match date+store+text_time).
5. DM Joshua on Slack (user ID U03BB52MDSA) using the Slack connector's send_message. Plain English, short, mobile-readable, no file paths or tool names:
   - Headline: "Missed-call texts — <day or week>: X texted, Y replied (Z%)."
   - One line per store: texted / replied / typical store response time.
   - Up to 5 notable conversations (store, what they wanted, outcome).
   - Flag any store reply that took over 15 minutes (the text promises "usually within a few minutes"), with the store and employee.
   - Any opt-outs (STOP) and any failed sends.
   - Weekly reports also show the running totals since 9/24 from the CSV and the week-over-week change.
   - If zero texts were sent in the period, say so in one line and note it is expected on days stores are closed (Wednesday most stores closed; Sunday all closed).
This DM to Joshua is pre-approved by him ("send me updates daily for the next week and then weekly"). Send only to Joshua — never to a channel or anyone else.

On the last daily run (Thu 2026-10-01) add one line at the end: "Switching to weekly Monday updates from here."