# Bald Rock Guest Review Automation — Run 2026-10-09

**Task:** Scheduled guest-review task for Mountain Luxury (282 Bald Rock Road). For every guest
checked out in the last 3 days with a Confirmed reservation, leave a 5-star host review
(Airbnb) / 5-star guest rating (VRBO) with a warm public comment, unless the Guesty conversation
thread showed issues (damage, rule violations, complaints, payment disputes) — in which case skip
and flag.

## Result: No checkouts needing review today

**Checked (Guesty → Reservations report → Past Bookings, filter `Check-out is in the last 3 days`
+ `Status In Confirmed`):** 0 rows. The only reservation with a checkout inside the Oct 6–9
window was "Rochel" (Oct 5→Oct 7) — confirmed NOT a real stay, it is an unpaid **Inquiry**
(no stay status, $0 of $1,804.07 paid), so correctly excluded by the Status=Confirmed filter.

**Most recent real (Confirmed) checkouts**, both well outside the 3-day window and both already
fully handled:
- Erin Chase — Airbnb (HM92MJ4X9Z) — checked out Oct 4, 2026
- Michael Inzana — Airbnb (HM2XED9ECZ) — checked out Oct 2, 2026

Verified both are already closed out, not pending action:
- Guesty "Reviews left in the last 14 days" saved view shows both guests already posted their
  own public review of the stay.
- Airbnb hosting → Today tab has **no "Leave a review" follow-up cards** for either guest — if a
  host review were still outstanding it would show here, so the host side is already done (from
  a prior run or Joshua directly).
- VRBO review window not applicable to either (both are Airbnb bookings).

**VRBO side (vrbo.com/supply/reviews/post-stay-reviews, propertyId 119604391):** reviewed the
full post-stay list — every guest with a completed stay already shows "You would rent to <guest>
again" (host rating done), no outstanding "Rate guest" button found. One historical outlier
noted for awareness only, **not actionable** (6 months old, outside any review window): Stephanie
Cutler (Res #HA-63T7ZJ, Apr 3–6, 2026) has a host *response* to her review but no visible "would
rent again" rating — predates this automation's cadence, flagging in case it's a UI quirk worth a
second look sometime, not urgent.

**No review-window expirations at risk** — nothing pending inside the 14-day Airbnb window.

## Next run
Check-outs for Oct 11 (Lori Reed's group, HMH2NNNB42, Airbnb) and Oct 26 (Camille Hathaway,
HMCNSKQ4FE, Airbnb) are the next upcoming checkouts on the books — nothing to do until they
check out.

Login used: fullcirclepawn@gmail.com direct email/password form on app.guesty.com (per hardened
auth note — Google SSO not used). Chrome autofill handled the password.
