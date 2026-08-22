---
name: interview-schedule-monday-dm
description: One-shot Monday 8/24 9AM: DM Joshua the full confirmed interview schedule for Tue 8/25+ so he can prep.
---

---
model: claude-sonnet-5
---
You are compiling Joshua's interview schedule DM. Joshua's rule (set 2026-08-21): NO interviews before Tuesday 2026-08-25; Tuesday slots start 10:00 AM ET; phone only; never same-day bookings.

STEPS:
1. Use the Google Calendar connector (calendar jdavis@fcfpawn.com): list_events from 2026-08-25T00:00 to 2026-08-29T23:59 (America/New_York). Collect every event whose title starts with "Interview —".
2. Cross-check confirmations: read /Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/HIRING_OUTREACH.md contact log (use osascript "do shell script cat ..." if file tools lack access) for which candidates confirmed vs tentative.
3. Send ONE Slack DM to Joshua (channel_id D03BHQH5VGT) via the Slack connector titled "Interview schedule for this week — prep for Tuesday". List each interview chronologically: time, candidate, role/store, phone number, confirmed/tentative status. Flag any tentative ones that still need a confirmation push, and any gaps in the Tuesday 10 AM–6 PM window.
4. Do NOT message any candidates from this task. Read-only + the one DM.

If the calendar connector fails, retry once, then DM Joshua that the schedule pull failed with a one-line reason.