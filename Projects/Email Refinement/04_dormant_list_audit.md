# Dormant List Audit + Reactivation Plan

**Date:** 2026-05-28
**Scope:** Quantify the engagement pool, design a reactivation sequence, set the sunset rule.

---

## Calibration: the "95 in 6 months" number was misleading

Earlier this session I cited "only 95 contacts have clicked any link in 6 months." That came from a Brevo segment UI count and was either stale or filtered too narrowly. The real picture, pulled from per-campaign stats across the last 10 sends (March 30 → May 28):

| Metric | 10-campaign total | Avg per send |
|---|---|---|
| Emails sent | 99,916 | 9,992 |
| Delivered | 96,034 | 9,603 |
| **Real human opens (uniqueViews − MPP)** | **1,503** | **150 / send (1.57%)** |
| Apple MPP bot opens | 3,078 | 308 / send |
| **Real unique clicks** | **2,781** | **278 / send (2.90%)** |
| Unsubscriptions | 175 | 17.5 / send (0.18%) |
| Complaints | 76 | 7.6 / send (0.08%) |

**Click rate of 2.90% is inside the retail-email benchmark (2–4%).** The list isn't broken. But it's not optimized either, and the trend is bad: weekly click rate dropped from 3–6% in March/April to 1–1.5% in May. Classic list-fatigue.

True engaged-subscriber estimate (unique humans who clicked anything in last ~2 months): **somewhere between 800 and 1,500** of 9,700 deliverable. That's ~8–15% engaged. The remaining 8,000–9,000 are silently receiving every send without ever clicking.

---

## What's working / not working

**Working:**
- Gold & Silver themed sends (campaigns #4, #6) — 3.7% and 1.96% click rates, both above weekly avg
- April Fools' Day campaign (#2) was the breakout: 6.27% click rate
- Unsub rate is healthy (well under 0.5% red line)
- Master Template is now instrumented (this session's work) — future sends will give per-link cohort signal

**Not working / red flags:**
- Weekly click rate has compressed 4–6x in two months (engagement decay)
- May Gold email had 16 spam complaints vs 0 on April Gold — content drift or subject-line shift worth investigating
- April Fools' campaign also hit 0.54% unsub and 0.54% complaint — over the red line both ways (aggressive copy?)
- Real opens (1.57%) lag real clicks (2.90%) — unusual; means MPP filter is suppressing legit reads OR our recipients open emails without our tracking pixel firing

---

## The reactivation/cull theory

Industry standard for a list with ~85% dormancy:

1. **Define dormant:** subscribed AND on the master list AND no click in last 90 days AND not currently in a reactivation sequence
2. **Run a 3-email sequence over 14 days** to dormant subscribers only:
   - Email 1 (Day 0) — "We've missed you" — soft re-introduction, single CTA, low pressure
   - Email 2 (Day 7) — "Is this still right?" — preference check + value reminder, exit ramp ("update your preferences or unsubscribe — no hard feelings")
   - Email 3 (Day 14) — "Last call" — final attempt with clear exit messaging
3. **Sunset non-responders:** anyone who didn't open OR click any of the 3 → move to a "Sunset" list, stop including in regular sends. Keep them reachable for transactional only.
4. **Measure the lift over 60 days:** expect engaged-rate to rise from ~2.9% → 10–15% mechanically. Domain reputation improves with Gmail/Yahoo/Apple over 30–60 days.

**Expected outcomes after the sweep:**
- Master list drops from ~9,700 deliverable → ~1,500-2,500 actively engaged
- Click rate mechanically rises 3-5×
- Inbox placement improves (provable via Gmail Postmaster Tools if connected)
- Send costs drop (Brevo pricing is per-send)
- Complaint risk drops (the people most likely to complain are the ones who already forgot they subscribed)

**One real risk:** if the master list size matters for any external optics (sales reports, "we have 11K subscribers!" claims) — be ready for the optics drop. The right framing: "We have 2,000 ACTIVE subscribers who actually do business with us, vs 11,000 who don't." Active > big.

---

## Proposed sequence — copy direction (not final)

**Email 1 — Day 0**
- Subject: "Still want to hear from Valley Pawn?"
- Preheader: "It's been a while. Quick question for you inside."
- Hero: warm, no offer
- Body: 80-100 words. Acknowledge the gap. One-line value reminder (loans, gold, used merch, the warranty). Single CTA: "Yes, keep me in."
- CTA link: tracked with `utm_content=reengagement_e1_keep_in`. Clicking marks them re-engaged automatically (via the same segmentation infra we just built).

**Email 2 — Day 7**
- Subject: "Should we still be reaching out?"
- Preheader: "Last few emails before we update your preferences."
- Body: 120-150 words. Slightly more direct. Mention the 30-day warranty, the 5 stores. Two CTAs: "Yes, keep sending" or "Update preferences" — the latter goes to a Brevo subscription-management page where they can pick what they want.
- The preference-check approach typically reactivates 2-4% of dormant.

**Email 3 — Day 14**
- Subject: "Goodbye? Or one more chance?"
- Preheader: "We'll stop emailing unless you click."
- Body: 60-80 words. Direct. Single big CTA: "Keep me on the list." Clear consequence: "If we don't hear back, we'll stop sending after this — no hard feelings."
- Brutal but honest. Recovers an additional 1-2% of dormant.

Combined recovery rate: industry standard is 5-10% across all three. On a dormant pool of 8,000, that's 400-800 reactivated subscribers who'll go on to be high-quality engaged contacts — vs the alternative of continuing to email all 8,000 with zero response.

---

## Sunset policy

**Decision rule:** at the end of the 14-day sequence, contacts who haven't OPENED (real, not MPP) OR CLICKED any of the 3 reactivation emails get moved to a list called `Dormant — Sunset` (separate from list 3). They stay there indefinitely. The regular weekly send targets the engaged segment only.

**Exception window:** contacts who later click an organic-channel touchpoint (a Bravo POS in-store visit they associated with their email, a website form they fill out, a manual "add me back" request) can be moved back to list 3 manually.

**Re-engagement on Sunset contacts:** maybe once a year, a single "things have changed at Valley Pawn — want to come back?" email. Industry data: a small percentage of long-sunsetted contacts re-engage when a big news / brand-refresh moment hits.

---

## Build order

1. Build the **Dormant segment** in Brevo: list 3 AND subscribed AND not blocklisted AND has NOT clicked any link in last 90 days.
2. Build the **Engaged segment** as the inverse: list 3 AND subscribed AND clicked at least 1 link in last 90 days. This becomes the default target for the weekly newsletter going forward.
3. Build the **Sunset list** (an actual list, not a segment) — empty for now.
4. Draft the 3 reactivation emails in Brevo as standalone campaigns OR as a 3-step automated workflow. Recommend automated workflow so the timing is hands-off.
5. Send Email 1 to the Dormant segment. Wait 7 days.
6. After Email 3 sends, run a script that moves all dormant-segment members who didn't open/click into the Sunset list and removes them from list 3.

Estimate: ~2 hours of build, then 21 days of elapsed time for the sequence + measurement.

---

## What I want from you

Greenlight to proceed with build. I'll:
- Draft the 3 emails (you'll see them before they send)
- Build the dormant + engaged segments
- Schedule Email 1 to send next Wednesday or Thursday
- Update brevo-context with the sunset policy as the new operating rule

You don't have to make any structural calls — I'll execute on the design above unless you push back on something specific.
