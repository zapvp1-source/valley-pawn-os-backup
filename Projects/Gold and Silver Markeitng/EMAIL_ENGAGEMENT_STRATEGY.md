# Valley Pawn — Email Engagement Strategy

**Decision date:** June 16, 2026
**Question on the table:** Should we send two emails a week instead of one to get more customers?
**Verdict:** No — hold the weekly cadence. The growth is in *who* we send to and a *win-back*, not in *more volume*.

---

## The short version

We are not under-emailing. We are emailing a mostly-dead list. Of ~9,600 deliverable
contacts, only ~95 have clicked anything in the last six months. Adding a second weekly
blast to that list is the textbook way to *lose* customers, not gain them — ~81% of
consumers unsubscribe from brands that over-communicate, and inbox providers read low
engagement as a reputation signal that then suppresses delivery for *everyone* on the list,
including our ~95 real clickers.

So we stand firm on once a week — and we execute the two higher-leverage moves our own
analytics has been recommending for a month: **segment the send** and **run a win-back**.

---

## What the data says (last ~6 weeks, #email-campiagns)

- **List is mostly dormant.** ~9,600 deliverable; ~95 clicked anything in 6 months.
- **North-star is far below target.** Calls + Texts per 1,000 sits at ~0.10 vs a ≥8 goal.
- **Engagement is thin and volatile.** Primary-CTA clicks swing 1–22 per send; Directions/1k near zero most weeks.
- **Unsubscribe rate is healthy** (~0.08%, well under the 0.5% red line) — we have room, but spending it on volume to dead inboxes is the wrong bet.
- **The standing recommendation, four weeks running:** send to the Engaged-90d segment, not the full ~9.6K. Dormant inboxes are diluting every KPI.

---

## What works elsewhere (proven tactics we're adopting)

1. **Segmentation is the biggest lever.** Segmented retail campaigns run ~100% higher click
   rates and up to 6× higher conversion than broadcasts. We switch the weekly send to the
   **Engaged-90d** segment.
2. **Structured win-back beats endless newslettering.** A 3-email reactivation series
   (value → offer → "still want these?") reactivates ~5–10% of dormant subscribers and lets
   us cleanly retire the rest. We build it for the dormant ~8,000.
3. **Use the layout our own data already proved.** The single-offer, CTA-first layout (W1)
   pulled 22 CTA clicks; the multi-block W2 pulled 1. Deals/Community themes beat
   New-Arrivals/Education on engagement repeatedly. Keep the weekly single-offer and
   CTA-first.

---

## What we're building (additive — nothing hardened gets modified)

| # | Build | Audience | Status |
|---|-------|----------|--------|
| 1 | **Engaged-90d segment** + retarget the weekly send to it | clicked ≥1 link in 90d | new segment |
| 2 | **Dormant segment** (subscribed, on list 3, not blocklisted, no click in 90d) | ~8,000 | new segment |
| 3 | **3-email win-back sequence** (Day 0 / 7 / 14) to Dormant | ~8,000 | new campaigns |
| 4 | **/keep-in-touch** page on thevalleypawn.com | win-back CTA click target | new page |
| 5 | **Sunset sweep** after Email 3 — non-responders → "Dormant — Sunset" list, removed from list 3 | non-responders | follow-up |

The Deal-of-the-Week tasks, the monthly Gold & Silver send, and the Friday
`email-analytics-weekly` job are **untouched**. Everything here is built alongside them.

---

## How we measure success

- **Win-back:** reactivation rate (target 5–10% of dormant), click-rate lift on the next 4
  sends (target 1.5–3×), complaint rate (must not rise).
- **Weekly (Engaged-targeted):** Calls + Texts per 1,000 trending toward ≥8; Primary-CTA
  click rate ≥1.5%. With dead inboxes removed from the denominator, both should jump
  immediately.
- **List health:** unsubscribe < 0.5%, spam complaints < 0.1%.

---

## When a second weekly email *would* make sense

Later — and only to the **Engaged segment**, never the full list. Once the Engaged audience
is reliably clicking, a second weekly send to *people who actually want to hear from us
twice* is low-risk. Sending twice to dormant inboxes is not. Revisit after the win-back
sweep completes and the Engaged segment has 4–6 weeks of clean data.

---

## Sources

- Growth Analytics — retail segmentation tactics 2025
- Enchant Agency — retailer re-engagement tactics
- Bloomreach — targeted email marketing strategies
- abmatic.ai — impact of email frequency on campaign success
- GlockApps — email fatigue & deliverability
- Internal: `#email-campiagns` weekly analytics, `brevo-context` skill (Phase 2 segmentation + sunset policy)
