---
name: cypress-roof-followup-1
description: One-time check for roofer replies re: 844 Cypress Crossing Trail same-day quotes, confirm/calendar or nudge
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Context: Joshua is trying to get roof-replacement quotes on his personal residence at 844 Cypress Crossing Trail, St. Augustine, FL 32095. Today (whatever today's date is when this runs) he wants contractors to come out THE SAME DAY if at all possible. He is jdavis@fcfpawn.com (also reachable at zapvp1@me.com) in the connected Gmail account.

Four contractors were contacted:
1. Sunshine Roof Services - sunshineroofservices@gmail.com - originally offered tomorrow (the day after initial contact) 1:00 PM; Joshua already asked them if they could move it up to today instead.
2. AK Certified Roofing - akroofing@akccfl.com - Joshua asked for a same-day afternoon slot after their morning window passed.
3. Fidus Roofing & Construction - sales@thefidusgroup.com - nudged for a same-day visit, no reply yet as of last check.
4. Enterprise Roofing - wesetthestandard@enterpriseroofingllc.com - nudged for a same-day visit, no reply yet as of last check.

DO THIS:
1. Use the Gmail connector (search_threads / get_thread with PLAIN_TEXT format) to search for new messages from each of these four sender addresses since the last check (use queries like "from:sunshineroofservices@gmail.com newer_than:1d", etc., or broader if needed).
2. For any contractor who replied proposing or confirming a specific time TODAY: verify it's a real confirmation (an actual reply in the thread, not just something referenced secondhand). Reply to confirm if it's just a proposal (say something short like "Sounds good, see you then" in Joshua's casual/short voice - no corporate phrases, no "happy to help" style filler). Then create a Google Calendar event via the calendar connector for that appointment at 844 Cypress Crossing Trail, St. Augustine, FL 32095, with a description naming the company and contact.
3. For any contractor who still has NOT replied to the "can you come today" ask: send ONE brief, casual follow-up nudge (not corporate-sounding) asking again if they can fit in a same-day visit, or if not today, the soonest available slot. Keep it under 3 sentences. Do not nudge a contractor more than once in this run.
4. If Sunshine Roof Services confirms they CAN come today, and it's replacing their previously-booked tomorrow 1pm slot, delete/update the old calendar event accordingly (search calendar for a "Sunshine Roof Services" event first).
5. Do NOT fabricate or assume any confirmation - only act on what you actually read in the email thread.
6. When done, summarize concisely: which contractors are now confirmed and for when, which are still pending, and what if anything Joshua needs to decide. Keep it factual and short - no headers, no bullet spam, just plain sentences (2-5 sentences total).

This is a one-time task - it will auto-disable after this run. A second follow-up check is separately scheduled for later.