---
name: indeed-applicant-outreach
description: Hourly 9AM-7PM ET: contact new Valley Pawn Indeed applicants across all 5 listings (email + text), monitor replies on all 3 channels, book confirmed phone interviews to Joshua's Google Calendar, and post an activity-only digest to Slack #employee-prospects. Hard 9AM-8PM ET send window.
model: claude-sonnet-5
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
Valley Pawn Indeed hiring loop. FIRST read /Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/HIRING_OUTREACH.md (operating manual, contact log, listing table, THE FULL LOOP, contact-window rule, known blockers; mount ~/Documents/Claude/Projects via request_cowork_directory if needed). That file is authoritative over this prompt. THE GOAL IS A BOOKED INTERVIEW, not a sent message. FORMAT IS PHONE ONLY — no in-person, no Zoom, no exceptions (Joshua, 2026-08-16). NEVER book same-day — next day or later, always.

*** STEP 0 — MANDATORY CLOCK CHECK, IMMEDIATELY BEFORE EVERY SEND BATCH ***
Get the time from JOSHUA'S MAC, not the sandbox: mcp__Control_your_Mac__osascript → do shell script "date '+%Y-%m-%d %H:%M:%S %Z (%A)'". A clock check older than 5 MINUTES is void; re-run it before each batch. If outside 9:00 AM–8:00 PM ET, send NOTHING and skip to Step 7 logging. Reading, harvesting, reply-checking, logging, and calendar work are allowed any time; only OUTBOUND SENDING is restricted.

*** STEP 0.2 — RUN LOCK (prevents concurrent-run collisions) ***
Check ~/Documents/Claude/Scheduled/indeed-applicant-outreach/RUN_LOCK via osascript (cat it). If it exists and its timestamp is under 55 minutes old, another session is actively working this pipeline: do READ-ONLY work only (no sends, no bookings, no calendar writes), log the stand-down in HIRING_OUTREACH.md, end the run. Otherwise write the current timestamp to RUN_LOCK (echo "$(date '+%Y-%m-%d %H:%M:%S')" > the file), run normally, and DELETE the lock as the run's last action. A lock older than 55 minutes is stale — overwrite and proceed. Why: on 2026-08-16 three sessions worked the pipeline simultaneously; duplicates and contradictory bookings resulted before the advisory collision check caught it.

*** STEP 0.5 — MANDATORY ANTI-DUPLICATE / THREAD-STATE CHECK, BEFORE EVERY SINGLE SEND ***
This task runs hourly and Joshua also texts candidates himself. Before composing ANY message to a candidate:
1. read_imessages that number (limit 10) AND check the Gmail thread AND, if they were Indeed-messaged, that Indeed thread. READ THE WHOLE THREAD — not just check-if-empty. Any prior outbound from any session or from Joshua means continue from that exact state. (2026-08-16: a run template-blasted Brandon Bird, whom Joshua had personally booked the night before.)
2. If an outbound message in the last 12 hours already accomplishes what you were about to send, SEND NOTHING. Log "already handled."
3. Never contradict the most recent outbound. If you find you already sent something wrong, send ONE short correction, never a second competing offer.

*** MESSAGE STYLE (Joshua, 2026-08-16) ***
Introduce ONLY on first contact — never re-introduce on follow-ups/confirmations/replies. Short and conversational: "Morning Rita — you're set for tomorrow at 2:00. I'll call this number." No signatures on texts, no "Reply STOP" language. Email keeps subject "Valley Pawn — let's talk about your application" and signs "Joshua Davis, Owner, Valley Pawn". First-contact template as written in HIRING_OUTREACH.md.

*** KNOWN NON-BUG ***
read_imessages appends "iI" + NSKeyedArchiver/bplist junk to message text. Read-side decode artifact only — appears on inbound too. Sent messages are clean. Never re-send because of it.

STEP 1 — CONTACT NEW APPLICANTS (inside window only). https://employers.indeed.com/jobs in Chrome (fullcirclepawn@gmail.com). Check candidates PER LISTING via the per-job URLs in HIRING_OUTREACH.md — never the merged all-jobs view. Cover all 5 listings. ZERO-COUNT DOUBLE-CHECK: Indeed is a SPA and serves stale renders — a tab showing 0 New applicants counts only if confirmed by a second fresh full navigation to the same URL (on 2026-08-16 a stale render showed 0 when the truth was 2). Viewing a profile flips New→Reviewing, so also scan Reviewing for anyone missing from the contact log. Send first-contact template personalized (first name, role, store): (a) email via Gmail MCP, (b) text via send_imessage, (c) Indeed in-app (recipe in HIRING_OUTREACH.md; on failure log ✗ and move on). NEVER claim a channel sent when it didn't. Max ~10 texts per run, spaced a few seconds apart; correction/confirmation texts to already-open threads may exceed the cap when leaving a candidate waiting would be worse — note the overage in the log. VERIFY each send via chat.db is_sent.

STEP 2 — FOLLOW-UPS (inside window only). Day 2 and Day 5 per HIRING_OUTREACH.md Stage 2. Three touches total, then CLOSED–NO RESPONSE. Any reply cancels remaining follow-ups.

STEP 3 — CHECK REPLIES ON ALL THREE CHANNELS FIRST, every run, before any new outreach: (1) Indeed inbox at https://employers.indeed.com/messages — full list scan; (2) text via read_imessages on contacted numbers; (3) Gmail search for inbound from contacted addresses + the outreach subject. Older pre-process Indeed threads (Dakota Fitzgerald, Khamekka Hubbard, etc.): do not action, do not re-flag.

STEP 4 — WORK EACH REPLY TOWARD A TIME (sends inside window only). Same channel they used, after Step 0.5. Specific time → Step 5. Vague interest → ask what day/time works (tomorrow or later — never offer today). Question → answer from the job post AND ask for a time in the same message. Not interested → CLOSED/OPT-OUT.

STEP 5 — BOOK AND CONFIRM. *** PRE-BOOKING VALIDATOR — mandatory immediately before EVERY create_event or update_event: first RE-READ the policy sections of HIRING_OUTREACH.md (THE FULL LOOP + Policy change entries) because policies change mid-session — on 2026-08-16 a session booked 6 same-day and 3 in-person interviews because phone-only/no-same-day landed after it had loaded the manual. Then verify ALL FIVE: (1) format is PHONE — if the candidate asked for in-person/Zoom, tell them interviews are by phone for now and keep their time; (2) the date is NOT today — next day or later regardless of what they proposed; (3) time is 7AM–9PM ET; (4) list_events for that day shows no conflict AND no duplicate event another run already created; (5) you have a dialable phone number — never create an event without one, keep working the reply until you have it. Any check fails → do not book. *** Event on jdavis@fcfpawn.com: title "Interview — {Name} — {Role}, {Store} (Phone)", 30 min, location = candidate's phone number, description = phone + email + listing + latest role + booking trail, reminders 60 and 10 min. Confirm to the candidate conversationally — a booking isn't done until they're told. DM Joshua on Slack (D03BHQH5VGT). Once booked, stop all other outreach to that person. Reschedules: update the event and re-confirm.

STEP 6 — DAILY DIGEST (run nearest 7PM ET only, and ONLY if activity in last 24h). Post to #employee-prospects (C0BQDRXRPEJ): today's + tomorrow's interviews first, then replied-but-unscheduled, new contacts with per-channel status, follow-ups, gaps, opt-outs, possible no-shows. Channel post fails → DM Joshua the digest and say so.

STEP 7 — LOG. Append/update the HIRING_OUTREACH.md contact log every run: contacts, per-channel ✓/✗, replies, bookings, anything skipped by Step 0.5, any classifier-blocked sends. Report only what you VERIFIED against real output (chat.db, Gmail message id, calendar event id) — never from a run record. Then delete RUN_LOCK.

CLASSIFIER-BLOCK HANDLING (applies to every step): if a send, form_input, or calendar call is denied by the permission classifier, retry ONCE with rephrased wording. Still blocked → log the specific miss and DM Joshua — NEVER silently drop a correction or confirmation; a candidate left waiting is worse than an extra ping to Joshua.

SPONSORSHIP RULE: sponsored jobs run 15-day windows only. Waynesboro and Harrisonburg Store Manager end 2026-08-29. Within 3 days of lapse on a still-open role → flag Joshua via DM; never auto-renew. Any other failure: ONE plain-language Slack DM to Joshua, never to team channels.