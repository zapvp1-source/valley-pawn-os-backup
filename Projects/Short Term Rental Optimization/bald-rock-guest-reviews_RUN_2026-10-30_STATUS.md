# Bald Rock Guest Review Automation — Run 2026-10-30

**Task:** Scheduled guest-review task for Mountain Luxury (282 Bald Rock Road). For every guest
checked out in the last 3 days with a Confirmed reservation, leave a 5-star host review
(Airbnb) / 5-star guest rating (VRBO) with a warm public comment, unless the Guesty conversation
thread showed issues (damage, rule violations, complaints, payment disputes) — in which case skip
and flag.

## Result: 0 guests reviewed. 1 checkout found, review window not yet open on Airbnb's side.

**Checked (Guesty → Past Bookings view, sorted by Check-out descending, filter `Check-out Is in
the past` + `Status In Confirmed`, listing Mountain Luxury / Mountain Valley Luxury with Pool and
Hot Tub):** 1 reservation with check-out in the last 3 days (window Oct 27–30) — Patrick McGovern
(HMCXX8R4CZ, Airbnb, 5 adults, check-in Oct 28 2026, check-out Oct 30 2026 10:00 AM). Next-most-
recent checkout was Camille Hathaway (HMCNSKQ4FE, Oct 26) — already reviewed on the 10/27 run, out
of this run's 3-day window. Login already live on app.guesty.com — no login step needed.

**Conversation thread review (Patrick McGovern):** Read the full Guesty inbox thread end to end.
Guest is a documentary producer (Macroscopic) who booked for a film shoot in Staunton, coordinated
a location release and an on-property interview with Dr. Francis Collins (all pre-approved by
Joshua in-thread), signed the DocuSign rental agreement, confirmed the 30+ age requirement with ID,
and the group checked out a few hours early the morning of Oct 29 (stay was booked through Oct 30)
without being asked to — guest proactively told the host ("fully out of the house as of this
morning... thanks again for a wonderful stay"), host confirmed amicably. No damage, no rule
violations, no complaints, no payment dispute — early-but-notified checkout with a warm send-off
on both sides. No red flags. Guest qualifies for the 5-star review once Airbnb opens it.

**Airbnb (hosting.airbnb.com, Today tab + the guest message thread):** No "Leave Patrick a review"
follow-up card present yet — Today tab only shows the "Patrick's group of 5 checks out" event for
today, and the message thread with Patrick/Michael/Beverly has no review prompt. This matches the
pattern from the 10/27 run, where Camille's review card appeared with "13 days left of the 14-day
window" the day *after* her checkout — i.e., Airbnb opens the review window the calendar day after
checkout, not on checkout day itself. Patrick's checkout is today (Oct 30), so the card is expected
to appear starting tomorrow (Oct 31). Confirmed via three separate checks (Today feed, message
thread body, message thread "Conversation actions" panel) — none show a review option. This is
expected platform timing, not a failure.

**VRBO (vrbo.com/supply/reviews/post-stay-reviews, propertyId 119604391):** Applied the "Need
rating" filter directly — result: "No reviews found for property." Zero pending VRBO guest
ratings.

## Conclusion
0 guests reviewed this run — not because of any issue with Patrick, but because Airbnb has not yet
surfaced the review opportunity (expected: opens the day after checkout, per the observed pattern).
0 guests skipped for cause. No review-window (14-day Airbnb expiry) at risk — window hasn't started
yet for Patrick, so there's no urgency.

## Next run
Patrick McGovern (HMCXX8R4CZ) should show a "Leave a review" card starting ~Oct 31 — the next run
should check for it first before re-scanning Guesty, and complete the 5-star review + warm public
comment + private note signed "Best, Joshua" per the standard flow.

Claude in Chrome reachable throughout — no retries needed, no failures to log. Nothing written to
the fleet failure ledger (this was not a failure).
