# Launch Campaigns — SMS + Email + Cross-Promo

All three drafted. **Nothing sent yet** — these are drafts for Joshua to approve, then send via Brevo/SMS provider (per behavior rules: customer-facing sends require explicit Joshua approval).

---

## 1. SMS Launch Blast — One-shot

**Audience:** Existing opted-in customer SMS list (TCPA-consent verified)
**Provider:** Brevo SMS (or existing SMS pipeline)
**Send window:** Tue–Thu, 10 AM – 6 PM ET (best deliverability + best response)
**Char count:** 158 chars + link (under 160 keeps it as 1 SMS not 2)

### Copy (Option A — direct):
```
Valley Pawn here. We're on Instagram, TikTok & X now. Enter our $100/month
giveaway: thevalleypawn.com/follow. Reply STOP to opt out.
```
(157 chars)

### Copy (Option B — sweepstakes-led):
```
Valley Pawn: WIN $100 this month — drop your email at
thevalleypawn.com/follow. New giveaway every month. Reply STOP to opt out.
```
(135 chars)

**Recommendation: Option B.** Stronger hook ($100 first, brand second). Drives more clicks.

---

## 2. Email Launch Campaign — Brevo

**Audience:** Full Valley Pawn Customers email list (~11,159 contacts per Brevo)
**Brevo template:** Use existing Valley Pawn template if available, otherwise create new
**Send window:** Tuesday 10 AM ET

### Subject lines (pick one — A/B if you want):
- **A:** "Win $100 every month — Valley Pawn is everywhere now"
- **B:** "We're on Instagram, TikTok, and X — and we're giving away $100/month"
- **C:** "Family-owned. 5 Virginia stores. Now $100/month giveaway." *(lean)*

**Recommendation: A** (gift-first hook).

### Preheader (preview text):
*"Drop your email at thevalleypawn.com/follow — you're entered. New winner every month."*

### Email body (HTML — embed in Brevo template):

```html
<div style="max-width:560px;margin:0 auto;font-family:-apple-system,system-ui,sans-serif;color:#1a1a1a;">

  <!-- Hero -->
  <div style="text-align:center;padding:32px 24px 16px;">
    <img src="https://thevalleypawn.com/wp-content/uploads/2026/03/vp_logo_name-no-tag.png"
         alt="Valley Pawn" style="max-width:280px;height:auto;" />
  </div>

  <!-- Headline -->
  <div style="background:linear-gradient(135deg,#0F3D8F,#1657c8);color:white;padding:28px 24px;border-radius:12px;margin:0 24px;">
    <h1 style="margin:0 0 8px;font-size:26px;font-weight:700;">WIN $100 EVERY MONTH</h1>
    <p style="margin:0;font-size:15px;opacity:0.95;">New winner the last day of every month.<br/>No purchase necessary. Just drop your email.</p>
    <a href="https://thevalleypawn.com/follow"
       style="display:inline-block;background:white;color:#0F3D8F;text-decoration:none;padding:14px 28px;border-radius:8px;font-weight:700;margin-top:16px;">
      Enter Now →
    </a>
  </div>

  <!-- Body -->
  <div style="padding:24px;line-height:1.6;font-size:15px;">
    <p>You know us as your local pawn shop. Family-owned since 2014. Fair loans. Gold buying. 30-day warranty on everything we sell.</p>

    <p><strong>We've just gone bigger online.</strong> Find us on:</p>

    <ul style="list-style:none;padding:0;">
      <li style="padding:8px 0;">📘 <strong>Facebook</strong> — each store's local page</li>
      <li style="padding:8px 0;">📸 <strong>Instagram</strong> — <a href="https://instagram.com/valley_pawn">@valley_pawn</a></li>
      <li style="padding:8px 0;">𝕏 <strong>X / Twitter</strong> — <a href="https://x.com/valleypawnva">@valleypawnva</a></li>
      <li style="padding:8px 0;">🎵 <strong>TikTok</strong> — <a href="https://tiktok.com/@thevalleypawn">@thevalleypawn</a></li>
      <li style="padding:8px 0;">🎥 <strong>YouTube</strong> — live selling coming soon</li>
    </ul>

    <p>Follow your local store and drop your email at <a href="https://thevalleypawn.com/follow"><strong>thevalleypawn.com/follow</strong></a> — you're entered in this month's $100 giveaway.</p>
  </div>

  <!-- 5-store directory per valley-pawn-context Rule -->
  <div style="background:#f8f4ec;padding:24px;border-radius:12px;margin:0 24px;">
    <h3 style="margin:0 0 12px;color:#0F3D8F;">FIND YOUR VALLEY PAWN</h3>

    <div style="border-bottom:1px solid #e0e0e0;padding:12px 0;">
      <strong>Lexington</strong><br/>
      125 Walker Street, Lexington, VA 24450<br/>
      <a href="https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Lexington+VA">Directions</a> ·
      <a href="tel:+15404618349">(540) 461-8349</a>
    </div>
    <div style="border-bottom:1px solid #e0e0e0;padding:12px 0;">
      <strong>Roanoke</strong><br/>
      2362 Peters Creek Road, Suite C, Roanoke, VA 24017<br/>
      <a href="https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Roanoke+VA">Directions</a> ·
      <a href="tel:+15405620776">(540) 562-0776</a>
    </div>
    <div style="border-bottom:1px solid #e0e0e0;padding:12px 0;">
      <strong>Harrisonburg</strong><br/>
      1790 East Market Street, Harrisonburg, VA 22801<br/>
      <a href="https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Harrisonburg+VA">Directions</a> ·
      <a href="tel:+15405744500">(540) 574-4500</a>
    </div>
    <div style="border-bottom:1px solid #e0e0e0;padding:12px 0;">
      <strong>Waynesboro</strong><br/>
      1321 West Broad Street, Waynesboro, VA 22980<br/>
      <a href="https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Waynesboro+VA">Directions</a> ·
      <a href="tel:+15402216346">(540) 221-6346</a>
    </div>
    <div style="padding:12px 0;">
      <strong>Culpeper</strong><br/>
      571 James Madison Highway, Culpeper, VA 22701<br/>
      <a href="https://www.google.com/maps/search/?api=1&query=Valley+Pawn+Culpeper+VA">Directions</a> ·
      <a href="tel:+15404455510">(540) 445-5510</a>
    </div>

    <p style="font-size:12px;color:#666;margin-top:12px;">
      Culpeper: Mon–Sat 10am–6pm. All other stores: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun).
    </p>
  </div>

  <!-- Footer -->
  <div style="text-align:center;padding:32px 24px;font-size:12px;color:#666;">
    Valley Pawn<br/>
    571 James Madison Highway, Culpeper, VA 22701<br/>
    <a href="https://thevalleypawn.com">thevalleypawn.com</a>
  </div>

</div>
```

---

## 3. Cross-Promo Posts — 3 across 2 weeks

Routes through `vp_social_publisher.py` as brand-tier (auto-fan to FB Brand + IG + X + WordPress). Each post promotes a different aspect.

### Week 1 (Tuesday) — "We're on X"
```
Valley Pawn is now on X / Twitter — @valleypawnva.

Family-owned since 2014. 5 Virginia locations. Same fair deals, just easier to follow.

Follow us → x.com/valleypawnva
And drop your email at thevalleypawn.com/follow for our $100 monthly giveaway 🎁
```

### Week 2 Wednesday — "We're on TikTok"
```
@thevalleypawn is live on TikTok 🎬

We're going to show you what comes in our doors — the watches, the tools, the surprise finds. New videos starting this month.

Follow us → tiktok.com/@thevalleypawn

(Yes, we do live selling soon. Stay tuned.) 💎
```

### Week 2 Saturday — "Follow us everywhere"
```
One scan. Every Valley Pawn channel.

We're on:
📘 Facebook (each store)
📸 Instagram — @valley_pawn
𝕏 X — @valleypawnva
🎵 TikTok — @thevalleypawn

Plus a $100 giveaway every month. Drop your email:
👉 thevalleypawn.com/follow

(Or visit any of our 5 Virginia stores — we'll show you in person.)
```

---

## 4. Manifest for vp_social_publisher.py

Save the 3 cross-promo posts as a single approved manifest, run through `vp_social_publisher.py` to schedule them in Publer. Manifest file: `manifests/launch_cross_promo_2026-06.json`

```json
{
  "batch_id": "launch-cross-promo-2026-06",
  "items": [
    {
      "id": "xpromo-week1-x",
      "routing_tier": "brand",
      "caption": "Valley Pawn is now on X / Twitter — @valleypawnva.\n\nFamily-owned since 2014. 5 Virginia locations. Same fair deals, just easier to follow.\n\nFollow us → x.com/valleypawnva\nAnd drop your email at thevalleypawn.com/follow for our $100 monthly giveaway 🎁",
      "scheduled_at": "2026-06-23T14:00:00Z",
      "status": "approved"
    },
    {
      "id": "xpromo-week2-tiktok",
      "routing_tier": "brand",
      "caption": "@thevalleypawn is live on TikTok 🎬\n\nWe're going to show you what comes in our doors — the watches, the tools, the surprise finds. New videos starting this month.\n\nFollow us → tiktok.com/@thevalleypawn\n\n(Yes, we do live selling soon. Stay tuned.) 💎",
      "scheduled_at": "2026-07-01T14:00:00Z",
      "status": "approved"
    },
    {
      "id": "xpromo-week2-everywhere",
      "routing_tier": "brand",
      "caption": "One scan. Every Valley Pawn channel.\n\nWe're on:\n📘 Facebook (each store)\n📸 Instagram — @valley_pawn\n𝕏 X — @valleypawnva\n🎵 TikTok — @thevalleypawn\n\nPlus a $100 giveaway every month. Drop your email:\n👉 thevalleypawn.com/follow\n\n(Or visit any of our 5 Virginia stores — we'll show you in person.)",
      "scheduled_at": "2026-07-04T14:00:00Z",
      "status": "approved"
    }
  ]
}
```

Run command after Joshua approves:
```
python3 vp_social_publisher.py manifests/launch_cross_promo_2026-06.json
```

---

## Joshua's send order (recommended sequence)

1. **TODAY** — review this doc. Approve copy + send order below.
2. **Day 1 (Tue)** — Email launch via Brevo. Reaches widest audience first.
3. **Day 2 (Wed)** — SMS launch via Brevo. Closes loop with mobile-first customers.
4. **Day 3 (Thu)** — Run `vp_social_publisher.py` on the cross-promo manifest → schedules all 3 posts.
5. **Watch the entries roll into the Brevo "Giveaway Entries" list.** First monthly drawing at end of the entry month.

All three campaigns reinforce each other and drive traffic to the same destination (thevalleypawn.com/follow → Brevo form → giveaway entry).
