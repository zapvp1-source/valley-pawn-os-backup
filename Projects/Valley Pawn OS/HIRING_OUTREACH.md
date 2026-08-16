# Hiring Outreach — Indeed Applicant Triple-Contact Process

**Created:** 2026-08-15 · **Owner:** Joshua (execution: Claude scheduled task `indeed-applicant-outreach`)

## Purpose
Every new applicant to any Valley Pawn Indeed listing gets contacted IMMEDIATELY (within the hour) on all three channels:
1. **Indeed message** (via employers.indeed.com → Candidates → message)
2. **Email** (address from their application/resume, sent from Gmail)
3. **Text** (iMessage/SMS from Joshua's number, to the phone on their application/resume)

## Message template (all channels — keep it this simple)
> Hi {first name}, this is Joshua Davis, owner of Valley Pawn. We saw your resume for the {role} position at our {store} store and would like to talk — phone, Zoom, or in person. You name the day and time, and we'll be there.

- `{role}` = "Sales and Loan Associate" or "Store Manager" depending on the listing.
- No Mon–Wed limitation — candidates can pick ANY time (per Joshua 2026-08-15).
- Email subject: `Valley Pawn — let's talk about your application`
- Sign emails: `Joshua Davis, Owner, Valley Pawn`
- **No "Reply STOP to opt out" language** — removed by Joshua 2026-08-15: candidates contacted us first by applying, so the opt-out line reads like spam and misframes the relationship. The message is identical across all three channels. (Opt-out handling below still applies if someone asks to stop — we just don't advertise it.)

## Rules
- Check the contact log below BEFORE contacting anyone. One triple-contact per applicant, ever. No duplicates.
- If a channel is unavailable (no phone on resume, etc.), send the other two and log the gap.
- When a candidate replies with a time, DM Joshua on Slack (D03BHQH5VGT) immediately with name, store, and proposed time.
- Failures: one plain-language Slack DM to Joshua. Never message staff/team channels.
- **Opt-out (TCPA):** if a candidate replies STOP / "stop texting" / "unsubscribe" or similar, immediately stop all texting to that number, log it in the contact log as OPT-OUT, and never text them again. Email and Indeed messaging may continue unless they ask otherwise.
- **Pacing:** send no more than ~10 texts per run, spaced a few seconds apart. Bursting 40+ texts at once risks carrier spam filtering and Apple rate limits, which would silently kill deliverability. Backlog gets worked down across runs, not all at once.

## How the texting actually works (verified 2026-08-15, not assumed)
- **Sends from:** the Messages app on Joshua's Mac via AppleScript (`mcp__Read_and_Send_iMessages__send_imessage`). Account handles on this machine: `+18049304221` and `zapvp1@me.com`. Texts arrive from Joshua's real number.
- **Non-Apple phones work.** Verified against `~/Library/Messages/chat.db`: trailing-90-day outbound volume was 2,938 iMessage + 299 SMS + 186 RCS. Live SMS/RCS traffic confirms iPhone Text Message Forwarding is enabled, so Android recipients get a standard SMS/RCS text.
- **Replies** land in Joshua's normal Messages threads (Mac + iPhone) — nothing intercepts them. The task detects them by reading the thread per contacted number.
- **Dependency / failure mode:** this whole channel depends on Joshua's Mac being awake, signed into Messages, and the iPhone being reachable for SMS relay. If the Mac is asleep or offline, texts silently do not send. The task must verify each send and log ✗ rather than assuming success.

## Reply detection — ALL THREE CHANNELS, every run
A candidate may answer on any channel we used. Check all three every run; do not assume a channel is quiet just because another one is.

1. **Text** — `mcp__Read_and_Send_iMessages__read_imessages` on each contacted number in the log that isn't yet marked replied.
2. **Email** — search Gmail for replies. Use `search_threads` for recent inbound mail from contacted addresses (including `@indeedemail.com` relay addresses, which is how most Indeed applicants' mail arrives) and for replies to subject "Valley Pawn — let's talk about your application".
3. **Indeed in-app** — check https://employers.indeed.com/messages for unread/new candidate replies. Indeed shows an unread badge in the top nav; open the Messages section and read any threads with candidate responses.

For every reply found:
- **Proposes a time** → schedule it (see below), then DM Joshua on Slack (D03BHQH5VGT) with name, role/store, channel, and the time.
- **Interested but no time given** → reply asking for two or three windows that work; log it.
- **Asks to stop** → cease that channel permanently, mark OPT-OUT in the log.
- Mark the reply in the contact log with channel + date so it's never double-handled.

## HARD RULE — CONTACT WINDOW: 9:00 AM to 8:00 PM ET ONLY (set by Joshua 2026-08-15)
**No outbound message of any kind — text, email, or Indeed — outside 9:00 AM–8:00 PM Eastern. No exceptions.**
- **Check the real clock before every send batch.** Do not infer the time from when a session started or from a scheduled-run timestamp; a long session can drift many hours. Run `TZ=America/New_York date` (or the equivalent on the host) and read it.
- If the current time is outside the window, send NOTHING and stop. Do not "just send a couple." Queue the work for the next run inside the window.
- Task cron is `0 9-19 * * *` (hourly 9 AM–7 PM ET) so the last run has time to finish sending before 8 PM. The cron is a guardrail, not the check — the runtime clock check above is still mandatory, because a run can start at 7:xx and keep working past 8.
- Reading, harvesting contact details, logging, and scheduling are fine any time. **Only outbound sending is restricted.**

> **Why this rule exists:** on 2026-08-15 a session was told "run it" and was one step from texting ~19 candidates at **11:05 PM on a Saturday**. It had been working since late morning and had no idea how much time had passed. Nothing in the system would have stopped it. The clock check is now mandatory and explicit.

## THE FULL LOOP — first contact → booked phone interview (added 2026-08-15)
The goal is a booked interview, not a sent message. Default format is **PHONE** unless the candidate asks for Zoom or in person. Every stage below is required; the loop is what converts, not the first touch.

**Stage 1 — First contact (Day 0).** Email + text + Indeed message (Indeed when it works). Template as above.

**Stage 2 — Follow-up for non-responders.** Most applicants don't answer the first message; without follow-ups this pipeline mostly produces silence. Cadence per candidate:
- **Day 2** — one follow-up, text + email: *"Hi {first name}, Joshua Davis with Valley Pawn following up on the {role} position in {store}. Still interested? Happy to do a quick call whenever works for you."*
- **Day 5** — final follow-up, text + email: *"Hi {first name}, last note from me on the {role} role at Valley Pawn in {store}. If you'd still like to talk, just reply with a day and time that works."*
- **Stop after Day 5.** Three touches total, then mark CLOSED–NO RESPONSE in the log. Never a fourth.
- Any reply cancels all remaining follow-ups immediately.

**Stage 3 — Work the reply toward a time.** Always answer on the SAME channel the candidate used (text reply to a text, email reply to an email, Indeed reply to an Indeed message), same day.
- Gave a specific time → Stage 4.
- Interested but no time → *"Great — what day and time work best for a quick call? I'll work around your schedule."*
- Asked a question (pay, hours, duties) → answer it plainly from the job post, then ask for a time in the same message. Never answer without asking for the time.
- Not interested / asked to stop → mark CLOSED or OPT-OUT, cease contact.

**Stage 4 — Book it and confirm.** Create the calendar event (format below), then confirm back to the candidate on their channel: *"You're set — {day}, {date} at {time}. Joshua will call you at {their number}. Talk then."* If in person, give the store address; if Zoom/Meet, give the link. A booking is not complete until the candidate has been told.

**Stage 5 — Keep it alive.** If a candidate asks to move a booked interview, reschedule the calendar event and re-confirm. If a booked time passes with no calendar change and no note, flag it to Joshua in the next digest as "possible no-show — follow up?"

**Acceptable booking hours:** 7:00 AM–9:00 PM ET, any day. Candidates name their own time (that's the promise in the outreach message) — this range only guards against a 2 AM booking from a typo. Anything outside it gets a polite ask for a different time. *Assumption made 2026-08-15 because Joshua's own interview availability was never specified — adjust if wrong.*

**Once booked, stop all other outreach to that person.** No follow-ups, no duplicate messages.

## Interview scheduling — the daily view Joshua asked for (added 2026-08-15)
When a candidate confirms a time, create a Google Calendar event immediately. This calendar IS the daily schedule — it's what Joshua checks, so it must be accurate and complete.

- **Calendar:** `jdavis@fcfpawn.com` (his primary — resolved via `list_calendars` 2026-08-15).
- **Title format:** `Interview — {Candidate Name} — {Role}, {Store} ({Phone|Zoom|In person})`
  e.g. `Interview — Rita Allen — Sales & Loan Associate, Waynesboro (Phone)`
- **Duration:** 30 minutes default unless the candidate/Joshua says otherwise.
- **Location field:**
  - Phone → the candidate's phone number, so Joshua can tap to dial from the event
  - Zoom → set `addGoogleMeetUrl: true` (Meet is what's wired up; use a Zoom link only if Joshua supplies one) and put the link in the event
  - In person → the full street address of the relevant store from `valley-pawn-context`
- **Description:** candidate's phone, email, the listing they applied to, and a one-line summary of their most recent role from the resume, so Joshua walks in informed.
- **Reminders:** popup 60 minutes and 10 minutes before.
- **Never double-book** — check `list_events` for that window first. If it conflicts, propose the nearest open slot to the candidate rather than stacking.

### Daily digest must include the schedule
The #employee-prospects post (activity days only) leads with:
1. **Today's and tomorrow's interviews** — time, candidate, role/store, channel
2. **Replied, needs a time** — candidates who answered but haven't committed
3. **New applicants contacted** — per listing, with per-channel ✓/✗
4. **Gaps / opt-outs**

## Active listings (as of 2026-08-15, all Sales & Loan Associate roles $18–22/hr)
| Store | Status | employerJobId (URL-encoded) |
|---|---|---|
| Culpeper | Open (free, flagged — needs sponsorship for search visibility) | aXJpOi8vYXBpcy5pbmRlZWQuY29tL0VtcGxveWVySm9iLzUwYzczMTJlLWE4NzctNDViNy04MTRkLTc4Yjk2MDcwNDE2MA%3D%3D |
| Waynesboro | Open, sponsored — Indeed shows "Sponsorship ends in 14 days" as of 2026-08-15 (≈2026-08-29, NOT ~8/17 as previously noted) | aXJpOi8vYXBpcy5pbmRlZWQuY29tL0VtcGxveWVySm9iLzY2NGY1NDI0LTVlNjUtNGE5Ni04MTJiLWJmODk5MDE5Mzc3NQ%3D%3D |
| Harrisonburg (Associate) | OPEN (corrected 2026-08-15 per Joshua — earlier "PAUSED" note was wrong). 15 New applicants in backlog. | aXJpOi8vYXBpcy5pbmRlZWQuY29tL0VtcGxveWVySm9iL2JlZDA3ZDNmLTZiNzAtNDU2Yi04MmQyLWViNDM5MzE5M2MwOQ%3D%3D |
| Roanoke | Open (free, flagged — needs sponsorship for search visibility) | aXJpOi8vYXBpcy5pbmRlZWQuY29tL0VtcGxveWVySm9iLzljZTdmZmEyLTU5NjEtNGUyMS04Yjk2LTgwZmY0OGI4NTQwOA%3D%3D |

## Manager listing (now IN SCOPE for triple-contact, added 2026-08-15)
| Store | Title | Pay | Status | employerJobId (URL-encoded) |
|---|---|---|---|---|
| Harrisonburg | Store Manager | $22.00–$26.00/hr | Reopened 2026-08-15. Sponsorship capped to **15 days, ends 2026-08-29** ($10/day, $150 max — Joshua's explicit cap, not continuous). 29 total applicants (older, unreviewed — 5 marked New), pre-existing screening Qs incl. "list 2-3 interview time ranges". App updates also route to preston@fcfpawn.com (informational copy — does not replace the triple-contact process). | aXJpOi8vYXBpcy5pbmRlZWQuY29tL0VtcGxveWVySm9iLzQ0Yjc0MmM3LWVkN2YtNDJiMC1iMmI3LTdiOTEzM2I4OWRiYQ%3D%3D |

This manager listing is now included in the hourly scheduled task's checklist alongside the 4 associate listings — same triple-contact treatment, immediate on new applicant.

**Reminder for whoever revisits this:** re-check the sponsorship end date (2026-08-29) — if the role is still open past that, either renew for another capped window or let it lapse per Joshua's "no open-ended ad spend" preference.

## Daily Slack digest (added 2026-08-15, updated 2026-08-15 — activity-only)
Once per day, in addition to the immediate per-applicant triple-contact, post a summary to **#employee-prospects** (https://valleypawnworkspace.slack.com/archives/C0BQDRXRPEJ) — **only if there was activity in the last 24 hours**:
- New applicants in the last 24 hours, by listing (store + role)
- Triple-contact status for each (Indeed ✓/✗, email ✓/✗, text ✓/✗)
- Any candidate replies with a proposed interview time (also DMed to Joshua per the existing rule)
- Any gaps (missing phone/email on an application)
**If there were zero new applicants in the last 24 hours, skip the post entirely — no "no new applicants today" filler.** Per Joshua 2026-08-15: only post when there's something to report.

Jobs list: https://employers.indeed.com/jobs (account fullcirclepawn@gmail.com, Chrome saved login)

## Contact log
Format: `| date | name | store | indeed ✓/✗ | email ✓/✗ (address) | text ✓/✗ (number) | notes |`

| Date | Name | Store | Indeed | Email | Text | Notes |
|---|---|---|---|---|---|---|
| 2026-08-15 | Rita Allen | Waynesboro — Sales & Loan Associate | ✗ | ✓ ritaallen83_gpj@indeedemail.com | ✓ +15404707493 | Text + email confirmed sent (original outreach 11:58 AM). Indeed in-app message NOT sent (composer issue, since solved per recipe below — Rita's Indeed leg still never completed). REPLIED by text 9:35 PM: "Sorry I just saw this and anytime except tomorrow morning I'm going to church." **NOT YET BOOKED — needs correction next window (see After-Hours Violation note below).** A garbled auto-reply went out at 10:05 PM ET containing raw calendar-metadata text instead of a real message; she replied confused ("Sure thing what time," 10:11 PM) — she was never actually given a proposed time. No calendar event created. Next 9AM+ run must send a clean message proposing a specific Sunday/Monday time (not Sunday AM, per her church note) and book once she confirms. |
| 2026-08-15 | Tessa Serrett | Waynesboro — Sales & Loan Associate | ✓ (4:44 PM) | ✓ tessaserrettw8zev_arj@indeedemail.com | ✓ +15404701417 | Full triple contact. Applied today. REPLIED on Indeed 4:46 PM ("whenever you're free is fine with me"). Proposed Mon 1 PM phone via Indeed reply (5:06 PM) + text. INTERVIEW BOOKED: Mon 2026-08-17 1:00–1:30 PM ET, phone, on jdavis@fcfpawn.com (event 0048d14jjvk9dg76fddrt3qdj0). **CONFIRMED by candidate via text 5:14 PM ("1pm is fine with me").** No further action needed. |
| 2026-08-15 | Leeann Adkins | Waynesboro — Sales & Loan Associate | ✓ (4:43 PM) | ✓ serenitysmommy212@gmail.com | ✓ +15402927084 | Full triple contact. Applied 8/14. REPLIED by text 5:57 PM: "Thank you I can come Monday in person." **NOT YET BOOKED — needs correction next window (see After-Hours Violation note below).** An automated reply went out at 9:01 PM ET saying "phone" instead of in-person and gave no specific time; garbled/duplicated text ("on phone on phone"). No calendar event created. Next 9AM+ run must send a clean message confirming IN-PERSON Monday, ask for a specific time, and give the Waynesboro store address, then book. |
| 2026-08-15 | Lee Cornelison | Waynesboro — Sales & Loan Associate | ✓ (4:42 PM) | ✓ evanbrown4kh6x_nno@indeedemail.com | ✓ +15406497816 | Full triple contact. Applied 8/14. No reply yet as of 8/15 11 PM check. NOTE: relay email alias reads "evanbrown" — as shown on his application; monitor for mismatch. |
| 2026-08-15 | Tracey Aylor | Waynesboro — Sales & Loan Associate | ✓ (4:41 PM) | ✓ traceyaylorgbvia_xw5@indeedemail.com | ✓ +15405229358 | Full triple contact. Applied 8/13. |
| 2026-08-15 | Steven Faulkner | Harrisonburg — Store Manager | ✓ (4:48 PM) | ✓ stevenfaulkner47_am7@indeedemail.com | ✓ +15408364886 | Full triple contact. Older applicant (Nov 2025). |
| 2026-08-15 | Dakota Dickenson | Harrisonburg — Store Manager | ✓ (4:49 PM) | ✓ dakotadickenson7_3vw@indeedemail.com | ✓ +15404488843 | Full triple contact. Older applicant (~8 mo). |
| 2026-08-15 | McKenna Haines | Harrisonburg — Store Manager | ✓ (4:51 PM) | ✓ hainesmckenna45673_4cc@indeedemail.com | ✓ +15409649366 | Full triple contact. Older applicant (~8 mo). |
| 2026-08-15 | Alex Randall | Harrisonburg — Store Manager | ✓ (4:52 PM) | ✓ alexrandall86_5ke@indeedemail.com | ✓ +15402444967 | Full triple contact. Older applicant (~8 mo). |
| 2026-08-15 | Annabella Funkhouser | Harrisonburg — Store Manager | ✓ (4:53 PM) | ✓ annabellafunkhouser5eby8_x9c@indeedemail.com | ✓ +15408105419 | Full triple contact. REPLIED by text 4:48 PM same day — proposed Mon 3 PM; Joshua confirmed phone call by text. INTERVIEW BOOKED: Mon 2026-08-17 3:00–3:30 PM ET, phone, on jdavis@fcfpawn.com calendar (event 54gs2krj3c69i3mte4bhdro8m4). |

### BACKLOG — Harrisonburg Sales & Loan Associate: 15 New applicants NOT yet contacted (as of 2026-08-15 4:55 PM)
Listing is OPEN (manual previously said PAUSED — corrected per Joshua 2026-08-15, "it's been open"). 15 New candidates await triple contact. This run hit the ~10-text pacing cap (9 sent). Next runs: work these down ~10 per run via the per-listing New tab.

### SOLVED — Indeed in-app messaging recipe (verified 2026-08-15, 9 messages sent)
The composer blocker is solved. Working recipe, per candidate:
1. Open candidate profile → click the "Send new message" button (aria-label `Send new message`).
2. If the chat popup opens minimized (dark bar bottom-right with candidate name), click the bar to expand it.
3. `form_input` on the composer textbox (placeholder starts "Use AI to help draft or refine…"). Do NOT use the "Write private note here..." box — that's a private note, not a message.
4. Coordinate/ref clicks on Send are unreliable — dispatch a JS click on the visible enabled Send button instead: `[...document.querySelectorAll('button')].filter(b=>b.textContent.trim()==='Send'&&!b.disabled&&b.offsetParent).pop().click()`
5. VERIFY by screenshot: the message must appear in the thread with a "Sent H:MM PM" stamp before logging ✓.

## READINESS STATE — what is PROVEN vs UNPROVEN (as of 2026-08-15, honest assessment)

**Proven against real output:**
- Listing pay updates + Roanoke typo fix — saved and re-read on screen
- Sponsorship 15-day caps (Waynesboro Aug 15–29, Store Manager Aug 15–29) — confirmation pages read
- Outbound TEXT — 1 send verified in `~/Library/Messages/chat.db` (Rita Allen, 11:58 AM)
- Outbound EMAIL — 1 send, Gmail returned message id `1a00625ac94d328b`
- SMS/RCS relay reaches non-Apple phones — 90-day history shows 299 SMS + 186 RCS sent from this Mac
- Google Calendar read access — `list_calendars` returned Valley Pawn Operations + jdavis@fcfpawn.com
- Slack channel `#employee-prospects` (C0BQDRXRPEJ) exists and is searchable — **private** channel

**UNPROVEN — never once executed successfully:**
- **The scheduled task itself.** One run fired (12:09 PM ET) and accomplished nothing. It has never completed end to end. Everything below depends on it.
- **Reply detection on all 3 channels** — spec written, never run
- **Calendar event creation** — not one interview event has ever been created
- **Slack posting** — `slack_send_message` to C0BQDRXRPEJ was BLOCKED by the Cowork permission classifier on 2026-08-15. Unknown whether a scheduled run can post. Also unverified whether the Slack app is even a member of this private channel (private channels reject non-member apps). **If posting fails, the daily digest silently never appears.**
- **Indeed in-app messaging** — actively broken, see blocker below
- **15 of 16 applicants** — still not contacted at all

**Bottom line: the plumbing is laid; water has never run through it.** Do not describe this system as working until a full run is observed producing real contacts, a real calendar event, and a real Slack post.

### Known blocker — scheduled task runs but does nothing (2026-08-15)
Task `indeed-applicant-outreach` was created ~12:02 PM ET and its first run fired at 12:09 PM ET (`lastRunAt` 2026-08-15T16:09:14Z). Verified against OUTPUT per Rule 12, not the run record: **zero contacts were made** — the Messages database shows only the one manually-sent text (Rita Allen, 11:58 AM), and no rows were added to the contact log. No run log was written to the task folder either. Cron is correct (`0 8-20 * * *`, hourly 8AM–8PM; the sidebar's "At 08:09 AM, every day" label is a cosmetic mis-render, `nextRunAt` confirms hourly).
**Most likely cause:** the run paused on first-time tool-permission prompts (Chrome browser control, Gmail, iMessage). Scheduled runs cannot self-approve tool permissions on their first execution.
**Fix:** Joshua opens the Scheduled sidebar → `indeed-applicant-outreach` → **Run now**, and approves the tool prompts once. Approvals persist to all future runs. Until that happens the task will keep firing hourly and accomplishing nothing.

### Run log — 2026-08-15 4:09 PM ET (scheduled)
Chrome browser control DENIED for the scheduled run → could not check Indeed listings or /messages. Gmail + iMessage ARE approved and worked: verified no reply from Rita Allen (text or email) and no other inbound `@indeedemail.com` mail. No new contacts made. Slack DM sent to Joshua covering the browser-permission fix (Run now + approve once) and the Waynesboro sponsorship lapse (~8/17) decision. Not the 8PM run and zero activity → no #employee-prospects digest.

### Slack — RESOLVED, access is fine (2026-08-15)
`slack_read_channel` on C0BQDRXRPEJ succeeded (returned the channel's join/rename history), so the app CAN see the private channel — membership is not the problem. The earlier failure was purely the Cowork permission classifier blocking `slack_send_message` in an interactive session. A scheduled run may or may not hit the same gate, so the task now has a fallback: if the channel post fails, DM the digest to Joshua instead. Channel members: Joshua + Preston Peters.

### Known blocker — Indeed in-app messaging (2026-08-15, 5 approaches tried, ALL FAILED)
The candidate-page composer is a single React-controlled `<textarea>`. Attempts:
1. Coordinate click + `type` → no text, Send stays disabled
2. Element-ref click + `type` → same
3. `form_input` → unavailable (classifier outage), retry later
4. **`javascript_tool` with the native `HTMLTextAreaElement.value` setter + `input`/`change` events** → the value DOES land (verified `ta.value.length` = 236) but React re-renders and wipes it; the field visually keeps its placeholder and Send never enables
5. `Escape` to clear the "Easily schedule…" onboarding tooltip, then click + type, then the widen-compose control → still nothing

An onboarding tooltip ("Easily schedule in-person, phone, and video interviews in one place") persistently overlays the compose area and may be intercepting pointer events — dismissing it permanently by clicking its own close control, in a real human session, is worth trying before anything else.
**Not yet tried:** React fiber access (`ta[Object.keys(ta).find(k=>k.startsWith('__reactProps'))].onChange({target:{value:msg}})`), Indeed's `/messages` section compose (different component tree), or Indeed's own "Draft a reply" AI control then editing. **Joshua's call 2026-08-15: email + text are sufficient for now** — this stays a background improvement, not a blocker on the pipeline.

### Run log — 2026-08-15 11:09 PM ET (reading/verification only, outside contact window)
Clock check: `TZ=America/New_York date` → 11:09 PM ET, outside the 9AM–8PM window. Per the hard rule, sent NOTHING (no text/email/Indeed). Read-only verification pass instead:
- **Found an After-Hours Violation from an earlier session tonight.** Two candidates got outbound texts AFTER the 8PM cutoff, both garbled:
  - **Rita Allen** — 10:05 PM ET text reads as raw calendar-metadata plist garbage ("Monday!! iI NSDictionary...") instead of real words. She replied confused ("Sure thing what time," 10:11 PM) — never actually told a time.
  - **Leeann Adkins** — 9:01 PM ET text said "Let's talk on phone on phone Monday!!" (duplicated word, garbled) even though she'd asked for **in-person**, not phone. No time given.
  - Root cause guess: the send tool/iMessage auto-detects date phrases like "Monday" and attaches a calendar-event data blob that's leaking into the visible message text. **This needs a fix before the next confirmation send** — avoid bare weekday words in outbound text bodies, or find why the calendar-detection payload is being included as literal text.
  - Neither candidate has a calendar event yet; both need a clean, correct follow-up during the 9AM–8PM window tomorrow (2026-08-16), per the corrected contact log rows above.
- **Confirmed via Indeed + iMessage:** Tessa Serrett texted "1pm is fine with me" (5:14 PM) confirming her Monday 1 PM interview — already booked, no action needed.
- Checked Gmail (`subject:` search + `indeedemail.com` inbound) and iMessage for Rita, Tessa, Leeann, Lee Cornelison, Tracey Aylor, Steven Faulkner, Dakota Dickenson, McKenna Haines, Alex Randall — no other replies found.
- Checked Indeed Messages inbox directly (screen-read, not automation-send): confirms the above and surfaces a **separate, older backlog of unread candidate messages unrelated to today's process** — Dakota Fitzgerald (Aug 8, "I'd like to schedule another interview if possible"), Khamekka Hubbard (Aug 7, asking if the Roanoke role is still open), Sherry Mayne (Aug 12), Allison Campbell (Aug 5), Taija Thompson (Jul 29), Nicole Nesselrodt (Jul 29) — all show unread indicators and predate the 2026-08-15 triple-contact process (different message template, looks like Preston's or an earlier round). Not actioned — flagged to Joshua, not in scope of today's contact log.
- Did not check the Harrisonburg Associate 15-applicant backlog or run new-applicant harvesting this pass — reading is allowed anytime but the priority was verifying tonight's mess before adding more; next window's run should still start with new-applicant coverage per the normal loop.
- Slack DM sent to Joshua (D03BHQH5VGT) summarizing the violation, the two candidates needing correction, Tessa's confirmation, and the old unread-thread backlog.

### Superseded blocker note — Indeed in-app messaging (original entry)
The candidate-page message composer (`Send new message` → textbox) did not accept programmatic text entry; the Send button stayed disabled after both coordinate-click+type and ref-click+type. `form_input` was unavailable at the time (classifier outage) and has not yet been tested against this field. **Until this is solved, the "triple" contact is effectively a DOUBLE contact (email + text).** Options to try next run, in order: (1) `form_input` on the textbox ref, (2) the "Widen compose area" control then type, (3) `javascript_tool` to set the field value and dispatch an input event, (4) Indeed's Messages section (`/messages`) rather than the candidate panel. Do not report a triple contact as complete unless the Indeed message actually sent.
