## 2026-08-22 (eBay channel in-depth audit — read-only, nothing changed on eBay)

- Full live audit of the eBay channel across all 5 store seller accounts via the Trading API.
  Read-only; no listing, price, policy, or setting was modified. Additive scripts + raw data in
  `Projects/eBay/audit_2026-08-22/`. Report: `Projects/eBay/eBay_Channel_Audit_2026-08-22.md`.
- **Baseline, trailing 90d (5/24–8/22):** 514 active listings / $83,441 listed value; 555 orders /
  $82,064 revenue; $13,617 eBay fees = 16.6% of item revenue (FVF $12,972 · Promoted Listings $314 ·
  international $123 · insertion $92 · return shipping $53). Per store rev/listing: Lexington $433,
  Waynesboro $361, Harrisonburg $359, Roanoke $173, **Culpeper $82**.
- **Two June-29 scorecard items are now CLOSED and should stop being re-raised:** all 5 stores carry an
  eBay Store subscription (insertion fees effectively $0 — $92 across 2,192 listings), and small-store
  listing depth is no longer the binding constraint.
- **Biggest finding — zero of 514 listings qualify for Top Rated Plus.** Handling time is 2 days (404
  listings) or 3 days (106); the requirement is same-day or 1 business day. Separately, all 469
  return-accepting listings are buyer-pays-return-shipping; the requirement is free returns. Both
  verified independently via `GetItem`. Worth $1,297/qtr ($5,189/yr) channel-wide; ~$3,587/yr net if
  applied selectively to listings >=$100. Culpeper and Waynesboro already hold Top Rated Seller status,
  so their share ($400 + $222/qtr) is immediately claimable.
- **Promoted Listings is effectively off:** $314.46 of ad fees in 90 days, all of it Culpeper. Roanoke,
  Waynesboro, Harrisonburg, Lexington are at $0.00 on $56,737 of sales. Flagged in the 2026-06-29
  scorecard, unchanged 8 weeks later. An unread 7/12 eBay message in the Roanoke inbox offers 50% off
  Promoted Listings.
- **Markdown engine has no terminal action.** `ebay_markdown_engine.py` works (283 items tracked, 182
  cut on Aug 1, 0 failures) but caps at 30% off after 3 cuts with nothing scheduled afterward. 154 items
  take their third cut on **2026-09-01** and then sit permanently. The `eBay Listing-Age Standard
  (Reprice & Pull)` policy's "pull" half is unenforced. Fix before Sep 1.
- **Other verified defects:** Best Offer switched OFF on 193 Culpeper listings ($15,372, no
  `BestOfferDetails` node at all); Roanoke 100% at 3-day handling + 14-day returns (only store not at 30
  days); 45 listings accept no returns ($10,932, 40 Culpeper); Lexington Below Standard as of 8/20 on a
  4.23% late-ship rate (re-eval Sep 20); avg 5.8 photos vs the 8-photo standard (71% below, Roanoke avg
  4.3); median 4 item specifics (34% at <=3); zero seller replies to the 3 open negative/neutral
  feedbacks, 2 of which cite description inaccuracy; 714 of 1,093 eBay messages unread over 60 days
  including 22 unread return/refund notices; 220 of 555 orders were sub-$50 for only $6,963 of revenue.
- **API scope gap from 2026-06-29 confirmed STILL OPEN.** `sell/marketing`, `sell/analytics`, and
  `sell/finances` all return HTTP 403 "Insufficient permissions" on all 5 accounts. Combined with
  `HitCount`/`WatchCount` returning 0 from Trading (deprecated), there is currently **no traffic,
  impression, or conversion data of any kind** for any listing. One OAuth re-authorization with those
  scopes unblocks Promoted Listings automation, all listing measurement, and automated fee reporting.
- **Security finding:** `~/ebay_weekly_rankings.py` hardcodes the Slack webhook, `APP_ID`, `DEV_ID`,
  `CERT_ID` and all 5 store OAuth tokens in plaintext (mode 701), and every other eBay script imports it
  to get credentials. The rest of the stack already moved to `~/.vp_secrets/`. Not yet remediated.
- **Rule 12 note — three candidate findings were discarded, not reported.** `GetSellerList` under-reports
  item specifics and descriptions; the first pass appeared to show zero item specifics, empty
  descriptions, and universal single-photo listings on all 514 listings. `GetItem` verification proved
  all three wrong. `quality_pull.json` (the first pull) is unreliable for those fields — use
  `quality_pull2.json` for handling/returns/photos and `fees_specs.json` for the verified 100-listing
  specifics sample.
