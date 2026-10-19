---
name: "vp-hiring-pipeline"
description: "Valley Pawn's continuous hiring pipeline for the Waynesboro and Harrisonburg Sales & Loan Associate listings on Indeed: screen new applicants, contact them, answer replies, and book Joshua's 5-minute phone interviews for the next business day (Fri/Sat/Sun applicants go to Monday) from 11 AM. Use when the vp-hiring-pipeline scheduled task runs, or when Joshua says \"keep the hiring going,\" \"book the new applicants,\" \"who's interviewing Monday,\" \"run the hiring loop,\" or anything about scheduling candidate interviews."
---

# Valley Pawn Hiring Pipeline (continuous)

Owner: Joshua Davis (owner, Full Circle Finance Inc DBA Valley Pawn). Set up 2026-10-02 at Joshua's direction: "this needs to be a continuous process."
Load `enterprise-map`, `hiring-contact-check` and `indeed-access` first. Follow `vp-operating-rules` (no failure notices or jargon to Slack).

## Scope
- Indeed for Employers, signed in as **fullcirclepawn@gmail.com** (Chrome).
- Listings: **Sales and Loan Associate — Waynesboro** (1321 W Broad St) and **Sales and Loan Associate — Harrisonburg** (1790 E Market St). No other listings unless Joshua adds them.
- Interviewer: **Joshua Davis**, calling from **(804) 930-4221**. Preston Peters (Operations Manager) may also be talking to candidates; Joshua's instruction is to answer everyone, including Preston's.

## Hard rules
1. **No felons, period.** If an application's screener answer to "Can you pass a criminal background check for firearms?" is No, or a candidate discloses a felony, do not schedule. Mark Rejected on Indeed and send once: "Thank you for your interest and for being upfront. Because every role in our stores involves handling firearms, we're not able to move forward with your application. I wish you the best."
2. Never contact anyone with Indeed status **Rejected**, or on the do-not-contact list: Aaron Riley, Jim Helmintoller, Elizabeth Small, Shaun Snead, Kia Jasper, Bradyn Parr, Wes Fullen, and anyone Joshua later calls a "no / no go".
3. Messages are concise and polite. Only about scheduling. Never discuss pay, decisions or other candidates; if asked (for example "weekly or biweekly pay?"), reply "Great question. Joshua can cover that on your call." and DM Joshua the question.
4. Contact window: 9:00 AM–8:00 PM ET, any day.
5. Screening order (do not change): phone interview → conditional offer → Checkr background + drug screen + VSP firearms check → start. Never order screening before the interview.

## Interview slots
- 5-minute phone slots **11:00 AM–2:55 PM ET, Monday–Friday** on Google Calendar **jdavis@fcfpawn.com**.
- **Which day:** the next business day after the applicant is first contacted. Contacted Mon–Thu → next day. Contacted Fri, Sat or Sun → **Monday**, starting at 11:00 AM. If the day is full, use the next business day. Skip US federal holidays.
- Fill slots in order from 11:00 (first available); keep second-round Zoom interviews and other Joshua events clear. Always list the calendar before booking; never double-book.
- Event title: `Interview — {Full Name} — Sales & Loan Associate, {Store} (Phone)`. Location: phone number. Description: `Interviewer: Joshua Davis. Phone screen. Call from (804) 930-4221.` notificationLevel NONE.

## Each run
1. **New applicants.** On each listing's candidate list, find candidates with status New or Reviewing and no message from us in their Indeed thread (and not on the do-not-contact list). Run `hiring-contact-check` for each (Gmail "New Message from <first name>", HIRING_OUTREACH history). Apply rule 1 via screener answers first.
2. **First contact** for each clean new applicant. Send this Indeed message: "Hi {first}, this is Joshua Davis, owner of Valley Pawn. Thanks for applying for our Sales and Loan Associate position in {store}! Are you free for a quick phone interview on {Day M/D} between 11 AM and 3 PM? Reply with a time and the best number to reach you, and I'll call you." Set the Indeed status to Contacting.
3. **Replies.** Open the Indeed Messages inbox (employers.indeed.com/messages). For every thread where the candidate wrote last:
   - If they give or accept a time, book the slot (nearest open if theirs is taken) and confirm: "You're set for {Day M/D} at {time}. I'll call you at {number} from (804) 930-4221."
   - If they gave no number, ask for one.
   - If they can't do the day, offer the next business day.
   - If they decline, reply "Thanks for letting me know, {first}. Best of luck!"
4. **No-shows.** If Joshua reports a no-answer (or a call slot passed and Joshua says they didn't answer), send one reschedule offer for the next business day: "Sorry we missed each other today! Are you free {Day M/D} between 11 AM and 3 PM? Reply with a time and I'll call you." A second no-show means stop contacting them.
5. **No reply in 2 business days** after first contact: send one nudge, "Just checking in. Are you still interested in a quick phone interview? Reply with a day and time between 11 AM and 3 PM." Then stop.
6. **Text messages** (optional, batched): only at the 9:30 AM, 1:00 PM and 6:00 PM runs, and only if computer-use full-screen control is available. Use the Messages app: Cmd+N, type the +1 number, Return, click the message field, zoom to verify the To: number and text, then Return. NEVER click the sidebar conversation list (it reorders and lands in personal chats). Never type in any existing personal conversation. If screen control is unavailable, skip texting silently; Indeed messages notify candidates by email and app.

## Indeed composer (proven method)
In the Messages inbox, click the conversation `[role=option]` by name and wait 3 seconds. Click the "Easily schedule…" tooltip to dismiss it (it steals focus). Click the reply box, then verify with synchronous JS (no `await`; async evaluation hangs this page) that:
- the pane header contains the candidate's name;
- the visible textarea is focused and empty.

Type the message, verify the textarea value, click the enabled "Send" button via JS, and verify the text now appears in the thread. If focus fails, take a screenshot, click the tooltip and the box again, and retry once.

## Reporting
- After any booking change, DM Joshua (Slack D03BHQH5VGT) and post to #employee-prospects (C0BQDRXRPEJ) the updated schedule for the next interview day: time, name, store, number, confirmed/offered. Post nothing if nothing changed.
- At the first run each weekday (about 9 AM), post that day's interview list to both.
- Candidate questions you can't answer go to Joshua by DM, one line each.

## Known state as of 2026-10-02 3 PM
- **Mon 10/5:**
  - 11:00 Stephanie Chaplin, Zoom 880 9437 0222 / passcode 267473, Preston invited
  - 12:00 Jean Gonzalo, Zoom 879 2549 8704 / passcode 872206, Preston invited
  - 12:30 Kymberlyn Mitchell, phone 228-314-0355
  - Keep 11:00–12:35 clear; book Monday phone screens from 12:35 onward, then fill any earlier gaps only if Joshua says so.
- **No-shows 10/2, offer Monday:** Michele Campbell (540-290-3072), Matthew Reynolds (540-415-2551), Gabriel Troehler (540-416-6135; he prefers 1–3 PM because he works nights).
- **Contacted 10/1 with no reply yet (send one nudge offering Monday):** Clowie Smith, Cameron Hughes, Britney Landes, Elise Ripple, C. Jackson, Michael King, Anita Hedrick, Brad Andrews, Konner Collier, Glen Way, Jordyn Bolton, Jonathan Bishop, Simon Cai.
- Angelina Kioroglo: status unclear after her 10/2 11:15 call. Ask Joshua before contacting her.
- Cordell Long: had the 11:20 call 10/2. No action unless Joshua says.
- Both listings are sponsored at $10/day through Mon 10/5. Never extend or change spend without Joshua.

