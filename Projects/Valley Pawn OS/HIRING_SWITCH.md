# HIRING SWITCH — single source of truth (read by the hiring-switch skill)

STATE: OFF
CHANGED: 2026-10-09 by Joshua ("Stop all interviews")

When STATE is OFF, every hiring automation and every assistant run does nothing hiring-related:
- No Indeed messages, no new interview bookings, no reschedules, no nudges, no texts.
- No hiring posts to #employee-prospects or any other Slack channel, and no hiring DMs.
- Indeed job listings stay Paused. No sponsorship spend.
- Hiring inbox watch trigger stays disabled.
- Preston assistant: for hiring/interview/Indeed requests reply once, plainly: "Hiring is on hold right now." Nothing else.

When STATE is ON, the vp-hiring-pipeline skill runs as written.

Turn ON / OFF: tell Claude "turn hiring on" or "turn hiring off" (hiring-switch skill does every step below).

## OFF checklist (done 2026-10-09)
1. Set STATE: OFF in this file.
2. Indeed (fullcirclepawn@gmail.com) → all 5 listings Paused (Store Manager St. Augustine; Sales and Loan Associate Lexington, Waynesboro, Harrisonburg, Roanoke).
3. Disable scheduled task "Hiring inbox watch" (trig_01KAJ8yYRM2see7NB3UJQhRy).
4. Preston assistant task (trig_01CjJusgBC2hkcCg5GHziHtC) carries the hiring gate in its prompt.

## ON checklist
1. Set STATE: ON and CHANGED date here.
2. Indeed → Reopen the listings Joshua names (default: Waynesboro + Harrisonburg). Never start sponsorship spend unless Joshua says so.
3. Re-enable "Hiring inbox watch".
4. Remove the hiring gate line from the Preston assistant prompt.
5. Resume vp-hiring-pipeline; first run re-checks calendar and Indeed inbox before messaging anyone.
