# bald-rock-15-day-contract — run 2026-10-13 — Completed, nothing new to send

## Outcome
Window 2026-10-13 -> 2026-10-28 inclusive. Pulled via Guesty REST API (primary path, in-page
fetch with the Okta bearer token) rather than the UI grid. 113 total reservation rows on the
listing; 3 fell inside the window, of which 1 is a confirmed booking (Camille Hathaway) and 2
are inquiries (April Suarez check-in 10/27, Veronica check-in 10/28) -- both skipped per the
task's rule to only act on confirmed bookings.

## Classification (DocuSign getEnvelopes, account 320a0ff8-3001-4e1a-93b4-4fc3004b1116, from_date
2026-09-13, search_text "Hathaway")
- Camille Hathaway -- HMCNSKQ4FE (Airbnb) -- check-in Oct 22, 2026 (9 days out) -- envelope
  4af9d3eb-b025-8849-8343-89d532ffe5a9, status "delivered" (sent 2026-10-07, not yet opened or
  signed) -- classified UNSIGNED. days_until_checkin = 9 > 3, so no reminder this run; logged as
  WATCHING, same as the 2026-10-12 run.

## SEND phase
Nothing to send -- the only confirmed booking already has a non-voided envelope from 2026-10-07.

## REMIND phase
Nothing sent -- Camille Hathaway is UNSIGNED but 9 days out, past the <=3-day reminder trigger.

## VERIFY phase (age/ID 30+)
De-dup check on the Guesty conversation thread (699e3e57a76f3500145d01f9) confirmed the
"primary guest to be 30 or older" request was already sent 2026-08-07, and Camille replied
2026-08-10 "I just barely meet the minimum age!" -- confirmed. Marked VERIFIED, matches prior
runs. No new request sent (never re-send once verified).

## Slack
Posted the daily summary to Joshua's DM (D03BHQH5VGT), matching the 2026-10-12 format. Confirmed
present on re-read before closing out (self-verify per the hardening block).

## Nothing failed this run. No FAILURE_LEDGER row needed.
