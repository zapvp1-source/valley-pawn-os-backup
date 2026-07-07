# Valley Pawn eBay — 5-Store Channel Scorecard & Plan

**Pulled:** 2026-06-29 · **Method:** existing eBay Trading-API tokens (via new additive `ebay_account_health.py`) for listings + store status; Slack **#ebay-performance** for sales; browser for Roanoke seller health. No logins, no changes to the live rankings automation.

---

## The channel at a glance

| Store | Active listings | June MTD sales | Orders (MTD) | eBay Store sub? | Seller level |
|---|---:|---:|---:|---|---|
| Culpeper | **286** | $5,409 | 59 | ✅ "VP Culpeper" | not pulled* |
| Roanoke | 197 | $4,378 | 34 | ❌ none | Above Standard |
| Harrisonburg | 48 | **$5,673** | 28 | ❌ none | not pulled* |
| Lexington | 42 | $3,279 | 22 | ❌ none | not pulled* |
| Waynesboro | 43 | $2,253 | 24 | ❌ none | not pulled* |
| **Channel** | **616** | **$20,992** | **167** | 1 of 5 | — |

May full month (all 5): **$17,160 / 109 orders.** June is pacing well ahead. Avg order ~$125. Returns near-zero (quality is good).

\* Seller level/Top-Rated + defect rate couldn't be pulled by API — the existing tokens lack the analytics scope (403). Only Roanoke was read via browser. See "Gaps."

---

## What the data shows

**1. Listings are wildly uneven — and that's the biggest sales lever.**
Culpeper (286) and Roanoke (197) carry the catalog; Harrisonburg, Lexington, and Waynesboro sit at ~42–48. Yet **Harrisonburg turns just 48 listings into the #1 sales month ($5,673)** — the best sell-through in the channel. The three low-listing stores are starving the funnel. This is exactly the "listing velocity" problem you've been pushing in #ebay-performance ("Boro needs work"), now quantified: if Harrisonburg/Lexington/Waynesboro built toward Culpeper's listing depth, channel sales would step up materially.

**2. Only 1 of 5 stores has an eBay Store subscription.**
Culpeper has one ("VP Culpeper"); Roanoke, Harrisonburg, Lexington, Waynesboro do **not** (eBay error 13003 confirmed). No subscription = standard (higher) final-value fees on every sale. Harrisonburg and Roanoke especially — both doing $4–6K/mo with no Store — are the clearest candidates where a Basic/Premium Store likely pays for itself.

**3. Promoted Listings appears unused.**
Confirmed off for Roanoke (0 ad spend/sales, 11K views). Not yet checked for the others (needs Marketing-API scope or a browser look), but if it mirrors Roanoke, turning it on is the fastest visibility lever channel-wide. A 30%-off Promoted offer was expiring 6/30 on Roanoke.

**4. Reputation (Roanoke proxy):** Above Standard, not Top Rated — blocked by defect rate (0.93%), 2 unresolved cases, and weak tracking-upload (76.74%). Worth checking the same three metrics on the other four.

---

## Prioritized plan (channel-wide)

### Biggest win — listing velocity at the 3 small stores
Harrisonburg, Lexington, Waynesboro (~42–48 listings each) should be ramping toward Culpeper's depth. Harrisonburg's sell-through proves the demand is there. This is an ops/staffing push you already own — I can support it with a **per-store listing-count + listings-added tracker** (extend the same API script) so the weekly #ebay-performance post shows not just sales but *listings added* per store, making the velocity goal visible and accountable.

### Cost — add eBay Store subscriptions where they pay for themselves
Run the fee math for the 4 stores without a Store (start with Roanoke + Harrisonburg). At $4–6K/mo each, a Basic/Premium Store's lower final-value fees very likely beats the monthly cost. **Your call (recurring spend).**

### Sales — turn on Promoted Listings
Confirm status on the other 4; activate modest pay-per-sale campaigns on top-viewed listings channel-wide. **Your call (ad budget).**

### Reputation — push toward Top Rated
Tighten handling/tracking discipline (buy labels through eBay so tracking auto-uploads) and resolve cases before they close against us. Pull the seller-standards for all 5 once we add analytics scope.

---

## Gaps / follow-ups (honest)
- **Seller standards for 4 stores** + **Promoted Listings for 4 stores** need either a one-time eBay app re-authorization with analytics + marketing scopes (then fully automatable), or a quick browser pass. Recommend the scope upgrade — it makes this whole scorecard a repeatable automated report.
- The new `ebay_account_health.py` lives on the Desktop alongside the rankings script (additive; the live automation is untouched). It currently pulls listing counts + store status reliably.

## Phase 2 (secondary, per your note)
Surface Bravo + eBay inventory for purchase on thevalleypawn.com — real integration project, scoped after the channel is tuned.
