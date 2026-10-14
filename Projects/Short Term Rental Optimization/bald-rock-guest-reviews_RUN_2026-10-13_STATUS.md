# Bald Rock Guest Review Automation — Run 2026-10-13

**Task:** Scheduled guest-review task for Mountain Luxury (282 Bald Rock Road). For every guest
checked out in the last 3 days with a Confirmed reservation, leave a 5-star host review
(Airbnb) / 5-star guest rating (VRBO) with a warm public comment, unless the Guesty conversation
thread showed issues (damage, rule violations, complaints, payment disputes) — in which case skip
and flag.

## Result: One checkout in window — already reviewed, nothing to do

**Checked (Guesty → Reservations report, filter `Check-out is between Oct 10–Oct 13, 2026` +
`Status In Confirmed`):** 1 row.

- **Lori Reed** — Airbnb (confirmation `HMH2NNNB42`) — check-in Oct 9, 2026, check-out Oct 11,
  2026, 8 adults, $2,635.49 total payout. Same guest flagged review-eligible (clean thread, no
  issues) in the 2026-10-11 run, which found Airbnb's review flow not yet open at that time.

**This run:** Airbnb → Hosting → Reservations → Completed → Lori Reed → Details. No "Leave a
review" action present — only "Read Lori's review" (her review of the host: 5 stars, "Perfect
getaway for our couples getaway... Had a few hiccups but Josh was very responsive and
accommodating") and "Message." A guest's review of the host only becomes visible to the host
before the 14-day mutual-blind window closes when **both sides have already submitted a
review** — so the host side (Joshua's review of Lori) has already been completed, sometime
between the 2026-10-11 run (not yet open) and now. Not done by this session. Performance →
Overall quality also shows her stay folded into the 100% 5-star / 5.00 rating for the period.

**Conclusion: nothing to post.** No new checkouts, and the one checkout in the window is already
fully reviewed on the host side. No skipped guests, no issues found, no review-window risk.

**VRBO side (vrbo.com/supply/reviews/post-stay-reviews, propertyId 119604391):** 0 VRBO
checkouts in the window; all 14 listed VRBO reviews already carry a host "would rent again"
rating. Nothing pending there either.

## Next run
Next upcoming checkout on the books: Camille Hathaway (HMCNSKQ4FE, Airbnb, Oct 22–26).

Login used: fullcirclepawn@gmail.com direct email/password form on app.guesty.com (per hardened
auth note — Google SSO not used). Chrome autofill handled the password. Claude in Chrome
reachable throughout — no retries needed.
