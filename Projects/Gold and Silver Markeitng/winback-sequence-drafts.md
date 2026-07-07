# Valley Pawn — Dormant Subscriber Win-Back Sequence

**Audience:** "Dormant" segment (subscribed, on list 3, not blocklisted, no link click in 90 days) — ~8,000 contacts.
**Cadence:** Day 0 → Day 7 → Day 14.
**Build method:** Duplicate **VP Master Template (ID 11)** in Brevo, find-and-replace the 10 markers per email below.
**Primary CTA on all three:** `https://thevalleypawn.com/keep-in-touch` (a click here = re-engaged; auto-moves contact back to Engaged).
**Tracking:** distinct `utm_campaign` per email so the analytics job buckets them cleanly.

> After Email 3 sends, run the suppression sweep: anyone in Dormant who did NOT open or click
> across the 3 sends → add to "Dormant — Sunset" list, remove from list 3. Keeps the active
> list clean and protects domain reputation.

---

## EMAIL 1 — Day 0 — "We miss you" (warm, value-first, no hard ask)

| Marker | Value |
|---|---|
| `[[CAMPAIGN_SLUG]]` | `winback_01_miss_you_2026-06` |
| `[[HERO_EYEBROW]]` | `IT'S BEEN A WHILE` |
| `[[HERO_HEADLINE]]` | `We'd hate to lose touch` |
| `[[HERO_SUBLINE]]` | `It's been a minute since we've seen you — here's what's been happening at Valley Pawn, and a standing offer whenever you're ready.` |
| `[[PRIMARY_CTA_LABEL]]` | `Keep me in the loop` |
| `[[PRIMARY_CTA_URL]]` | `https://thevalleypawn.com/keep-in-touch` |
| `[[PRIMARY_CTA_SUB]]` | `One tap keeps the good stuff coming — deals, gold prices, and new arrivals.` |
| `[[SUBJECT_FALLBACK]]` | `We miss you at Valley Pawn` |

**Subject line:** `We miss you — still want deals from Valley Pawn?`
**Preheader:** `It's been a while. Here's what's new, and a 15% welcome-back offer.`

**`[[BODY_HTML]]`:**
```html
<p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#444;">Hey there —</p>
<p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#444;">We noticed it's been a while since you've opened one of our emails, and we get it — inboxes are crowded. But we'd genuinely hate to lose touch.</p>
<p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#444;">A lot has happened across the Valley. We're buying gold and silver at top dollar, our shelves turn over with new arrivals every week, and our 30-day warranty still stands behind everything we sell.</p>
<p style="margin:0 0 8px 0;font-size:16px;line-height:1.6;color:#444;"><strong>As a thank-you for sticking with us:</strong> show this email in any store this month for <strong>15% off</strong> anything you buy.</p>
<p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#444;">If you still want to hear from us — deals, gold prices, new finds — just tap the button below. That's all it takes.</p>
```

---

## EMAIL 2 — Day 7 — "Here's exactly what you're missing" (concrete value + offer)

| Marker | Value |
|---|---|
| `[[CAMPAIGN_SLUG]]` | `winback_02_whats_new_2026-06` |
| `[[HERO_EYEBROW]]` | `STILL HERE FOR YOU` |
| `[[HERO_HEADLINE]]` | `Here's what you've been missing` |
| `[[HERO_SUBLINE]]` | `Top-dollar gold buys, weekly deals across five stores, and free layaway — all a short drive away.` |
| `[[PRIMARY_CTA_LABEL]]` | `Yes, keep them coming` |
| `[[PRIMARY_CTA_URL]]` | `https://thevalleypawn.com/keep-in-touch` |
| `[[PRIMARY_CTA_SUB]]` | `Tap once and you'll stay on the list for deals and gold prices.` |
| `[[SUBJECT_FALLBACK]]` | `Here's what you've been missing at Valley Pawn` |

**Subject line:** `Gold's up, deals are in — here's what you've missed`
**Preheader:** `Top-dollar gold, weekly deals, free layaway. Still want in?`

**`[[BODY_HTML]]`:**
```html
<p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#444;">Still thinking it over? Here's what lands in our subscribers' inboxes every week:</p>
<ul style="margin:0 0 20px 0;padding-left:20px;font-size:16px;line-height:1.7;color:#444;">
  <li><strong>Top-dollar gold &amp; silver buys</strong> — we pay on the spot, prices move with the market.</li>
  <li><strong>This week's best deals</strong> — hand-picked finds, one from each of our five stores.</li>
  <li><strong>Free layaway</strong> — get what you want now, pay over time, no fees.</li>
  <li><strong>30-day warranty</strong> on everything we sell — most places won't do that.</li>
</ul>
<p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#444;">Your <strong>15% welcome-back offer</strong> is still good this month — just show this email at any store.</p>
<p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#444;">Want to keep getting these? One tap below and you're set.</p>
```

---

## EMAIL 3 — Day 14 — "Last one" (graceful permission ask)

| Marker | Value |
|---|---|
| `[[CAMPAIGN_SLUG]]` | `winback_03_last_call_2026-06` |
| `[[HERO_EYEBROW]]` | `ONE LAST NOTE` |
| `[[HERO_HEADLINE]]` | `Should we keep in touch?` |
| `[[HERO_SUBLINE]]` | `We don't want to crowd your inbox. If you'd still like to hear from us, just let us know — otherwise we'll quietly step back.` |
| `[[PRIMARY_CTA_LABEL]]` | `Yes — keep me subscribed` |
| `[[PRIMARY_CTA_URL]]` | `https://thevalleypawn.com/keep-in-touch` |
| `[[PRIMARY_CTA_SUB]]` | `No tap, no worries — we'll stop sending so we're not cluttering your inbox.` |
| `[[SUBJECT_FALLBACK]]` | `Should we keep in touch?` |

**Subject line:** `Last one — should we keep in touch?`
**Preheader:** `If we don't hear back, we'll quietly step away. One tap keeps us going.`

**`[[BODY_HTML]]`:**
```html
<p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#444;">This is the last email we'll send for a while — promise.</p>
<p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#444;">We'd love to keep sending you deals, gold prices, and new arrivals. But we only want to be in your inbox if you actually want us there.</p>
<p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#444;"><strong>If you'd like to stay on the list, just tap below.</strong> That single tap keeps everything coming. If we don't hear from you, we'll quietly stop sending — no hard feelings, and you're always welcome to walk into any of our five stores.</p>
<p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#444;">Either way — thank you for being part of the Valley Pawn family. What's Right Is Right.</p>
```

---

## Post-sequence sweep (run ~3 days after Email 3 matures)

1. Pull the Dormant segment members who did NOT click `/keep-in-touch` across the 3 sends.
2. Add them to a new list **"Dormant — Sunset"**.
3. Remove them from **list 3 (Valley Pawn Customers)**.
4. Going forward, the weekly newsletter targets **Engaged-90d**; list 3 remains the universe for reporting only.
5. Optional: one low-pressure "we're still here" email to the Sunset list around the holidays.
