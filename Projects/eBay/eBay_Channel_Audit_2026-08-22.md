# Valley Pawn eBay Channel — In-Depth Audit

**Date:** 2026-08-22 · **Window:** trailing 90 days (2026-05-24 → 2026-08-22)
**Method:** live eBay Trading API pull against all 5 store accounts (read-only, additive scripts in
`eBay/audit_2026-08-22/`). Nothing on eBay was changed. Every headline number below was verified a
second time against `GetItem` on live listings before being reported — three candidate findings were
discarded as parsing artifacts, not reported.

---

## The channel today

| Store | Active | Listed value | Orders 90d | Rev 90d | Rev/listing | Aged >90d | Aged $ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Culpeper | 307 | $47,077 | 226 | $25,328 | **$82** | **147** | **$21,573** |
| Roanoke | 106 | $11,939 | 138 | $18,384 | $173 | 37 | $4,003 |
| Waynesboro | 39 | $13,305 | 68 | $14,071 | $361 | 0 | $0 |
| Harrisonburg | 35 | $7,002 | 63 | $12,579 | $359 | 13 | $702 |
| Lexington | 27 | $4,119 | 60 | $11,703 | **$433** | 10 | $978 |
| **Channel** | **514** | **$83,441** | **555** | **$82,064** | **$160** | **207** | **$27,255** |

**Fees paid, 90 days — $13,617 (16.6% of item revenue):**
Final value fees $12,972 · Promoted Listings $314 · international $123 · insertion $92 ·
return shipping $53.

Two things the June 29 scorecard flagged are now **fixed** and should come off the list: all 5 stores
carry an eBay Store subscription (insertion fees are effectively $0 — $92 across 2,192 listings), and
the small stores' listing counts are no longer the binding constraint. Lexington turns 27 listings into
$11,703; Culpeper needs 307 to make $25,328.

---

## Findings, ranked by money

### 1. Not one of 514 listings qualifies for Top Rated Plus — $3,600–5,200/yr
The 10% final-value-fee discount requires **same-day or 1-business-day handling** AND **30-day or longer
free returns**. Current state, verified on live listings:

- Handling time: 404 listings at 2 days, 106 at 3 days. **Zero at 1 day or same day.**
- Return shipping: all 469 listings that accept returns are set to **buyer pays**. Free returns is the
  requirement; 30-day-buyer-pays does not qualify.

Culpeper and Waynesboro already hold Top Rated Seller status, so their share is claimable immediately —
$400 + $222 per quarter. Channel-wide if all five qualify: **$1,297/quarter, $5,189/yr.**

Free returns costs something. At a 5% return rate (Lexington's measured rate) that's ~28 returns per
quarter at ~$12 a label = ~$333/quarter against $1,297 of savings. **Applying it only to listings ≥$100
captures 81% of the revenue and nets ~$3,587/yr with a fraction of the return exposure.**

⚠️ Sequence matters: Lexington is already Below Standard on late shipments (4.23%). Tightening handling
to 1 day before the shipping discipline is fixed makes that worse, not better. Fix ship-out first, then
flip the setting.

### 2. Promoted Listings is effectively off — the single biggest untapped visibility lever
$314.46 of ad fees in 90 days, **all of it Culpeper**. Roanoke, Waynesboro, Harrisonburg, Lexington:
**$0.00.** This was called out in the June 29 scorecard and has not moved in eight weeks.

Sitting unread in the Roanoke eBay inbox since 7/12: *"Exclusive offer: 50% off Promoted Listings with a
priority strategy."*

For reference, the four unpromoted stores did $56,737 in 90 days. Promoted Listings is pay-per-sale —
it only charges when the ad produces the sale, so the downside is bounded by the ad rate you set.

### 3. Culpeper is carrying 60% of the catalog and 46% of it is dead
- 147 of 307 listings are older than 90 days, worth **$21,573 — 46% of Culpeper's listed value**
- 16 listings older than **365 days**
- $82 revenue per listing vs. $359–433 at the three small stores

The auto-markdown engine (10% per month, hard stop at 30% off) is working — 283 items tracked, 182 cut on
Aug 1, zero failures. But **it has no terminal action.** 154 items take their third and final cut on
**September 1** and then sit at 30% off forever with nothing scheduled to touch them again. The
*eBay Listing-Age Standard (Reprice & Pull)* policy exists on paper; nothing enforces the "pull" half.

### 4. Best Offer is switched off on 193 Culpeper listings — $15,372 of inventory
Confirmed by direct `GetItem` (no `BestOfferDetails` node at all — genuinely off, not a reporting gap).
Every other store runs Best Offer on 100% of listings. Culpeper is the store with the worst aging, and
it's the only one that has the negotiation lever disabled.

### 5. Roanoke is the worst-configured store and the second-biggest seller
All 106 listings: **3-day handling** (worst in the channel) and **14-day returns** (only store not at 30
days). Both settings disqualify it from Top Rated Plus twice over, and 14-day returns costs conversion
against sellers offering 30. $18,384 in 90 days is running through the channel's weakest configuration.

### 6. 45 listings accept no returns at all — $10,932
40 of them Culpeper ($10,438), plus 3 Roanoke, 1 Harrisonburg, 1 Lexington. No-returns suppresses
conversion, blocks Top Rated eligibility, and on eBay it doesn't actually stop a determined buyer from
opening a not-as-described case — it just removes our control of the outcome.

### 7. Lexington is Below Standard — search demotion in effect now
As of Aug 20: Below Standard, driven by a **4.23% late shipment rate** (9 of 213) against a 3% ceiling.
Also 2 cases closed without seller resolution and a 5.12% return rate. Next evaluation **Sep 20** — it
would pass today, but "would pass today" is not the same as passing. Worst return categories: Cameras &
Photo (33.3%), Collectibles (18.2%), Business & Industrial (18.2%).

### 8. Listing quality is below the standard we already wrote down
Measured against `ebay-context`'s own targets, on a verified 100-listing sample plus full-catalog photo
counts:

| Standard | Target | Actual |
|---|---|---|
| Photos per listing | 8–12 | **avg 5.8** — 367 of 514 (71%) below 8; Roanoke avg 4.3 |
| Item specifics | every field eBay offers | **median 4** — 34% have ≤3, 61% have ≤5 |
| Title length | use all 80 chars | avg 63 — 155 listings under 60 chars |

Real examples: a $1,200-class Epiphone Explorer with 2 specifics (Brand, Model). A Nintendo Wii console
with 2. A Snap-On cordless ratchet with 2. Item specifics are what Cassini filters on — a buyer narrowing
by "Body Material" or "Storage Capacity" never sees these listings at all.

### 9. Nobody has replied to a single piece of negative feedback
Three negatives/neutrals in the window, **zero seller responses** — and future buyers read those. Worse,
the causes are all self-inflicted:

- Harrisonburg 7/8 (neutral): *"only complaint is the lack of charger when the description claimed"*
- Lexington 4/10 (negative): *"Seller wrote complete set in the listing header yet it only came with an extra white queen no black queen"*
- Roanoke 5/24 (neutral): *"Buckle was loose. Messaged seller but no response was given. Had it repaired at my cost."*

Two are description accuracy — the same root cause as the title/photo audit backlog cleaned up on 8/21.
One is an unanswered buyer message.

### 10. The eBay message centre is unmonitored — 714 unread over 60 days
Roanoke 485 unread of 597, Waynesboro 136 of 193, Lexington 74 of 153. Best Offers are **not** being lost
(only 3 pending right now and counteroffers are actively going out, so the team is working them through
Seller Hub) — but **22 return/refund notifications are unread**, and unwatched return notices are exactly
how a case closes without seller resolution. Lexington already has 2.

### 11. 40% of orders produce 8.5% of revenue
220 of 555 orders were under $50, generating $6,963. Each one still costs a photo session, a listing, a
pack, a label, a $0.40 per-order fee, and a slot in the same-day ship queue that's driving the late
shipment rate. Culpeper alone did 136 of them for $4,048.

### 12. The API scope gap from June 29 is still open — it's now the ceiling on everything else
Verified today: Marketing, Analytics, and Finances REST endpoints all return **403 Insufficient
permissions** on all 5 accounts. Consequences:

- No automated Promoted Listings management — campaigns can only be run by hand in the browser
- **No traffic data at all.** `HitCount` and `WatchCount` return 0 from the Trading API (deprecated), and
  the Analytics API is blocked. We cannot currently measure impressions, click-through, or conversion on
  any listing. Every listing-quality decision is being made blind.
- No automated fee reporting — the fee numbers in this report had to be reconstructed from
  `GetAccount` invoice entries

A single one-time OAuth re-authorization with `sell.marketing`, `sell.analytics`, and `sell.finances`
scopes fixes all three and makes this entire audit a scheduled report instead of a project.

### 13. Security: all five store tokens are sitting in plaintext
`~/ebay_weekly_rankings.py` hardcodes the Slack webhook, `APP_ID`, `DEV_ID`, `CERT_ID`, and all five store
OAuth tokens — and every other eBay script imports the file to get them. The rest of the stack already
moved to `~/.vp_secrets/`. This one didn't, and it's the file everything depends on.

---

## What to do, in order

| # | Action | Impact | Effort | Decision |
|---|---|---|---|---|
| 1 | Turn Best Offer on for 193 Culpeper listings | $15,372 of stuck inventory gets a negotiation path | 1 script run | Mine |
| 2 | Roanoke → 30-day returns (from 14) on all 106 listings | Conversion + TRS eligibility | 1 script run | Mine |
| 3 | Fix the 45 no-returns listings → 30-day returns | $10,932, conversion, TRS gate | 1 script run | Mine |
| 4 | Terminal action for max-markdown items **before Sep 1** | Stops 154 items becoming permanent shelf-warmers | Build + policy | Mine, per policy |
| 5 | Reply to all 3 open negative/neutral feedbacks | Reputation, visible to every future buyer | 20 min | Mine |
| 6 | Item specifics + photo fill-in pass, ≥$100 listings first | Cassini ranking — the free lever | Ongoing/automated | Mine |
| 7 | eBay OAuth re-auth with marketing/analytics/finances scopes | Unblocks #8, #9 and all future measurement | One browser session | **Yours** (account owner) |
| 8 | Promoted Listings on the 4 dark stores, low ad rate | Biggest visibility lever; $56.7K/90d currently unpromoted | After #7 | **Yours** (ad budget) |
| 9 | Ship discipline → then 1-day handling + free returns ≥$100 | ~$3,587/yr fee savings + TRS Plus seal | Ops change | **Yours** (ops policy) |
| 10 | Move `ebay_weekly_rankings.py` secrets to `~/.vp_secrets/` | Removes plaintext tokens | 30 min | Mine |
| 11 | Raise Culpeper's intake floor (sub-$50 items) | Frees the ship queue that's causing late shipments | Policy | **Yours** |

Items 1–6 and 10 I can execute without you. Items 7–9 and 11 are yours: one is a login only you can do,
two commit recurring money or an ops standard, one is a merchandising policy call.

---

## Method notes / honesty

- All figures pulled live from the eBay Trading API on 2026-08-22 against all 5 seller accounts.
- Fee figures reconstructed from `GetAccount` invoice entries over the same 90-day window, deduplicated.
- FVF % is expressed against **item revenue only**; eBay charges FVF on item + shipping, so the true
  effective rate on gross is lower than 15.8%.
- Item-specifics and photo counts verified against `GetItem` on a 100-listing random sample after
  `GetSellerList` was found to under-report them. Three findings drawn from the unverified data
  (zero item specifics, empty descriptions, universal 1-photo listings) were **wrong and discarded**.
- Seller-level and return-rate figures for Lexington come from the 2026-08-21 `monthly-ebay-ratings-sweep`
  seller dashboard, the only account reachable that run. The other four stores' seller dashboards remain
  unpulled — that gap is a known defect in the monthly sweep and should be fixed on its next run.
- Not measured, because the API scope blocks it: impressions, click-through rate, conversion rate,
  search placement, per-listing views.
