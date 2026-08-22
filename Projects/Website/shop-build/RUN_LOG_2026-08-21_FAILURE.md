# vp-website-shop-nightly — run 2026-08-21 — FAILED at verification (Step 4)

## What happened
Scrape (sandbox bash curl, eBay /str/ storefront endpoint) and publish (WP Application Password
+ curl to /wp-json/wp/v2/pages/833) both completed successfully:

- Scraped 526 items across 5 stores, excluded 23 weapons-adjacent, published 503 items
  (Culpeper 310, Waynesboro 36, Harrisonburg 33, Lexington 23, Roanoke 101).
- POST to /wp-json/wp/v2/pages/833 returned HTTP 200, id=833, status=publish.
- Confirmed via REST GET (?context=edit) that page 833's stored content.raw is 483,220 bytes,
  contains the VP-SHOP-START marker, slug=shop, status=publish, modified=2026-08-21T11:05:37.
  **The publish itself is good and the content is correctly saved on the page.**

## Where it broke
Step 4 (live verification) failed: `curl https://thevalleypawn.com/shop/` returns 0 vp-card
elements and no VP-SHOP-START marker. The returned HTML's `<body>` class list is:
`archive post-type-archive post-type-archive-product ... woocommerce-shop woocommerce
woocommerce-page woocommerce-block-theme-has-button-styles ...`

This means **WooCommerce is now active on thevalleypawn.com** and has claimed the `/shop/` URL
for its own Product Archive template, which is rendering INSTEAD OF page 833's saved content.
Page 833 (slug "shop") is very likely the page WooCommerce auto-assigned as its
`woocommerce_shop_page_id` option when the plugin was activated/set up — WooCommerce overrides
normal page-template rendering for whatever page holds that role, regardless of the page's own
content.

This is NOT a bug in the scrape/publish pipeline — the pipeline did exactly what it has done
successfully on 8/5, 8/13, 8/15, and 8/18. Something changed on the WordPress site itself between
2026-08-18 (last successful verified run, 507 live cards) and today that introduced WooCommerce.
Nothing in Valley Pawn OS/CHANGELOG.md mentions this.

## Why I did not attempt a fix
Un-hijacking `/shop/` would require changing WooCommerce settings (e.g. reassigning
`woocommerce_shop_page_id` to a different/dummy page, or deactivating WooCommerce, or moving this
block to a different URL) — none of that is "additive," all of it touches site architecture I
don't have context on. WooCommerce may have been installed intentionally for a real storefront
project that supersedes this scraped-eBay-block approach entirely, in which case reverting it
would be wrong. This is a decision for Joshua, not a call to make unilaterally on a nightly cron
run.

## What the next session should do
1. Ask Joshua (or check for a WooCommerce-related task/note) why WooCommerce was installed and
   whether it's intentional / permanent.
2. If WooCommerce is NOT meant to own `/shop/`: reassign WooCommerce's Shop page setting
   (WooCommerce > Settings > Products > "Shop page") to a different/placeholder page, which will
   free `/shop/` back up for page 833's content with no further changes needed here — the content
   is already correctly saved.
3. If WooCommerce IS meant to own `/shop/` going forward: this whole scheduled task
   (vp-website-shop-nightly) needs to be redesigned — either publish the eBay inventory feed to a
   different URL (e.g. `/inventory/`), or feed it into WooCommerce as actual products via wc/v3
   REST API instead of a static HTML block on a page.
4. Do not re-attempt Steps 1-3 as-is until the /shop/ URL ownership question is resolved — they
   will keep succeeding (content saves fine) while Step 4 verification keeps failing (WooCommerce
   still renders over it).

## Artifacts from this run
- items.json (503 items, this run)
- shop-block.html / shop-block-wrapped.html (483KB, this run's built block)
- publish_payload.json / publish_response.json (HTTP 200, id 833)

---

## RESOLVED — 2026-08-21 (same day, interactive session)

Root cause was more specific than "WooCommerce claimed /shop/": `woocommerce_shop_page_id` pointed
at page **496, which no longer exists**. With an invalid shop page, WooCommerce falls back to the
literal `shop` slug for its product-archive rewrite, shadowing page 833.

Fix applied (all via REST, no wp-admin):
1. Created placeholder page **1110** (`/store-products/`, published) — its only job is to be the
   WooCommerce product-archive base. DO NOT DELETE page 1110 — deleting/orphaning it recreates
   this exact hijack.
2. `PUT wc/v3/settings/products/woocommerce_shop_page_id = 1110`.
3. Rewrite-flush gotcha: the option-update hook flushes rules DURING the same request, i.e. with
   the OLD slugs still registered — stale rules survive. The reliable path is saving the shop page
   itself (`POST wp/v2/pages/1110`), which queues WC's deferred flush; the next front-end request
   regenerates rules with correct slugs.
4. Verified: /shop/ renders VP-SHOP-START + vp-cards (503 items), no woocommerce-shop body class;
   /store-products/, /in-store-inventory/, /cart/, /checkout/ all healthy.

vp-website-shop-nightly needs NO changes — its Step 4 verification will pass on the next run.
