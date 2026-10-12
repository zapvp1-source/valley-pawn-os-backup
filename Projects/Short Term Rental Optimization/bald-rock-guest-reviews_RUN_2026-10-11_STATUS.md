# Bald Rock Guest Review Automation — Run 2026-10-11

**Task:** Scheduled guest-review task for Mountain Luxury (282 Bald Rock Road). For every guest
checked out in the last 3 days with a Confirmed reservation, leave a 5-star host review
(Airbnb) / 5-star guest rating (VRBO) with a warm public comment, unless the Guesty conversation
thread showed issues (damage, rule violations, complaints, payment disputes) — in which case skip
and flag.

## Result: One checkout found, review-eligible, but Airbnb review flow not yet open

**Checked (Guesty → Reservations report → Past Bookings, filter `Check-out is in the last 3 days`
+ `Status In Confirmed`):** 1 row.

- **Lori Reed** — Airbnb (confirmation `HMH2NNNB42`) — check-in Oct 9, 2026, check-out Oct 11,
  2026 (10:00 AM), 8 adults, $2,635.49 total payout.

**Guesty conversation thread reviewed in full (Open in inbox):** No issues of any kind — no
damage, no rule violations, no complaints, no payment disputes. Guest was warm and easy to work
with throughout: asked for an early (noon) check-in, which Joshua accommodated; had two DocuSign
link-expiration hiccups (platform issue, not guest-caused, resolved each time); asked a simple
checkout question ("Sheets should stay on bed?") that was answered normally. **This guest clears
the bar for a 5-star host review with a warm public comment.**

**Could not complete the review — Airbnb has not yet opened the review flow for this guest.**
Checked every place a "Leave a review" action could appear, roughly 15–20 minutes after the
10:00 AM checkout:
- Hosting → Today tab (both immediately after checkout and again ~15 min later) — only shows
  the checkout card, no review follow-up card.
- Hosting → Reservations → Upcoming — Lori shows as "Past guest" but the row's "..." menu has no
  review option (Call / Message / Change reservation / Cancel / Send or request money only).
- Hosting → Reservations → Completed — Lori's reservation has not moved into this tab yet (most
  recent entry there is Erin Chase, Oct 2–4).
- Reservation detail panel (both from the Today card and from the Reservations table) — no
  review button in any section.
- Messages thread with Lori — no review-prompt banner.

Conclusion: this is normal Airbnb processing delay (the review flow typically opens some hours
after an actual checkout, not instantly), not a login/access/technical problem — Guesty, Airbnb,
and VRBO were all reachable and functioning normally throughout this run.

**VRBO side (vrbo.com/supply/reviews/post-stay-reviews, propertyId 119604391, filtered to "Need
rating"):** 0 results — no VRBO guest currently awaiting a host rating. Consistent with the
Guesty checkout filter, which found only one checkout (Airbnb) in the last 3 days.

**No review-window expiration risk** — well within the 14-day Airbnb window; plenty of runway
for the next scheduled run to pick this back up.

## Next run
Re-check Lori Reed (HMH2NNNB42) first — the checkout filter (last 3 days) will still surface her
on tomorrow's run, by which point Airbnb's review flow should be open. Complete the 5-star host
review + warm public comment then, using the thread summary above (no re-verification of the
conversation needed unless new messages came in). After Lori, next upcoming checkout on the
books is Camille Hathaway (HMCNSKQ4FE, Airbnb, Oct 26).

Login used: fullcirclepawn@gmail.com direct email/password form on app.guesty.com (per hardened
auth note — Google SSO not used). Chrome autofill handled the password.
