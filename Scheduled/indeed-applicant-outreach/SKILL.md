---
name: indeed-applicant-outreach
description: Hourly 9AM-7PM ET: contact new Valley Pawn Indeed applicants across all 5 listings (email + text), monitor replies on all 3 channels, book confirmed phone interviews to Joshua's Google Calendar, and post an activity-only digest to Slack #employee-prospects. Hard 9AM-8PM ET send window.
model: claude-sonnet-5
---

Valley Pawn Indeed hiring loop. FIRST read /Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/HIRING_OUTREACH.md (operating manual, contact log, listing table, THE FULL LOOP, clock procedure, known blockers; mount ~/Documents/Claude/Projects via request_cowork_directory if needed). That file is authoritative over this prompt. THE GOAL IS A BOOKED PHONE INTERVIEW, not a sent message. Default format is PHONE unless the candidate asks otherwise.

*** STEP 0 — ESTABLISH THE TRUE TIME. DO NOT TRUST THE LOCAL CLOCK. ***
On 2026-09-03 the Linux sandbox AND the Mac both reported 2026-08-15 23:05 when the real time was 2026-09-03 09:57 — wrong by 19 DAYS. Two local clocks agreed and were both wrong, so local agreement proves nothing. Required:
  (a) External authoritative time: `curl -sI https://www.google.com | grep -i '^date:'` (or web_fetch https://timeapi.io/api/Time/current/zone?timeZone=America/New_York)
  (b) Local time: `TZ=America/New_York date`
  (c) If they differ by more than ~5 minutes, THE EXTERNAL SOURCE WINS. Note the skew in the digest.
  (d) Cross-check any date stated in the session environment as a third anchor.
Then: if the true Eastern time is outside 9:00 AM–8:00 PM, send NOTHING (no text, no email, no Indeed) and skip to logging. Reading, harvesting, reply-checking, logging, and calendar work are allowed any time; only OUTBOUND SENDING is gated. Never infer time from run timestamps or session start.

STEP 1 — CONTACT NEW APPLICANTS (inside the window only). Open https://employers.indeed.com/jobs in Chrome (fullcirclepawn@gmail.com, saved login). Check candidates PER LISTING via the per-job URLs in HIRING_OUTREACH.md — never the merged "all jobs" view (it hides which store/role someone applied to; naming the wrong store is unacceptable). Viewing a profile flips New→Reviewing, so also scan Reviewing for anyone missing from the contact log. Pull name, email, phone (@indeedemail.com relay addresses are normal). Send the template personalized with first name, role, store — identical on every channel, NO opt-out line: (a) email via Gmail MCP, (b) text via mcp__Read_and_Send_iMessages__send_imessage, (c) Indeed in-app (KNOWN BLOCKER: React-controlled textarea resists automation; try the untried approaches in HIRING_OUTREACH.md, else log ✗ and move on — email+text are sufficient per Joshua). NEVER claim a channel sent when it didn't. Max ~10 texts per run, spaced a few seconds apart; verify each send.

STEP 2 — FOLLOW UP WITH NON-RESPONDERS (inside the window only). Day 2 follow-up #1, Day 5 follow-up #2, both text + email, wording in HIRING_OUTREACH.md Stage 2. Three touches total, then CLOSED–NO RESPONSE. Any reply cancels remaining follow-ups. Day counts use the TRUE date from Step 0.

STEP 3 — CHECK REPLIES ON ALL THREE CHANNELS (any time): (1) text via read_imessages on contacted numbers, (2) email via Gmail search for inbound from contacted addresses and replies to "Valley Pawn — let's talk about your application", (3) Indeed in-app at https://employers.indeed.com/messages.

STEP 4 — WORK EACH REPLY TOWARD A TIME (sends inside the window only). Answer on the SAME channel they used. Specific time → Step 5. Interested but vague → ask what day/time works. Question asked → answer from the job post AND ask for a time in the same message. Not interested → CLOSED/OPT-OUT.

STEP 5 — BOOK AND CONFIRM. Create the event on calendar jdavis@fcfpawn.com per HIRING_OUTREACH.md: title "Interview — {Name} — {Role}, {Store} ({Phone|Zoom|In person})", 30 min, location = their phone number / Meet link via addGoogleMeetUrl / store street address, description = phone + email + listing + latest role, reminders 60 and 10 min. Check list_events first to avoid double-booking; on conflict offer the nearest open slot. Accept interview times 7:00 AM–9:00 PM ET. Then confirm to the candidate on their channel ("You're set — {day} at {time}, Joshua will call you at {number}") — a booking isn't done until they're told. DM Joshua on Slack (D03BHQH5VGT). Once booked, stop all other outreach to that person. Handle reschedules by updating the event and re-confirming.

STEP 6 — DAILY DIGEST (run nearest 7PM ET only, and ONLY if there was activity in the last 24h — zero activity means post NOTHING). Post to Slack #employee-prospects (C0BQDRXRPEJ). Lead with today's + tomorrow's interviews, then replied-but-unscheduled, then new applicants contacted with per-channel status, then follow-ups sent, gaps, opt-outs, possible no-shows, and any clock skew detected in Step 0. Slack read access on this private channel is CONFIRMED; posting was once blocked by the permission classifier — if the post fails, DM Joshua (D03BHQH5VGT) the digest and say the channel post failed.

SPONSORSHIP RULE: all sponsored jobs run 15-day windows only, never continuous. If one is within 3 days of lapsing on a still-open role, flag Joshua via Slack DM — never auto-renew or change ad spend. Any other failure: ONE plain-language Slack DM to Joshua, never to team channels.

NOTE — TASK IS CURRENTLY DISABLED and all 5 listings are Paused/Closed per Joshua's full-stop order. Do not resume outreach until he re-enables.