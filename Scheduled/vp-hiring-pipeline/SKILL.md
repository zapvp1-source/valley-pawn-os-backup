---
name: vp-hiring-pipeline
description: Continuous Waynesboro/Harrisonburg Indeed hiring loop: screen + contact new applicants, answer replies, book Preston's next-business-day phone interviews from his Zoom line (540) 202-4200 (Fri–Sun applicants go to Monday from 11 AM)
model: claude-sonnet-5
---

Run Valley Pawn's continuous hiring pipeline. Load the `vp-hiring-pipeline` skill and follow it exactly. Load enterprise-map, hiring-contact-check and indeed-access first, as that skill says.

Joshua's standing instruction (2026-10-02): "This needs to be a continuous process. Today's applicants get booked for Monday; Sat/Sun candidates get booked for Monday starting at 11 AM." Concise and polite with every candidate. No felons, period.

INTERVIEWER CHANGE (Joshua, 2026-10-23): Preston Peters does the phone screens from his Zoom work line **(540) 202-4200**. Every candidate message names Preston and that number ("Preston will call you at {number} from (540) 202-4200."). Never give candidates (540) 836-4200 (Preston's personal cell) or (804) 930-4221 (Joshua). Bookings confirmed before 10/23 stand as they are — don't re-message them just to change the number.

Each run:
1. Screen and first-contact new applicants on the Waynesboro and Harrisonburg Sales & Loan Associate listings.
2. Answer every candidate reply in the Indeed Messages inbox and book/confirm interview slots on the jdavis@fcfpawn.com calendar (event description: "Interviewer: Preston Peters. Phone screen. Call from Zoom (540) 202-4200."), 5-minute slots, 11:00 AM–2:55 PM, next business day.
3. Handle no-shows and 2-business-day nudges per the skill.
4. Texts only at the 9:30 AM, 1:00 PM and 6:00 PM runs, and only if full-screen control is available. Never click the Messages sidebar.
5. Post schedule changes to #employee-prospects (C0BQDRXRPEJ) and DM Joshua (D03BHQH5VGT). At the first weekday run, post that day's interview list (Preston's call list). Post nothing if nothing changed. No jargon or failure notices.

---

# QUIET RULE — no "nothing new" messages (Joshua standing preference, enforced 2026-10-21 audit)

This overrides any reporting habit above. Joshua does not want routine status DMs.
- If this run changed nothing (no new applicant contacted, no reply answered, no booking made/moved/cancelled, no no-show handled, no candidate question that needs Joshua), send NO Slack message of any kind — not to Joshua's DM, not to #employee-prospects. No "nothing new to action", no "checked live: N total", no recap of counts or still-open items. Just end the run.
- When something did change, send ONE short DM to Joshua listing only what changed (and post the schedule to #employee-prospects only if the schedule changed). Never repeat the still-open list in every message; include it at most once a day, in the first weekday run's interview-list post.
- A run that could not reach Indeed (Cloudflare check, sign-in) also sends nothing to Slack; write one FAILURE_LEDGER row instead.