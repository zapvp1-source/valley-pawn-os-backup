# Reactivation Sequence — 3-Email Drafts

Three emails, each duplicated from VP Master Template (Brevo ID 11) with the markers below.
Target audience: Dormant segment (will be built next). Cadence: Day 0, Day 7, Day 14.

The CTA URL on every reactivation email goes to a dedicated page — `https://thevalleypawn.com/keep-in-touch` — that's a "thanks, you're staying on the list" confirmation page. Clicking it both confirms re-engagement and adds the contact to an `Engaged-via-reactivation` segment (built off the URL pattern). If this page doesn't exist yet, I'll create it on WordPress as part of the build.

---

## Email 1 — Day 0 — "Still want us in your inbox?"

**Subject line:** Still want us in your inbox?
**Preheader:** It's been a while. Quick question for you.
**utm_campaign:** `reengagement_e1_2026-06`

**Markers:**

| Marker | Value |
|---|---|
| `[[CAMPAIGN_SLUG]]` | `reengagement_e1_2026-06` |
| `[[HERO_EYEBROW]]` | A QUICK CHECK-IN |
| `[[HERO_HEADLINE]]` | Still want us in your inbox? |
| `[[HERO_SUBLINE]]` | It's been a while since you opened or clicked anything from us. We get it — life moves fast. |
| `[[BODY_HTML]]` | (see below) |
| `[[PRIMARY_CTA_LABEL]]` | Yes — keep me in |
| `[[PRIMARY_CTA_URL]]` | `https://thevalleypawn.com/keep-in-touch` |
| `[[PRIMARY_CTA_SUB]]` | One click confirms — that's it. No form. |

**BODY_HTML:**

> Hey, it's Valley Pawn. Five family-owned stores across the Shenandoah Valley — Culpeper, Waynesboro, Harrisonburg, Lexington, and Roanoke — and a Joshua / Lainie team that actually reads replies to these emails.
>
> Here's why we're reaching out: we'd rather send fewer emails to people who actually want them than blast everyone every week. So we're checking in.
>
> If you still want loan tips, gold-and-silver price alerts, used-merchandise drops, and the occasional in-store deal — one click and you're locked in.
>
> If not, no hard feelings — you'll hear from us a couple more times, then we'll quietly stop.

---

## Email 2 — Day 7 — "Should we still be reaching out?"

**Subject line:** Should we still be reaching out?
**Preheader:** Last few before we update your preferences.
**utm_campaign:** `reengagement_e2_2026-06`

**Markers:**

| Marker | Value |
|---|---|
| `[[CAMPAIGN_SLUG]]` | `reengagement_e2_2026-06` |
| `[[HERO_EYEBROW]]` | CHECKING IN AGAIN |
| `[[HERO_HEADLINE]]` | Should we still be reaching out? |
| `[[HERO_SUBLINE]]` | We sent a note last week and didn't hear back. One more try before we adjust how often you hear from us. |
| `[[BODY_HTML]]` | (see below) |
| `[[PRIMARY_CTA_LABEL]]` | Keep sending — I'm in |
| `[[PRIMARY_CTA_URL]]` | `https://thevalleypawn.com/keep-in-touch` |
| `[[PRIMARY_CTA_SUB]]` | Or scroll down to update your preferences. |

**BODY_HTML:**

> Quick reminder what we actually do:
>
> **Pawn loans on anything of value** — up to $25,000, no credit check, no hit to your credit score. Cash same day.
>
> **We buy gold, silver, and coins** — paying near-spot. If you've got an old class ring in a drawer, we'll tell you what it's worth, no obligation.
>
> **Used merchandise** — tools, electronics, jewelry, instruments. Every single thing carries a 30-day warranty, which most pawn shops can't say.
>
> If any of that's useful to you, click below and we'll keep showing up in your inbox. If not, no hard feelings — you'll get one more from us next week, then we'll stop.
>
> Want fewer emails instead of none? Update your preferences and tell us what you actually want to hear about.

**Secondary CTA (below body):** `Update preferences` linking to Brevo's subscription-management page (Brevo auto-generates this URL per send — `{unsubscribe}` token gives them the preference center, not just unsub).

---

## Email 3 — Day 14 — "One more chance"

**Subject line:** Goodbye? Or one more chance?
**Preheader:** We'll stop emailing unless you click.
**utm_campaign:** `reengagement_e3_2026-06`

**Markers:**

| Marker | Value |
|---|---|
| `[[CAMPAIGN_SLUG]]` | `reengagement_e3_2026-06` |
| `[[HERO_EYEBROW]]` | LAST CALL |
| `[[HERO_HEADLINE]]` | One more chance to stay on the list |
| `[[HERO_SUBLINE]]` | This is the last one from us if we don't hear back. |
| `[[BODY_HTML]]` | (see below) |
| `[[PRIMARY_CTA_LABEL]]` | Keep me on the list |
| `[[PRIMARY_CTA_URL]]` | `https://thevalleypawn.com/keep-in-touch` |
| `[[PRIMARY_CTA_SUB]]` | One click is all it takes. |

**BODY_HTML:**

> We hate the idea of cluttering inboxes — especially with stuff people don't want. So we're keeping our word.
>
> This is the last email from Valley Pawn unless you click below. No tricks, no follow-ups.
>
> If you've ever bought, sold, pawned, or borrowed with us — or just plan to one day — keep us on the list. We'll be here when you need us.
>
> Five locations across the Valley. What's Right Is Right.
>
> — Joshua, Lainie & the Valley Pawn team

---

## Subject-line A/B alternative variants (optional, if we want to A/B)

If you want to A/B test Email 1, here are 3 alternatives:
- "Still want us in your inbox?" (baseline)
- "Quick favor?" (curiosity-driven)
- "Should we keep sending these?" (direct)

Industry data: curiosity-driven subject lines win ~60% of the time on reactivation, but the direct version converts at a higher quality (less click-bait drop-off). Recommend baseline + direct as the A/B if we test.

---

## What needs to happen on the WordPress side

Add a page at `https://thevalleypawn.com/keep-in-touch`:
- Simple content: "You're staying on the list. We'll be in touch."
- Optional: a quick "what do you want to hear about" preference selector (gold, loans, retail, app) — Phase 2-ish, not blocking.

I can either build that page directly via the WordPress REST API (same auth we use for the blog publisher) or via Chrome on the WP admin — your call. It's a 5-minute job either way.
