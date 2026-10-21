# thevalleypawn.com — Full Audit + Fixes (2026-10-20)

Data: GA4 + Search Console, 90 days (7/22–10/19) vs prior 90; live crawl; Lighthouse mobile before/after.
Backups of every touched object: `backups_pre/` (all 123 pages/posts, header, footer, nav, single template, Yoast meta).

## Scoreboard (90 days)
- Sessions 6,019 (+25%). Organic search 63% of traffic. Mobile 73% of sessions, 90% of calls.
- Phone clicks 722 · texts 82 · directions 92. **89% of all phone clicks happen on the homepage.**
- Search: 3,077 clicks / 95,070 impressions, CTR 3.2%, avg position 7.8 (was 8.7).
- Real form leads: **0.** All 70 "form_submit" events were the WooCommerce login/lost-password forms (bot noise; zero customer accounts exist).
- WooCommerce has never taken an order; every /shop/ item links to eBay.

## What's good
Click-to-call/text on every page with the store-aware sticky bar; clean schema (0 broken JSON-LD); SEO score 100;
location pages 1,100+ words with real ratings; $25K / hours consistent; #1 for "valley pawn {city}" and "pawn shop {city}" in 4 of 5 markets.

## What was bad → fixed today (verified live)
| # | Problem | Fix | Result |
|---|---|---|---|
| 1 | Header cart + account icons loaded React + ~20 editor scripts on every page; WooCommerce never used | Removed both blocks from header (cart page itself still works) | Scripts per page 34 → 11; React gone sitewide |
| 2 | 4 unused plugins (Polldaddy, Crowdsignal Forms, Gravatar Enhanced, Layout Grid) — 0 uses in 123 pages/posts | Deactivated | Smaller attack surface; no render change |
| 3 | Homepage hero = 600 KB JPG (LCP 6.8 s) | WebP 48 KB mobile / 200 KB desktop, preloaded | Homepage 2.1 MB/127 req → 1.0 MB/53 req |
| 4 | Homepage map loaded Leaflet + tiles on page open | Loads only when scrolled near | TBT 1,130 ms → 280–500 ms |
| 5 | Homepage H1 had no keywords | H1 = "Pawn Shop & Gold Buyer · Pawn Loans up to $25K · 5 Virginia Stores" (slogan kept, same look) | — |
| 6 | Nav "Shop in Store" → empty page (45 views/wk) | Removed from nav; "Shop Online" → "Shop"; empty page now hands off to /shop/ | — |
| 7 | 63 pages with no H1 (blog template used H2) | Blog template title → H1; H1 added to Contact, FAQ, Sell Gold | All key pages have exactly one H1 |
| 8 | Low CTR on high-impression pages (/locations/roanoke 10.5k impr @ 0.7%; /locations/ 6.8k @ 0.2%; home 65k) | New titles/descriptions on 18 pages: query-first ("Pawn Shop in Roanoke, VA…"), phone number + rating in descriptions | Re-measure CTR 11/17 |
| 9 | Weekly report counted login/password forms as leads | `ga4_pull.py` excludes /my-account (backup .bak-pre-formfilter-20261020) | Leads now true |
| 10 | Brevo form iframes on 6 QR pages loaded eagerly | loading="lazy" | — |

Lighthouse mobile, before → after (2 runs): Home perf 51 → 65/81, LCP 6.8 → 3.8–5.3 s · Roanoke location 52 → 71/81, LCP 8.3 → 3.3 s · Sell gold Roanoke 73 → 76/81 · Shop 64 → 63/76.

## Still open (priority order)
1. **Font: 341 KB Inter variable font on every page** — swap to the 48 KB Latin subset (blocked this session by the deploy-permission layer; one approval to run).
2. **No lead capture besides calls/texts.** Add "Text us a photo for a free quote" on all sell-gold/jewelry/silver/coin pages (SMS is already the working channel).
3. **Roanoke** ranks 5–6 on its biggest query (1,266 impr/90 d). Gap is reviews (292 vs The PawnShop ~727) — Chekkit review asks weighted to Roanoke.
4. Duplicate content: 6-page pawn-loan-explainer cluster → merge + 301 (open since 8/22).
5. GA4 admin (needs edit access): mark phone/sms/directions clicks as key events; exclude data-center traffic (Ashburn = 981 sessions).
6. WooCommerce CSS still render-blocking sitewide → scope to /cart/ via WPCode.
7. /in-store-inventory/ pipeline dormant since August — revive or retire.
8. Accessibility: color contrast + aria-hidden focus on the chat/contact bar.

## Rollback
Header: `backups_pre/assembler__header.html` · Home: `page7_home.html` · Nav: `nav_350.html` · Single template: `template_single.json` · Yoast: `yoast_meta_pre.json` · Plugins: reactivate in WP Admin. All page edits also have WP revisions.
