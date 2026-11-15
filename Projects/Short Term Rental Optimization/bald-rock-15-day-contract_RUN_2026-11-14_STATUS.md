# bald-rock-15-day-contract — run 2026-11-14 — Completed, nothing new to send

## Outcome
Window 2026-11-14 -> 2026-11-29 inclusive. Used the primary REST path (Guesty in-page fetch
against /api/reservations-reports with the Okta bearer token from localStorage, via Claude in
Chrome, already signed in) -- worked cleanly this run, no grid-render fallback needed.
reservations-reports total=119 rows; 2 fell inside the window:
- 6ac7fee0d4b186c79305595f — Stephenie Nickens, VRB-HA-TKM8P3-VE2JV (VRBO), check-in Nov 25,
  status CANCELED — excluded per constraints.
- 6ad3fce662e58ac58ec4c603 — Lina Nino, HMC5WQ2P5R (Airbnb), check-in Nov 25, 2026, status
  CONFIRMED.
No inquiry-status rows fell in this window (the prior run's open inquiry, Brittney Nov 13-15,
is now outside the window since check-in has passed the window start).

## Classification (DocuSign getEnvelopes, account 320a0ff8-3001-4e1a-93b4-4fc3004b1116, from_date
2026-10-15, search_text "Nino")
- Envelope 9d65b598-551d-85f4-8313-577a925280ee, status "sent" (sent 2026-11-10, not voided, not
  completed) -- classified UNSIGNED. days_until_checkin = 11 (Nov 25 - Nov 14) > 3, so no reminder
  this run -- logged WATCHING, consistent with the 11-10 through 11-13 runs.

## SEND phase
Nothing to send -- the only confirmed booking in window already has a non-voided envelope
(sent 2026-11-10, first time for this guest per the 11-10 run's own log).

## REMIND phase
Nothing sent -- UNSIGNED but 11 days out, past the <=3-day trigger.

## VERIFY phase (age/ID 30+)
Read the Guesty conversation thread (6ad3fce6e7c073000f929900) in full via Claude in Chrome. The
"primary guest to be 30 or older" request was sent 11/10/2026 4:12 AM; Lina replied the same day
("Good evening, Joshua. Of course, I'd be happy to send it to you." -- with what appears to be an
ID photo attachment not rendered as text) and Joshua (prior run) closed the loop at 11/10 10:33 AM
with "Thank you, Lina! You're all set." Marked VERIFIED (unchanged from the 11-11 through 11-13
runs' classification). No new request sent -- de-dup guard held.

## Slack
Posted the daily summary to Joshua's DM (D03BHQH5VGT), matching the established 11-10 through
11-13 format exactly. Checked the channel first (hardening block D) -- no "run 2026-11-14"
summary existed yet. Re-read the channel after posting (hardening block C) -- confirmed present
at ts 1794647479.002529.

## Catch-up check (hardening block A)
Yesterday's (2026-11-13) summary was present in the DM at the expected time. No gap to flag.

## Fleet publish guard
vp_dryrun.py status returned exit 1 (not armed) before posting -- published live per the guard's
own instructions.

## Nothing failed this run. No FAILURE_LEDGER row needed.
