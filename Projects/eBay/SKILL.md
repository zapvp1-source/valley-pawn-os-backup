---
name: ebay-context
description: >
  Reference and operating manual for Valley Pawn's eBay store — the online sales channel for moving
  inventory beyond in-store retail, plus high-value items where eBay's national audience pays more than
  the local market. Use this skill ANY time a task touches eBay: creating or optimizing a listing,
  pricing an item, handling a Best Offer, processing a return or dispute, responding to a buyer message,
  checking sales/seller performance, running Promoted Listings, or coordinating shipping. Also use when
  Joshua says "list this on eBay," "post it online," "the eBay store," "an eBay buyer," "an eBay sale,"
  "we sold one on eBay," "optimize eBay," or any variation involving online resale of inventory. Pairs
  with `valley-pawn-context` (brand voice, warranty, categories) and `bravo-context` (where the inventory
  comes from). Even without explicit mention, if a task is about online sales, listing items, eBay fees,
  or eBay performance for Valley Pawn, consult this skill first.
---

# eBay — Online Sales Operating Reference

Operating manual for Valley Pawn's eBay channel. Jump to the relevant section using the Quick Map. Items marked **CONFIRM** are account-specific facts to verify on the next live eBay session and lock in here — everything else is policy/best-practice that applies now.

---

## Quick Map

| If you need to know... | Section |
|---|---|
| What eBay is to Valley Pawn, who runs it, the goals | Overview |
| Account, login, dashboards | Account & Access |
| What we sell / never sell | Categories |
| How we price and handle offers | Pricing & Offers |
| Title / photo / description / condition standards | Listing Standards |
| Shipping setup | Shipping |
| Returns and disputes | Returns & Disputes |
| Seller health metrics and targets | Performance |
| How eBay ties back to Bravo inventory | Inventory Reconciliation |
| Step-by-step workflows | Common Workflows |
| **How we grow sales, cut fees, protect reputation** | **Optimization Playbook** |

---

## Overview

- **Channel:** eBay — secondary sales channel. Two strategic jobs: (1) **clearance** — move aged inventory that isn't selling in-store, and (2) **premium reach** — list high-value or niche items where eBay's national buyer pool pays more than the local Shenandoah Valley market.
- **Brand standard:** eBay listings represent Valley Pawn. Apply the brand voice — warm, confident, honest ("What's Right Is Right") — and lean on the trust signals that differentiate us: licensed pawnbroker, fair/transparent dealing, and our 30-day warranty (see Returns & Disputes for how this maps to eBay's policy).
- **Owner / operator:** *(CONFIRM — Joshua directly? a designated employee at one store? rotated across stores? This determines who handles messages, packing, and the daily handling-time SLA.)*
- **Volume:** *(CONFIRM — listings/week and sales/month. Baseline this on first access.)*

### Goals (the reason this channel is being optimized)
1. **Sales** — more revenue: better listings, sharper pricing, Promoted Listings, and more aged Bravo inventory live.
2. **Cost** — protect margin: right subscription tier, tuned ad rates, Top Rated Seller fee discount, efficient shipping, fewer returns.
3. **Reputation** — hold Top Rated Seller status and strong feedback so search visibility and fee discounts compound.

---

## Account & Access

- **Structure: FIVE separate eBay accounts — one per store.** The channel is not a single store; it is five independent seller accounts, each with its own listings, feedback, seller level, fees, and subscription. Optimization and reporting must be done per-account and rolled up.
- **Confirmed account:** `valley_pawn_roanoke` (Roanoke). Login = store email (`Roanoke@fcfpawn.com`), per Preston's standardization (see `store-credentials` skill).
- **Logins:** 5 SEPARATE logins, username = `<city>@fcfpawn.com` (passwords in `store-credentials`). Claude cannot type passwords (security policy) — rely on Chrome saved-password autofill, or use the API path below.
- **API access (the real automation path):** eBay **Trading API** with per-store user tokens lives in `~/ebay_weekly_rankings.py` (app: `FullCirc-ValleyPa-PRD-...`). Pulls all 5 stores with no login. Companion `~/Desktop/ebay_account_health.py` (additive) pulls listing counts + store status. **Limitation:** these tokens lack analytics/marketing scope (403) — seller-standards and Promoted-Listings data need a one-time app re-auth with those scopes to automate.
- **Automations (all additive; never modify the rankings script):**
  - `ebay_weekly_rankings.py` — **Monday 9:30 AM** LaunchAgent → weekly sales rankings to Slack `#ebay-performance`. (Moved from 6 AM → 9:30 AM 2026-07-03 to land at store open; original plist backed up as `.bak-*` in `~/Library/LaunchAgents/`.)
  - `~/ebay_daily_listings.py` (HOME — not Desktop; Desktop is Google-Drive-synced and wiped the file) — **daily 1:30 PM** LaunchAgent `com.valleypawn.ebay-daily-listings` (plist in `~/Library/LaunchAgents/`) → posts per-store *new listings (prior day)*, total active listings, and total listed value to `#ebay-performance`, ranked by count then value. Logs to `~/ebay_daily_listings.log`/`.err`. Built 2026-06-30, relocated to home 2026-07-01. **Counts "listed yesterday" via `GetSellerList` filtered by StartTime — this includes items listed AND sold the same day (an active-list scan misses fast-sellers). Fixed 2026-07-03 after Chadd flagged Waynesboro undercount.** Run `--post` to send; no flag = dry run. Source-of-truth copy also in this eBay project folder.
  - `~/ebay_efficiency_weekly.py` — **Friday 3:30 PM** LaunchAgent `com.valleypawn.ebay-efficiency-weekly` (moved off Monday 2026-07-03 to spread the #ebay-performance cadence; late-afternoon own slot) → weekly efficiency scorecard to `#ebay-performance`: per-store + channel **sell-through % (30d), days-to-sell (median), aged inventory >90d ($ & % of active value), revenue/listing, and 7-day new-listing velocity**, ranked by sell-through. Days-to-sell maps sold ItemIDs to listing StartTime via GetSellerList (last 120d). Longer run (~90s) — fine under LaunchAgent. Built 2026-07-03. Source copy in this eBay project folder.
- **Confirmed per-store state (2026-06-29):** Active listings — Culpeper 286, Roanoke 197, Harrisonburg 48, Waynesboro 43, Lexington 42. eBay Store subscription — **only Culpeper** ("VP Culpeper"); Roanoke/Harrisonburg/Lexington/Waynesboro have none.
- **Login flow:** Chrome saved passwords. Per `valley-pawn-context` Rule #2, never ask Joshua to log in — navigate to eBay in Chrome and use saved credentials.
- **Seller Hub:** `https://www.ebay.com/sh/ovw` (Overview)
- **Key Seller Hub URLs:**
  - Performance dashboard: `https://www.ebay.com/sh/performance/dashboard`
  - Active listings: `https://www.ebay.com/sh/lst/active`
  - Sold: `https://www.ebay.com/sh/ord/sold` / Orders: `https://www.ebay.com/sh/ord`
  - Reports/Downloads: `https://www.ebay.com/sh/reports`
  - Promoted Listings: `https://www.ebay.com/sh/marketing`
  - Fees / financials: `https://www.ebay.com/sh/fin` (Payments → Reports)
- **Store subscription tier:** Roanoke = **NO Store subscription** (confirmed 2026-06-29) — paying standard (higher) final-value fees and no discounted-listing allotment. *(CONFIRM other 4. Likely the same. See Optimization Playbook → Cost — a Basic/Premium Store almost certainly pays for itself at this volume.)*
- **Payments:** eBay Managed Payments. *(CONFIRM the linked bank account on file.)*
- **eBay developer API:** eBay offers free Sell APIs (Inventory, Fulfillment, Marketing, Analytics) to sellers. Not currently wired into this workspace. *(OPPORTUNITY — registering a dev key + OAuth would enable true automation: bulk list from Bravo, pull metrics, adjust prices programmatically. Browser-driven Seller Hub is the interim method.)*

---

## Categories We Sell

Pawn inventory maps well to eBay's highest-velocity categories:

- **Jewelry & watches** — gold, silver, diamond, brand-name watches (strong eBay premium vs. local)
- **Electronics** — phones, tablets, laptops, gaming consoles, audio
- **Tools** — power tools and hand tools (brand-name move well)
- **Musical instruments**
- **Coins / bullion** — gold/silver coins and bars
- **Collectibles**

### NEVER list (compliance — non-negotiable)
- **Firearms, ammunition, and most weapons** — prohibited on eBay. The Roanoke store carries firearms in-store; **never** create firearm or ammo listings, and never reference them. (Mirrors the firearms rule in `valley-pawn-context`.)
- **eBay restricted/edge items** — certain knives, replicas, some electronics with locks/activation, recalled goods. Check eBay's prohibited-and-restricted list before listing anything weapons-adjacent or unusual.
- **Stolen-risk / un-cleared collateral** — only list items that have cleared the pawn hold period and are legitimately Valley Pawn's to sell, properly removed from active loan status in Bravo.

---

## Pricing & Offers

**Pricing method — benchmark against SOLD comps, not asking prices.** The single most common pricing mistake is pricing off active listings (what people *hope* to get). Always price off eBay's **completed/sold** listings:
- On eBay search, filter → "Sold items." Use the median of recent solds for the same make/model/condition.
- Default list price: **the sold-comp median**, adjusted for condition. For aged-inventory clearance, list at the lower quartile to move it; for premium/rare items, list at the upper quartile or run an auction.

- **Format:** Buy It Now is the default (predictable, supports Best Offer and Promoted Listings). Use **Auction** only for genuinely rare/collectible items or bullion where demand is hot and price discovery beats a fixed price.
- **Best Offer:** Enable on most fixed-price listings. Set **auto-accept** at ~90% of list and **auto-decline** at ~75% of list so the team only manually handles the middle band. *(CONFIRM final thresholds with Joshua; these are sensible starting points.)*
- **Floor:** Never let a Best Offer or markdown drop below cost basis (loan amount / acquisition cost + eBay fees + shipping). Pull cost basis from Bravo before accepting low offers.
- **Promotions:** Use **Markdown Manager** for time-boxed sales on aged stock and **Volume Pricing / coupons** to clear multiples. Tie clearance events to the same seasonal calendar as the in-store/email promos where it makes sense.

---

## Listing Standards

Consistency = trust + search ranking. eBay's Cassini search engine rewards complete, accurate, well-photographed listings with item specifics filled in.

### Title (80 characters — use them all)
Formula: **Brand + Model + Key Spec(s) + Type + Condition keyword.**
- Front-load the words buyers actually search. No filler ("L@@K", "WOW"), no ALL-CAPS spam, no punctuation runs.
- Example: `Apple iPhone 13 128GB Blue Unlocked A2482 Very Good — Tested & Warrantied`
- Example: `DeWalt DCD771 20V MAX Cordless Drill Driver + Battery & Charger — Works Great`

### Photos (the conversion lever)
- **Minimum 8–12 photos**, more for high-value. eBay allows 24 free.
- Clean, uncluttered background (white/neutral lightbox preferred), good lighting, multiple angles, screen-on shots for electronics, and **close-ups of every flaw** (scratches, wear) — honest flaw photos cut "not as described" returns dramatically.
- Include shots of included accessories and any serial/model plate.
- *(CONFIRM photo workflow — taken at which store? Shared lightbox? Phone vs. DSLR?)*

### Description
- Lead with condition and what's included, then specs, then the trust block.
- **Trust block (use on every listing):** "Sold by Valley Pawn, a licensed Virginia pawnbroker in business since 2014. Every item is inspected and tested. Backed by our 30-day warranty." (See Returns for how this maps to eBay return settings.)
- Plain, scannable formatting. No phone numbers, no off-eBay contact info, no links off-platform (eBay policy violation).
- Disclose all flaws in text as well as photos.

### Item specifics (do not skip)
Fill in **every** item specific eBay offers for the category (Brand, Model, MPN, Storage, Color, Metal, Ring Size, Carat, etc.). Cassini uses these for search matching and filters — incomplete specifics is the #1 silent reason good items don't get seen.

### Condition grading (consistent rubric)
Use eBay's condition tiers honestly: New, Open Box, Certified/Manufacturer Refurbished, Used, For Parts/Not Working. For "Used," add a sub-grade in the description: **Excellent / Good / Acceptable**, with the photos to back it up. Over-grading drives returns and defects; under-grading leaves money on the table — match the grade to the flaw photos.

---

## Shipping

- **Carriers:** USPS for small/light and most jewelry/electronics; UPS/FedEx for heavier tools. Buy labels through eBay for the discounted rates and automatic tracking upload (protects late-shipment metric and Top Rated status). *(CONFIRM preferred carriers.)*
- **Handling time:** Target **same-day or 1 business day.** Fast handling is both a Top-Rated requirement and a search-ranking boost. *(CONFIRM the SLA the operator can actually hit.)*
- **Who packs/ships and from where:** *(CONFIRM — centralized at one store, or whichever store holds the item? This affects handling time and packaging stock.)*
- **Cost model:** **Free shipping built into price** for most items under a few pounds (buyers filter for it and it ranks better); **calculated shipping** for heavy tools so we don't eat oversized freight.
- **High-value items:** Require **signature confirmation** and adequate insurance for jewelry/watches/bullion over the eBay/carrier threshold — protects against Item Not Received fraud.
- **International:** Use eBay International Shipping (eBay handles customs/forwarding and shifts INR risk off us). *(CONFIRM whether we ship internationally.)*
- **Packaging:** Bubble mailers, boxes, void fill — stock via Amazon Business. Right-size packaging to avoid dimensional-weight overcharges.

---

## Returns & Disputes

- **Return policy:** Offer **30-day returns** on eBay — this aligns with Valley Pawn's 30-day warranty promise AND gives the listing a Top-Rated-Seller eligibility boost and better search placement. *(CONFIRM whether buyer or seller pays return shipping; "buyer pays" is fine and still TRS-eligible, but free 30-day returns ranks best. Decide per Joshua.)*
- **Warranty framing:** Our in-store 30-day warranty is delivered on eBay *through* the 30-day return window — say "30-day warranty / returns" in the description rather than promising a separate process eBay can't enforce.
- **Authenticity Guarantee:** eBay auto-authenticates certain categories (many watches, sneakers, some jewelry, trading cards) — items route through eBay's authenticator before reaching the buyer. Know which of our listings fall under it; it builds buyer confidence on high-value watches/jewelry.
- **Dispute handling:**
  - *Item Not as Described (INAD):* Accept the return, refund on receipt, inspect, and relist or restock in Bravo. Prevention (honest photos/grading) is the real fix — track INAD reasons to find listing-quality gaps.
  - *Item Not Received (INR):* Tracking + (for high-value) signature confirmation is the defense. If tracking shows delivered, escalate to eBay with proof.
  - *Never* let a case close "without seller resolution" — that directly damages the Performance metric. Resolve proactively.
- **Feedback:** Reach out to resolve before a buyer leaves negative feedback. Respond professionally and briefly to any negative that does post (future buyers read responses).

---

## Performance (seller health — protect this)

Check **Seller Hub → Performance dashboard** weekly. Targets:

| Metric | Target | Why |
|---|---|---|
| Seller level | **Top Rated** (or Above Standard min.) | Fee discount + search boost + TRS badge |
| Transaction defect rate | < 0.5% | Below Standard = visibility + fee penalties |
| Cases closed without seller resolution | < 0.3% | Direct path to Below Standard |
| Late shipment rate | < 3% | Buy labels via eBay + fast handling protects this |
| Valid tracking uploaded on time | high % | Required for TRS; auto-handled by eBay labels |

**Top Rated Seller requirements (US):** meet the defect/late/case thresholds, plus minimums on transactions and $ volume over the trailing period, same-/1-day handling with tracking, and a 30-day return policy. Hitting TRS unlocks the **final-value-fee discount** and the **Top Rated Plus** search badge — this is the highest-leverage single status for both cost and sales.

---

## Inventory Reconciliation with Bravo

When an item sells on eBay it MUST come out of in-store availability in Bravo so the counter can't sell the same unit. Returns must go back in.

*(CONFIRM the actual process and lock it here — until then, the rule is:)*
- **Listing:** When an item is moved to eBay, mark it in Bravo so the in-store team doesn't sell it (dedicated location/status for "eBay hold" — *CONFIRM the exact Bravo status/location used*).
- **Sale:** When an eBay order closes, remove/sell-out the item in Bravo same day.
- **Return:** When an eBay return is received and passes inspection, restock it in Bravo (back to its store/location) and relist on eBay or move to in-store.
- **Owner of this step:** *(CONFIRM who reconciles — must be unambiguous to prevent double-sells.)*
- See `bravo-context` for where the inventory lives and how to pull cost basis / aged-inventory candidates.

---

## Common Workflows

### List an item from Bravo inventory
1. Confirm it's clear to sell (loan period elapsed, not on active hold) and pull cost basis from Bravo.
2. Photograph per Listing Standards (8–12, flaws included).
3. Seller Hub → Create listing (or **Sell Similar** off an existing comparable listing to reuse the template — big time saver).
4. Title (80 char formula) → category → **all item specifics** → condition + sub-grade → description with trust block → sold-comp-based price + Best Offer thresholds → 30-day returns → shipping.
5. Add **Promoted Listings** (see Optimization) at the suggested-or-slightly-below ad rate.
6. Publish, then mark the item "on eBay" in Bravo.

### Respond to a buyer message
- SLA: reply within **24 hours** (eBay tracks response time). Brand voice, helpful, no off-platform contact. Templates: shipping-time questions, condition clarifications, offer negotiation, return requests.

### Handle a Best Offer
- Auto-accept ≥ ~90% of list, auto-decline ≤ ~75%, counter the middle — never below cost-basis floor. *(CONFIRM thresholds.)*

### Process a return
Accept → eBay return label → receive → inspect → refund → relist or restock in Bravo.

### Pull a sales / fee report
Seller Hub → Reports (`/sh/reports`) and Payments → Reports (`/sh/fin`). Fields we care about: item, sale price, final value fee, promoted-listing fee, shipping cost, net payout, sell-through, days-to-sell.

### Bulk-list similar items
Use **Sell Similar** + eBay bulk-listing tools / a listing template for batches of like items (e.g., a lot of similar tools or phones).

---

## Optimization Playbook

The working plan for the three goals. Phase 0 (baseline) comes first — most levers need real numbers to prioritize.

### Phase 0 — Baseline (do first, every optimization cycle)
Pull and record: active listing count, last-90-day sold vs. unsold (sell-through %), final-value + promoted-listing fees as a % of sales, current seller level and the five Performance metrics, store subscription tier, and the aged listings sitting unsold > 60/90 days. This becomes the scorecard everything else is measured against — and fills the **CONFIRM** fields above.

### Sales (grow revenue)
1. **Listing quality pass** — titles using the full 80 chars, 8–12 photos with flaw shots, and **complete item specifics** on every active listing. This is the cheapest, highest-ROI lever (free, and directly drives Cassini ranking).
2. **Re-price off sold comps** — audit active listings against current sold medians; cut over-priced laggards, nudge under-priced winners.
3. **Promoted Listings (Standard)** — eBay's pay-per-sale ads; only charged when the item sells via the ad. Start at or just below eBay's suggested ad rate, then tune by category using the campaign report. Biggest single visibility lever.
4. **More inventory live** — systematically list aged Bravo stock (pull aged-inventory candidates via `bravo-context`). More quality SKUs = more funnel.
5. **Markdown events & coupons** — clear slow movers; align with seasonal calendar.

### Cost (protect margin)
1. **Right-size the store subscription** — match tier (Basic/Premium/Anchor) to actual listing volume; the higher tiers lower per-listing and final-value fees once volume justifies them. Recompute after Phase 0.
2. **Tune Promoted Listings ad rate** — most sellers overpay. Use the campaign report to find the rate that wins placement without giving away margin; lower rates on items that already sell well organically.
3. **Earn/keep Top Rated Seller** — the final-value-fee discount is effectively free margin; protecting the seller metrics pays for itself.
4. **Shipping efficiency** — calculated rates on heavy items, right-sized packaging to dodge dimensional-weight fees, eBay-purchased labels for the discount.
5. **Cut returns** — honest photos/grading reduce INAD refunds (refunds cost the item's margin plus return shipping). Track INAD reasons and fix the listing patterns behind them.

### Reputation
1. **Hold the Performance metrics** in the table above — they gate both visibility and fees.
2. **Fast handling + tracking** — same/next-day, eBay labels auto-upload tracking.
3. **24-hour message replies** and proactive issue resolution before feedback posts.
4. **Respond to any negative feedback** professionally — future buyers read it.

### Phase 2 (secondary — website integration)
Surface Bravo + eBay inventory for purchase on `thevalleypawn.com`. This is a real integration project (Bravo inventory feed → website store, plus keeping eBay/website/in-store stock in sync to avoid oversells). Worth doing **after** eBay is tuned. Scope it separately when ready.

---

## Companion Skills
- **`bravo-context`** — where eBay inventory actually lives; source of cost basis and aged-inventory candidates; the reconciliation counterpart.
- **`valley-pawn-context`** — brand voice ("What's Right Is Right"), 30-day warranty, categories, the no-firearms rule, and Rule #2 (never ask Joshua to log in).

---

## How to Extend This Skill
Resolve the **CONFIRM** items on the next live eBay session (start with account/store name, subscription tier, operator, and the Bravo reconciliation status). Each resolved item makes more of the Optimization Playbook automatable — and registering the eBay Sell API key (noted under Account & Access) would unlock end-to-end automation of listing, pricing, and reporting.
