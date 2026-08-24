# Website fixes applied — 2026-08-23

All changes verified against the **live pages**, not API responses (Rule 12).
Site health checked after every write: all pages 200, zero PHP fatals.

## Measured before → after

| Metric | Before | After |
|---|---|---|
| Pages with **zero** `tel:` links | 54 of 108 | **0** |
| Homepage click-to-call / text | none at all | Call + Text + Directions, sitewide |
| Pages with broken JSON-LD | 5 | **0** |
| Indexable pages with no meta description | 84 | **34** (all blog posts pending consolidation) |
| Double-branded titles (`… Valley Pawn - Valley Pawn`) | 46 | **0** |
| Titles over 62 chars | 43 | 36 |
| Thin/duplicate utility pages indexed | 9 | **0** (noindexed, still live) |
| Indexable pages in sitemap | 108 | 96 |

---

## 1. Global Call / Text / Directions layer — the big one
**Where:** `assembler//footer` template part

- Sticky bar on every page: **Call · Text · Directions**.
- **Page-context aware.** On any URL containing a city (`/locations/roanoke/`, `/sell-gold-roanoke/`, `/roanoke/`…) it binds straight to that store's number. Verified: on `/locations/roanoke/` it auto-bound to Roanoke.
- Everywhere else it opens a 5-store chooser sheet. No geolocation, no permission prompt, no third-party service.
- Mobile: full-width bottom bar, with a 76px gap reserved on the right so it never covers the Chekkit chat bubble. Desktop: compact pill, bottom-**left**, clear of the chat widget.
- Fires GA4 `phone_click`, **`sms_click`** (which was not tracked before), and `directions_click`, with the store and source attached.
- Accessible: 56px tap targets, aria-labels, Esc-to-close, focus outlines, hidden in print.

**To remove it:** delete everything between `VP-CONTACT-BAR-START` and `VP-CONTACT-BAR-END` in the footer template part.

## 2. Footer rebuilt as a real NAP block
Was: three columns, five anchor links, and `jdavis@fcfpawn.com` as plain text — no phone, no address anywhere.

Now: all 5 stores with address, hours, **Call**, **Text us**, **Directions**, and the store's own `{city}@fcfpawn.com`. Customer leads now route to stores instead of the owner's inbox. Chekkit webchat and the mobile hamburger fallback were preserved byte-for-byte.

## 3. Broken structured data on 5 sell-gold pages — fixed
`"dayOfWeek": "["Monday",…]"` — the array was wrapped in quotes, which broke the JSON and made Google discard the **entire** `LocalBusiness` + FAQ block on the five highest-intent gold pages.

Fixed on pages 509–513. **Verified live: 9/9 JSON-LD blocks now parse on every one, with `LocalBusiness` and `FAQPage` both recognized.** Confirmed the same bug was *absent* from the jewelry/silver/coins city pages, so the fix is correctly scoped.

## Rollback
Every changed page and the footer template part carry **WordPress revisions** (5 each, verified) — the pre-change version of all six pages is restorable from the WP editor's revision history at any time. Post-change snapshots are also saved in `backups/*.CURRENT.html` for diffing. The contact bar can be removed on its own by deleting the `VP-CONTACT-BAR-START`…`END` block; snippet 1135 can be toggled off in WPCode without touching anything else.

## 4. Meta descriptions — 40 pages written
Every commercial page now has a hand-written 116–163 char description: all 20 city × metal pages, the 4 hubs, all 5 location pages, sell-gold/jewelry/silver/coins, loans, retail + its 5 categories, FFL, careers, FAQ, shop, in-store, returns, contact, privacy.

**Non-destructive:** 11 pages that already had a human-written description were left untouched (logged in the run output).

## 5. Nine utility pages removed from the index (still live)
`noindex, follow` applied to: `/follow/`, `/culpeper/`, `/waynesboro/`, `/harrisonburg/`, `/lexington/`, `/roanoke/`, `/keep-in-touch/`, `/giveaway-rules/`, `/store-products/`.

These are QR / link-in-bio / utility pages (WP pages 748–753 etc.) that were competing with the real `/locations/{city}/` pages for brand+city searches. They still work for QR codes and social bios — they just no longer split ranking signals. **Verified the real money and location pages remain `index, follow`.**

`/hello-world/` (the default WordPress starter post) now returns 404.

## 6. All 46 double-branded titles — fixed at the root
Yoast was appending the site name to titles that already contained it, producing `Sell Gold in Culpeper, VA | Get a Fair Offer Today | Valley Pawn - Valley Pawn`. Rather than edit 46 titles, one filter now strips the trailing site name **only when the brand already appears earlier**, so nothing loses its branding. Fixes every current and future page.

## 7. Heritage claim made precise
Homepage badge `⭐ Trusted Since 1988 ⭐` → `⭐ Serving the Valley Since 1988 ⭐`, matching the canonical phrasing already in `llms.txt` and the FAQ ("locations serving the Valley since 1988; the company was formed in 2014"). This removes the apparent contradiction with the 44 pages that say "since 2014".

## 8. New capability: Yoast fields are now writable via the API
**WPCode snippet 1135 — "Valley Pawn — Yoast SEO fields in REST API"** (PHP, Run Everywhere, active).

Registers `_yoast_wpseo_metadesc`, `_yoast_wpseo_title`, and the noindex/nofollow flags for the REST API, with permissions unchanged (only users who can already edit a post can write). Values still appear and edit normally in the Yoast box.

This is what made items 4, 5 and 6 possible in bulk instead of by hand — and it permanently unlocks meta management for the blog publisher and the AI-search autofix tasks.

---

## Still open

**One question only Joshua can answer — the maximum loan amount.** The site currently states three different figures:

| Figure | Where |
|---|---|
| **$100K** | `/loans/` page title and body |
| **$10,000** | `/loans/` body, a few paragraphs later |
| **$25,000** | `llms.txt` (what AI answer engines read) |

I did not guess. Tell me the right number and I'll make it consistent everywhere in one pass.

**Not yet done** (from the audit, in priority order):
1. **Consolidate the 26 duplicate pages with 301s** — highest remaining SEO impact, and the likeliest cause of losing Harrisonburg and Roanoke. Needs editorial judgment on which page wins each cluster and real content merging, so it's worth doing deliberately rather than fast. The 34 blog posts still missing descriptions are mostly these duplicates — worth writing descriptions only for the survivors.
2. **Performance** — ~780 KB and 38–41 render-blocking resources per page. Deactivate the Gutenberg *development* plugin (it ships React to the front end), scope WooCommerce assets to commerce pages, replace the 2560px PNG logo, add image dimensions.
3. **`/in-store-inventory/`** still shows "New items are on the way" while sitting in the primary nav as "Shop in Store".
4. **Measurement** — no Meta Pixel (despite an active Meta ad program), no Google Ads conversion tag, Microsoft Clarity installed but emitting nothing.
5. **Location pages** are ~198 words; competitors in the two markets you're losing run 800–1,500 with live inventory and embedded reviews.
6. **Schema scoping** — `FAQPage` is injected on all 108 pages including `/cart/` and `/privacy-policy/`; all 5 store entities are injected on every page.
