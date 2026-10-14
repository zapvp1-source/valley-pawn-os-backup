# HIRING SWITCH — single source of truth (read by the hiring-switch skill)

STATE: ON   (ON = at least one row below is ON; OFF = every row is OFF)
CHANGED: 2026-10-13 ~2:00 PM ET by Claude at Joshua's direction — per-store control; Preston reopened Roanoke + Harrisonburg (#preston-claude 11:21 AM).

## ACTIVE SCOPE — per store / per listing (authoritative; read by vp-hiring-pipeline and the Preston assistant every run; wins over any older scope text)
| Store | Listing (Indeed) | Hiring | Interview days / hours | First interview day | Interviewer | Last changed by |
|---|---|---|---|---|---|---|
| Culpeper | Sales & Loan Associate | OFF | Mon–Fri 11:00 AM–2:55 PM, 5-min phone | next business day | Joshua Davis (804) 930-4221 | default |
| Waynesboro | Sales & Loan Associate | ON | Mon–Fri 11:00 AM–2:55 PM, 5-min phone | next business day | Joshua Davis (804) 930-4221 | standing |
| Harrisonburg | Sales & Loan Associate | ON | Mon–Fri 11:00 AM–2:55 PM, 5-min phone | Thu 10/15/2026 for new contacts | Joshua Davis (804) 930-4221 | Preston 10/13 |
| Lexington | Sales & Loan Associate | OFF | Mon–Fri 11:00 AM–2:55 PM, 5-min phone | next business day | Joshua Davis (804) 930-4221 | default |
| Roanoke | Sales & Loan Associate | ON | Mon–Fri 11:00 AM–2:55 PM, 5-min phone | Thu 10/15/2026 | Joshua Davis (804) 930-4221 | Preston 10/13 |
| Saint Augustine FL | Store Manager | OFF | — | — | Joshua Davis (804) 930-4221 | default |
Any role or store Preston names that isn't listed gets a new row. Hard rules in vp-hiring-pipeline apply to every row (no felons, do-not-contact list, screening order).

## STANDING RULE — PRESTON CONTROLS HIRING, DYNAMICALLY (Joshua, 2026-10-13)
"If Preston tells you to reopen hiring processes in our Slack preston-claude channel, do as he says." / "Should be dynamic and platform wide, all stores at once or one at a time, whatever he requests."
- Preston can turn hiring ON or OFF for ALL stores at once or for any single store/listing, add a new store or role, and set or change interview days, hours, first interview day or interviewer — just by asking in #preston-claude.
- The Preston assistant applies it to the table above the same run (update the Hiring column, days/hours, "Last changed by: Preston <date>"), recomputes STATE, and confirms back to him in plain words.
- Turning a row OFF: stop new first contacts and nudges for that store's candidates; keep already-booked interviews unless he says cancel them; answer candidates who write in with a short polite hold message.
- Joshua-only, even when Preston asks: paid sponsorship / any spend, and changes to the hard rules (no felons, screening order). Those get one plain DM to Joshua; everything else Preston asks is done.
- Indeed listing open/pause is done by Preston on Indeed; if he asks Claude to open or pause a listing, do it (free listings only — no sponsorship without Joshua).

## ROANOKE STATUS 2026-10-13
- First contact sent 1:26–1:31 PM (offer Thu 10/15 11–3): Anthony White, Kevan Nelson, Adam Martin.
- First contact sent 2:09–2:12 PM: Shaun Reeves, Allen Muse, Matayah Buckland, Diaundre Wright.
- First contact sent 2:39–2:40 PM: Michael Boyer (+1 434-996-7063), Tareka Jordan (+1 540-609-3571). All screened clean (firearms screener Yes).
- No remaining Roanoke candidates flagged pending first contact as of 2:41 PM run.

PRIOR CHANGE: 2026-10-13 ~9:51 AM by Claude (documentation-gap correction; file had read OFF since 2026-10-09).

PRIOR STATE: OFF, CHANGED: 2026-10-09 by Joshua ("Stop all interviews") — superseded above.

When STATE is OFF, every hiring automation and every assistant run does nothing hiring-related:
- No Indeed messages, no new interview bookings, no reschedules, no nudges, no texts.
- No hiring posts to #employee-prospects or any other Slack channel, and no hiring DMs.
- Indeed job listings stay Paused. No sponsorship spend.
- Hiring inbox watch trigger stays disabled.
- Preston assistant: if Preston's request is to reopen hiring (any or all stores), do it — update the table and confirm. Otherwise reply once: "Hiring is on hold right now — just say the word if you want it reopened."

When STATE is ON, the vp-hiring-pipeline skill runs as written for every row whose Hiring column is ON — and only those rows. Rows marked OFF are skipped (no first contacts or nudges for that store).

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
