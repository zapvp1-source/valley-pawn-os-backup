# thevalleypawn.com — Full Website Audit
**Date:** 2026-08-22 · **Scope:** all 108 indexed URLs, crawled live · **Lens:** drive calls, texts, emails, and walk-ins

---

## Executive summary

The site is technically well-built and further along than most 5-location retailers — Yoast, schema, llms.txt, GA4 lead-event tracking, 20 city × service pages, a working deals block, and a real blog cadence. Somebody did serious work here.

But it is leaking money in three places at once:

1. **The homepage cannot be called.** There is not one `tel:` or `sms:` link on the homepage, in the header, or in the footer. Zero. The site-wide footer's only contact is `jdavis@fcfpawn.com` — the owner's personal address. Every visitor who lands on the homepage (the highest-traffic page on the site) has no one-tap way to reach a store. Your own north-star metric is `calls_texts_per_1k`.
2. **The content library is cannibalizing itself.** 26 pages are near-duplicates of other pages — four "emergency fund" posts, four "selling gold" posts, four "pawn loan explainer" pages, three "pawn shop myths" posts, two of nearly everything else. Google splits authority across all of them and ranks none of them well. This directly explains why Harrisonburg and Roanoke are losing.
3. **Every page loads ~780–815 KB across 48–51 requests with 38–41 render-blocking resources.** A local-business landing page should be under 250 KB with fewer than 10 blocking resources. On a mobile connection in a store parking lot, this is the difference between a call and a bounce.

Fix #1 in an afternoon. Fix #2 and #3 over two weeks. Those three alone should move calls/texts materially.

---

## P0 — Fix this week (revenue is leaking right now)

### 1. No click-to-call or click-to-text anywhere in the global header/footer
**Evidence:** Crawled all 108 pages. Homepage raw HTML contains **zero** `href="tel:"`, `href="sms:"`, or `href="mailto:"` — verified directly. Forms = 0. The footer's only links are five `/locations/#{city}` anchors; its only contact detail is `jdavis@fcfpawn.com` rendered as **plain text, not even a clickable mailto**. No phone, no address. 54 of 108 pages have zero `tel:` links.

**Why it matters:** Your stated north star is calls + texts per 1,000 sessions. The single highest-traffic page on the site offers neither. The only "Text Us" instruction on the homepage is passive prose — *"Click the chat button in the bottom right corner"* — which is a chat widget, not a text.

**Fix:**
- Add a sticky mobile bottom bar on every page: **Call · Text · Directions**, geo-defaulted or defaulted to nearest-store picker.
- Add a phone number + "Call / Text" buttons to the desktop header, right of the nav.
- Rebuild the footer as a real NAP block: all 5 stores, address, `tel:`, `sms:`, store email (`{city}@fcfpawn.com`), hours, directions link.
- **Remove `jdavis@fcfpawn.com` as the public contact.** It routes customer leads to the owner instead of a store and is a spam magnet.
- Your `/c/{store}` → `tel:` and `/t/{store}` → `sms:` redirects **work correctly** (verified all 5). Use them so QR/print and web share one tracked path.

**Effort:** Low (footer template part `assembler//footer` + one WPCode snippet). **Impact:** Highest on the list.

---

### 2. "Shop in Store" — a primary nav item leading to an empty page
**Evidence:** `/in-store-inventory/` renders *"New items are on the way — check back soon."* Zero items. It sits in the main navigation.

**Why it matters:** A shopper who clicks the one nav item promising local inventory hits a dead end. The `shop-in-store-sync` task was rebuilt 2026-08-21 but the page is still empty.

**Fix:** Either get the sync producing items, or temporarily point the nav item at `/shop/` (505 live items) and hide `/in-store-inventory/` until stocked. Do not leave an empty page in primary nav.

**Effort:** Low. **Impact:** High.

---

### 3. Broken structured data on all 5 `sell-gold-{city}` pages
**Evidence:** JSON-LD block #8 fails to parse. Root cause is a quoting bug:
```json
"dayOfWeek": "["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]"
```
The array is wrapped in quotes, which breaks the JSON. Google discards the **entire block** — meaning the `LocalBusiness` entity *and* the FAQ markup on your five highest-intent gold pages are invisible.

Verified present on **all 5** `sell-gold-{city}` pages and verified **absent** from the `sell-jewelry`/`sell-silver`/`sell-coins` city pages — so the bug is isolated to the gold template.

**Fix:** Remove the outer quotes so it's a real array. Re-test all 5 in Google's Rich Results Test.

**Effort:** 15 minutes. **Impact:** High — these are your money pages.

---

### 4. Conflicting facts across the site (trust + AI-answer poisoning)
| Claim | Where | Conflicts with |
|---|---|---|
| "Trusted Since **1988**" | Homepage | `/culpeper/`: "Family-owned since **2014**" |
| "Loans up to **$100K**" | `/loans/` title + body | `/loans/` body: "up to **$10,000** and beyond" · llms.txt: "up to **$25,000**" |
| "Average **4.9 stars**" | Homepage | No review count, no source, no `aggregateRating` schema anywhere on the site |

**Why it matters:** AI answer engines (which you already track via `vp-ai-visibility-metrics`) read these directly. Three different loan ceilings on one site is the kind of inconsistency that gets a brand dropped from an AI answer. Your own llms.txt reconciles the date correctly — *"locations serving the Valley since 1988; the company was formed in 2014"* — the site does not.

**Fix:** Pick one loan ceiling and use it everywhere. Use the llms.txt heritage phrasing site-wide. Either substantiate the 4.9 (add review count + "across N Google reviews") or drop it.

**Effort:** Low. **Impact:** High.

---

## P1 — Fix in the next 2–3 weeks

### 5. Keyword cannibalization: 26 redundant pages
| Topic | Live pages | Should be |
|---|---|---|
| Pawn loan explainer | 5 (`/loans/`, `/pawn-loans/`, `/how-pawn-loans-work/`, `/how-a-pawn-loan-actually-works…/`, `/how-pawn-loans-work-a-plain-english-guide/`) | 1 |
| Emergency fund | 4 | 1 |
| Selling gold | 4 | 1 |
| Pre-owned tools | 4 | 1 |
| Pawn shop myths | 3 | 1 |
| Shop surfaces | 3 (`/shop/`, `/in-store-inventory/`, `/store-products/`) | 2 |
| Selling silver, gold karat, instruments, pawn-vs-payday, appraisals, what-can-you-pawn, back-to-school, summer-in-the-valley | 2 each | 1 each |

**Fix:** For each cluster, pick the strongest page, merge the best unique content into it, then **301 the rest into it**. Do not delete without redirecting. Update internal links.

**Effort:** Medium (one focused day). **Impact:** High — this is the most likely single cause of Harrisonburg and Roanoke underperformance.

---

### 6. Duplicate city URL structures competing with each other
`/culpeper/` (189 words, link-in-bio page with giveaway + social links, **no phone**) and `/locations/culpeper/` (198 words, real store info) are both indexed, both targeting the same brand+city query. Same for all 5 cities.

**Fix:** `noindex` the `/{city}/` link-in-bio pages (they're for QR/social, not search). Keep them live — just take them out of the index. Also `noindex` `/store-products/`, `/follow/`, `/keep-in-touch/`, `/giveaway-rules/`, and **delete `/hello-world/`** (the default WordPress starter post is still live and indexed).

**Effort:** Low. **Impact:** Medium-High.

---

### 7. 84 of 108 pages have no meta description
Including **every single money page**: `/sell-gold/`, `/sell-jewelry/`, `/sell-silver/`, `/sell-coins/`, all 20 city × metal pages, all 5 `/{city}/` pages, `/shop/`, `/ffl-transfer/`, `/careers/`, `/frequently-asked-questions/`.

Google writes its own snippet when you don't — usually a worse one. On a "sell gold Harrisonburg" result, the snippet is most of your click-through rate.

**Fix:** Write 150–160 char descriptions for the ~30 commercial pages first (city × metal, hubs, locations, FFL, careers, FAQ, shop). Lead with the offer and a reason to click. Blog posts second.

**Effort:** Medium. **Impact:** High on CTR.

---

### 8. 53 pages have no `<h1>` at all
Every blog post, `/shop/`, `/frequently-asked-questions/`, `/directions-and-contact/`, `/sell-gold/`, `/in-store-inventory/`. The post title is rendering as something other than an H1.

**Fix:** Correct the theme/template so the page title outputs as H1. Single template fix covers most of them.

**Effort:** Low. **Impact:** Medium.

---

### 9. Homepage H1 is invisible to search
Current H1: *"Need money? We can Help. Need cool stuff? We got You."* Good hook, zero SEO value — no service, no place.

**Fix:** H1 → something like *"Pawn Loans & Gold Buying — 5 Locations Across Virginia's Shenandoah Valley."* Demote the current line to a kicker/H2 above it. You keep the voice and gain the keyword.

Also: homepage body is only **428 words** and contains no address, no phone, no map text, no reviews, no form. For a commercial homepage in five competitive markets that's very thin.

**Effort:** Low. **Impact:** Medium-High.

---

### 10. Performance: 780–815 KB, 48–51 requests, 38–41 render-blocking
Measured on a mobile user-agent:

| Asset | Size | Note |
|---|---|---|
| `googletagmanager.com/gtag/js` | **496 KB** | Single largest asset on the site |
| Gutenberg plugin `react-dom.min.js` | 43 KB | Front-end waste — see #11 |
| Leaflet (cdnjs) | 41 KB | Third-party CDN, homepage map |
| jQuery | 30 KB | |
| lodash | 26 KB | |
| WooCommerce CSS/JS | ~11 KB + | Loading on `sell-gold-culpeper` and every non-commerce page |
| Gutenberg compose + wp-polyfill | ~23 KB | |

Also: the logo is served as a **2560 px-wide PNG** (`?fit=2560%2C284`) on every page. Homepage images have no `width`/`height` attributes (layout shift) and no `loading="lazy"`.

**Fix:**
- Deactivate the **Gutenberg plugin** (see #11) — removes React DOM + compose + polyfill from the front end.
- Dequeue WooCommerce CSS/JS on non-commerce pages.
- Serve the logo as SVG or a 600 px WebP.
- Add explicit `width`/`height` to all images; lazy-load below-fold.
- Self-host or defer Leaflet; consider a static map image + "Get Directions" link instead of an interactive map on the homepage.
- Audit the GA4 container — 496 KB suggests more configs loaded than needed.

**Effort:** Medium. **Impact:** High on mobile conversion, and Core Web Vitals is a ranking factor.

---

## P2 — Fix this quarter

### 11. Plugin stack needs a cleanup
| Plugin | Status | Recommendation |
|---|---|---|
| **Gutenberg 23.8.0** | Active | **Deactivate.** This is the bleeding-edge *development* plugin running on a revenue site. Core's block editor is enough. It's also shipping React to the front end. |
| **Microsoft Clarity** | Active but **emitting nothing** | `clarity.ms` appears **0 times** in the page HTML. The plugin is installed but not configured — you're collecting zero session replay. Either add the project ID (heat maps on the sell-gold pages would be genuinely useful) or remove it. |
| **Yoast SEO + Jetpack** | Both active | Both generate sitemaps. `/sitemap_index.xml` (Yoast) *and* `/sitemap.xml` (Jetpack) are both live. robots.txt declares only Yoast's. Turn off Jetpack's sitemap module. |
| **Header Footer Code Manager + WPCode Lite** | Both active | Two script-injection plugins doing the same job. Consolidate onto WPCode (which already holds snippets 738 schema / 742 llms.txt). |
| Crowdsignal Dashboard, Crowdsignal Forms, Gravatar Enhanced, Layout Grid | Active | Verify anything uses them; deactivate what doesn't. |
| HFCM 1.1.44, WPCode 2.3.6 | Outdated | Update to 1.1.46 / 2.3.8. |
| WooCommerce + WooPayments | Active | Keep (the shop uses it), but scope its assets to commerce pages only. |

---

### 12. Measurement gaps
- **No Google Ads conversion tag (`AW-`).** You cannot run paid search with conversion tracking until this exists.
- **No Meta Pixel.** You have a `vp-ad-engine` skill that builds Meta ad variants and an active Meta posting program — with no pixel, none of that spend is measurable or retargetable. This is the highest-value 20-minute fix in the whole audit if you ever spend a dollar on Meta.
- **`sms_click` is not tracked.** Your GA4 snippet fires `phone_click` and `directions_click` only. Text is a stated primary goal — track it.
- No `form_submit` event on the email-capture forms.

---

### 13. Schema quality
- **FAQPage markup is injected on all 108 pages** — including `/cart/`, `/privacy-policy/`, and every blog post. Site-wide FAQ schema on pages with no visible FAQ is a low-quality signal and risks a manual action. Scope it to pages that actually display the FAQ.
- **All 5 store `PawnShop` entities are injected on every page.** Location entities should live on their location page. Sitewide, use one `Organization` + the store list on `/locations/`.
- **No `aggregateRating` / `Review` schema anywhere** — despite a 4.9-star claim on the homepage. If the reviews are real, surface them on-site with proper markup and you become eligible for star ratings in results.
- `/locations/{city}/` pages carry **no city-specific `LocalBusiness`** — but `/sell-jewelry-{city}/` pages do. Backwards: the location page should be the strongest entity.

---

### 14. Location pages are too thin to win local
`/locations/culpeper/` is **198 words**. It has address, phone, hours, email, directions — and nothing else. No store photos, no map embed, no staff, no reviews, no services list, no FAQ, no local inventory, no "what we buy here."

Competitors in Roanoke and Harrisonburg (The Pawn Shop Inc, Cash Converters, The Coin & Gift Shop) are running 800–1,500-word location pages with live inventory counts, embedded Google reviews, and lead forms.

**Fix:** Rebuild each location page to 700+ words: store photos, embedded map, full services list, staff intro, 5–8 embedded Google reviews, a store-specific FAQ, that store's deals block, and Call/Text/Directions above the fold.

---

### 15. Accessibility & hygiene
- Form inputs on `/careers/`, `/keep-in-touch/`, and the 5 `/{city}/` pages have **no label, no `aria-label`, no placeholder**.
- 2 images per page missing `alt` text.
- WooCommerce mini-cart (`Your cart (items: 0)`) renders in the DOM on every page including the homepage.
- `/Locations/` (capital L) returns **200**, not a 301 to lowercase. Canonical is correct, so low severity — but redirect it.
- `/hello-world/` — the default WordPress starter post — is still live, indexed, and in the sitemap.
- Title tags: 47 exceed 62 characters; several double-brand (`"Sell Gold in Culpeper, VA | Get a Fair Offer Today | Valley Pawn - Valley Pawn"`). Fix the Yoast title template so the brand isn't appended twice.

---

## Competitive read — where you're actually losing

Verified via search across all 5 markets:

| Market | Position | Notes |
|---|---|---|
| **Waynesboro** | **Winning** | Valley Pawn owns most of page 1. Only real competitor is Pawn Shop & Guns (Staunton) — dated site, no `tel:` link. |
| **Culpeper** | **Winning** | No local competitor with a real website. |
| **Lexington** | **Winning** | Rockbridge Pawn's domain doesn't resolve; they run on Facebook only. |
| **Harrisonburg** | **Losing** | JBS Pawn (no working website!), Pawn Emporium, and Yelp all outrank you. `/locations/harrisonburg/` didn't surface at all. On "sell gold Harrisonburg," The Coin & Gift Shop wins with live spot-price widgets, PCGS/NGC badges, estate services, and video testimonials. |
| **Roanoke** | **Losing badly** | `/sell-gold-roanoke/` ranked last of 8. Six gold/coin specialists rank above you. The Pawn Shop Inc runs 3 locations with live searchable PawnMate inventory (344 tools, 129 consoles, 120 jewelry — with counts), embedded Google reviews, an SMS program with HELP/STOP compliance, and a published 10/10/10 layaway. Cash Converters runs Podium webchat plus a real free-appraisal lead form that captures item detail *and desired payout*. |

**Being beaten in Harrisonburg by a business whose website does not resolve is a content-quality problem, not a competition problem.**

### Pages/features competitors have that you don't
1. **Free appraisal / "get an offer" lead form** — Cash Converters captures item, photos, and desired payout. You have no lead form of any kind.
2. **Live gold & silver spot-price widget** on sell-gold pages (The Coin & Gift Shop). You already run `vp-weekly-spot-price-update` — the data exists, it's just not on the site.
3. **Live, searchable inventory with category counts** (PawnMate model).
4. **Layaway page with published terms** (10/10/10). You offer layaway; there's no page for it.
5. **Jewelry / coin / bullion testing** as a named service page.
6. **Online loan payment portal.**
7. **Estate / collection buyout** service page — high-ticket, and nobody in your markets except Coin & Gift owns it.
8. **On-site Google Reviews embed + review-request form.**
9. **Vehicle title loans** (Rockbridge, Lexington market) — a service line no page of yours covers.

---

## Recommended sequence

**Week 1 (P0)**
1. Global header + footer: Call / Text / Directions on every page, all 5 stores in the footer NAP, remove `jdavis@fcfpawn.com`
2. Sticky mobile Call/Text bar
3. Fix the `dayOfWeek` JSON bug on 5 sell-gold pages
4. Reconcile 1988/2014, $10K/$25K/$100K, and the 4.9 claim
5. Fix or hide `/in-store-inventory/`

**Weeks 2–3 (P1)**
6. Consolidate the 26 duplicate pages with 301s
7. `noindex` link-in-bio/utility pages; delete `/hello-world/`
8. Meta descriptions for the ~30 commercial pages
9. H1 fix (template) + homepage H1 rewrite
10. Performance pass — kill Gutenberg plugin, scope Woo assets, fix the logo, add image dimensions

**Month 2 (P2)**
11. Plugin cleanup + Clarity configured (or removed)
12. Meta Pixel, Google Ads tag, `sms_click` + `form_submit` events
13. Schema scoping (FAQ, per-location entities, aggregateRating)
14. Rebuild all 5 location pages to 700+ words
15. Ship the free-appraisal lead form + spot-price widget + layaway page — the three highest-leverage competitive gaps

---

## What's already good (don't break it)
- Yoast + canonical tags + HTTPS/www redirects all clean
- `/c/{store}` → `tel:` and `/t/{store}` → `sms:` redirects verified working on all 5 stores
- `llms.txt` published and accurate — ahead of essentially every competitor
- GA4 with custom `phone_click` / `directions_click` events already wired
- `/retail/` deals block is the best-converting pattern on the site: per-store Call, Text, and Directions links on every deal. **This is the pattern to copy everywhere else.**
- 20 city × metal service pages exist with 10 `tel:` and 11–12 `sms:` links each — strong structure, they just need meta descriptions and the schema fix
- `/careers/` has valid `JobPosting` schema
- Cache is hitting at the CDN edge (`x-ac: HIT`, ~220 ms TTFB)
