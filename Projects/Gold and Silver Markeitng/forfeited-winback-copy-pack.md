# Forfeited-Loan Win-Back — Ready-to-Deploy Copy Pack

**Companion to:** `forfeited-loan-winback-plan.md`
**Approach:** emotional / relationship-only · no incentive · no item reference
**Status:** copy staged and ready. Audience wiring (Bravo pull → Brevo segment + Chekkit) is on hold until the store-cycle fix lands.

Voice rules on every piece below: warm, plain, human. Never name the lost item. Never imply they failed. No "we miss you" guilt. No discount. No firearms (Roanoke). DBA "Valley Pawn" only. "What's Right Is Right."

---

## 1. Email — evergreen "Here whenever you need us"

Built from **VP Master Template (ID 11)** — duplicate the master, find-and-replace the 10 markers below, leave all locked blocks (logo, warranty strip, 5-store directory w/ Call+Text, hours, DBA footer) untouched. **Target a dedicated engaged/forfeited segment — never the full ~9.6K list** (per the email-analytics guidance: dormant inboxes are diluting every KPI and hurting deliverability).

### Subject line options (A/B — keep it warm, no spam triggers, ≤1 emoji)
- A: `Whenever you need us, we're here`
- B: `A quick note from Valley Pawn`
- C: `No catch — just a hello from Valley Pawn`

*(Recommend A as primary, C as the B-test.)*

### Marker fill-ins

| Marker | Value |
|---|---|
| `[[CAMPAIGN_SLUG]]` | `winback_here_for_you_2026-MM` |
| `[[HERO_EYEBROW]]` | `STILL HERE FOR YOU` |
| `[[HERO_HEADLINE]]` | `No judgment. Just help when you need it.` |
| `[[HERO_SUBLINE]]` | `A pawn loan is the rare kind of borrowing that never follows you home — and our door is open the same as it always was.` |
| `[[BODY_HTML]]` | *(see below)* |
| `[[PRIMARY_CTA_LABEL]]` | `Find your store` |
| `[[PRIMARY_CTA_URL]]` | `https://thevalleypawn.com/locations` |
| `[[PRIMARY_CTA_SUB]]` | `Walk in any time — no appointment, no pressure.` |
| `[[SUBJECT_FALLBACK]]` | `Whenever you need us, we're here` |
| (preheader) | auto-filled from `[[HERO_SUBLINE]]` |

### `[[BODY_HTML]]`

```html
<p style="margin:0 0 16px;">Hey there,</p>

<p style="margin:0 0 16px;">We wanted to reach out for one simple reason: to say the door at Valley Pawn
is always open to you — same as it's ever been.</p>

<p style="margin:0 0 16px;">Sometimes a loan works out one way, sometimes another. Either way, you walked
out that day with what you needed — and that's exactly what we're here for. There's nothing to feel funny
about, and nothing to make up for.</p>

<p style="margin:0 0 8px;"><strong>A pawn loan is one of the most honest ways to borrow there is:</strong></p>
<ul style="margin:0 0 16px; padding-left:20px;">
  <li style="margin:0 0 6px;">No credit check, and it never touches your credit score.</li>
  <li style="margin:0 0 6px;">No collections, no debt that lingers — when a loan ends, it ends.</li>
  <li style="margin:0 0 6px;">A fair, straight look at what you bring in, every time.</li>
</ul>

<p style="margin:0 0 16px;">So whether you ever need a hand again, or you just want to come browse and see what's
new, we'd be glad to see you. You're always welcome here.</p>

<p style="margin:0 0 4px;">Warmly,</p>
<p style="margin:0;">Your Valley Pawn family</p>
```

**Why this works:** opens with welcome (not "where've you been"), reframes the loan as the system working, names the three real advantages plainly, closes with an open door and zero obligation. CTA goes to the store finder — no "redeem," because there's nothing to claim.

---

## 2. Email — second angle (rotation month 3) "How pawn protects your credit"

Same template, different hero + body. Use this when a customer has already seen the "here for you" email, so the monthly touch stays fresh.

| Marker | Value |
|---|---|
| `[[CAMPAIGN_SLUG]]` | `winback_protects_credit_2026-MM` |
| `[[HERO_EYEBROW]]` | `GOOD TO KNOW` |
| `[[HERO_HEADLINE]]` | `The loan that can't hurt your credit` |
| `[[HERO_SUBLINE]]` | `Most people don't realize a pawn loan is the safest borrowing they have access to. Here's why.` |
| `[[PRIMARY_CTA_LABEL]]` | `See how it works` |
| `[[PRIMARY_CTA_URL]]` | `https://thevalleypawn.com/how-pawn-loans-work` |
| `[[PRIMARY_CTA_SUB]]` | `Two-minute read. No sign-in, no catch.` |
| `[[SUBJECT_FALLBACK]]` | `The loan that can't hurt your credit` |

Subject options: `The one loan that can't hurt your credit` · `Why a pawn loan is the safest way to borrow`

### `[[BODY_HTML]]`

```html
<p style="margin:0 0 16px;">A bank loan, a card, a payday advance — every one of them can follow you: a credit
pull, a balance, a collections call if things go sideways.</p>

<p style="margin:0 0 16px;">A pawn loan doesn't work like that. You bring in something of value, we give you a fair
loan against it, and the item sits safe with us. Pay it back and it's yours again. If life takes a different
turn, the loan simply ends — <strong>no credit hit, no collections, nothing chasing you.</strong></p>

<p style="margin:0 0 16px;">That's not a loophole. That's the whole idea — borrowing that can't snowball on you.
It's why folks across the Valley have trusted us for over a decade.</p>

<p style="margin:0 0 16px;">If you ever need it again, we're right here. Same fair look, same open door.</p>

<p style="margin:0;">— Your Valley Pawn family</p>
```

---

## 3. Chekkit SMS — the workhorse (rotation month 2)

Sent from the customer's own store number, signed by a real first name from that store. **Consent-gate first** (Chekkit opt-in list + TCPA). Quiet hours: nothing before 8am / after 9pm local. Stagger by store so replies are answered live. One re-engagement text; if no reply, leave ~90 days before they fold into normal Chekkit touches.

Merge fields: `[First]` = customer first name, `[Name]` = sending employee, `[City]` = store.

**Primary:**
> Hey [First] — it's [Name] at Valley Pawn in [City]. Just wanted you to know the door's always open here, no strings. If you ever need cash or want to come browse, we'd be glad to see you. Call or text us anytime at this number.

**Alt A (lighter):**
> [First], it's Valley Pawn [City]. No catch, no sales pitch — just a hello and a reminder we're here whenever you need us. Same fair deal as always. 👋

**Alt B (value-forward):**
> Life gets expensive. When it does, we're an easy, no-judgment option — no credit check, nothing follows you home. We're right here in [City] whenever you're ready. — Valley Pawn

Every send must honor STOP/opt-out (Chekkit handles the footer).

---

## 4. Bravo push — lightest touch (rotation month 3, app users)

Push truncates — keep it short. One re-engagement push, then fold into normal seasonal pushes. Confirm during build whether Bravo can target by loan status; if not, send brand-wide so no one is singled out (which fits "no shame").

- `Valley Pawn is here whenever you need us — cash, deals, no judgment. Tap to see what's in.`
- `Life happens. We're still here for you, same as always. 👋`
- `Need a hand again? No credit check, no catch. We've got you.`

---

## 5. Instagram / Facebook — always-on, normalize it publicly

Runs through the **Story (STYLE-E)** and **Heritage (STYLE-B)** pillars in the existing content batch — a content *angle*, not a new channel. Post FB via the `facebook-post` skill (`--store all`, or `--store Brand` for the parent page). ~1–2 of these per month folded into the batch.

**Post A — Story / STYLE-E (real hand, real counter):**
> A pawn loan is the only loan that can't hurt your credit, can't go to collections, and can't follow you home. That's not a loophole — that's the whole point. Whatever life's done lately, we're a calm, fair place to start. Come see us.

**Post B — Heritage / STYLE-B:**
> For over a decade we've been the people who say yes when the bank says no — and we don't keep score. Need us again? We're right here. What's Right Is Right.

**Post C — Story / STYLE-E:**
> Sometimes you get your item back. Sometimes life takes a different turn. Either way, you walked out with what you needed that day — and you're always welcome back. No judgment, ever.

Caption tag line for IG: include `#ValleyPawn #WhatsRightIsRight` (IG only — never on GBP).

---

## 6. Google Business Profile — high-intent catch, always-on

Run the GBP checklist on every post: **no hashtags, no phone number in body, no ALL-CAPS, ≤2 emojis, no firearms, informational tone.** ~1 trust-first post per store per month, woven into the normal GBP rotation.

**Post A:**
> A pawn loan is one of the few ways to borrow with no credit check and no effect on your credit score. If life's thrown you a curveball, we're a calm, fair place to start — and we'll walk you through exactly how it works, no pressure. Stop by any Valley Pawn and say hello.

**Post B:**
> We've helped folks across the Valley get through tight spots for over a decade — no judgment, just a fair look at what you've got. Whether you need a hand or just want to browse, the door's always open.

**Post C (after the website page is live — drives the SEO page):**
> Wondering what actually happens if you can't repay a pawn loan? The short answer: nothing follows you — no credit hit, no collections. We put the full, plain-English explanation on our website so there are no surprises. Come see us anytime with questions.

---

## Deployment order (once the pipeline's healthy)

1. Website page live first (gives email/SMS/GBP a link target).
2. New-this-month forfeitures → Email #1 ("Here for you").
3. Rolling pool enters the 3-month rotation: Email → SMS → Push+Email#2.
4. Always-on social + GBP run every month regardless of the direct touch.
5. Watch opt-out / unsubscribe rate the first 90 days — if it climbs, drop the rolling pool to every-other-month.
