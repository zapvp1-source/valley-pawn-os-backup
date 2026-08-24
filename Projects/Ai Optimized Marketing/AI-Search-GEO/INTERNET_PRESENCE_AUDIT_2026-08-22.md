# Valley Pawn — Full Internet Presence Audit
**Date:** 2026-08-22 · **Remediation status updated 2026-08-23**

> ## ✅ TIER 1 EXECUTED 2026-08-23 — all verified live, cache-busted
>
> **Blocking question resolved:** Roanoke occupies **both Suite C and Suite D**. The ATF FFL record's
> "2362-D" is **correct, not drift** — the Suite C conflict in §6 is CLOSED. Canonical customer-facing
> NAP stays "Suite C". **Do not "correct" the FFL record.**
>
> | # | Fix | Verified |
> |---|---|---|
> | 1 | "Dixie Pawn" purged — it lived in the Media Library **attachment record**, so it was re-propagating to every new post using that photo | 108-URL crawl: **0** pages contain "dixie" |
> | 2 | Dead Harrisonburg FB page (`61584081596639`) removed from schema + homepage; now points at the real 756-like page | **0** occurrences site-wide |
> | 3 | Waynesboro `sameAs` was pointing at the brand page → now its own store page | live |
> | 4 | Phantom "Ste 22" removed (hid in the **footer template part**, not just schema) | **0** occurrences site-wide |
> | 5 | 5 duplicate PawnShop entities all claiming `/locations/` → each given its own `/locations/{city}/` | live, all 7 JSON-LD blocks re-validated |
> | 6 | `/contact` was indexed **and 404ing** → rebuilt as a real page with all 5 stores, call+text, directions | 200, 10 tel:/sms: links; `/contact` 301s |
> | 7 | Homepage had **zero** click-to-call → "Call or text your store" chip row added in the hero | 0 → **10** tel: links |
> | 8 | Loan figure ($100K / $10,000 / $25,000) aligned to **$100,000** across `/loans/`, `llms.txt`, FAQ | live, consistent |
> | 9 | **38 meta descriptions** hand-written | live |
> | 10 | 6 cannibalizing link-in-bio pages noindexed; real location pages still `index, follow` | live |
> | 11 | 20 city service pages: **0 internal links → ~30 each** (own location page, hub, /contact/, siblings) | live |
>
> **Correction to this report:** the "86 of 109 pages have no meta description" figure in §2 was measured
> from rendered HTML and is **wrong**. The authoritative REST check found 62 present / 46 missing — the
> 20 city service pages already had descriptions.
>
> **Deliberately not done:** geo coordinates in schema. Geocoding the real addresses disagreed with the
> existing Harrisonburg coordinate by ~1.5 km, and Google uses the GBP pin for local ranking — pushing a
> possibly-wrong pin was judged worse than leaving geo absent.
>
> **Heritage claims left alone:** "Trusted Since 1988" was already verified correct in the 8/21 audit
> (the locations date to 1988; Full Circle Finance was formed 2014). Not a defect.
>
> Backups of every pre-change state: `Website/_backups_20260822/`.
>
> **Everything in Tier 2 and Tier 3 below is still open**, plus one thing to confirm: **$100,000 was
> chosen as the loan figure because it was already the SEO title/H1 and the most-repeated public claim.
> If the true maximum is lower, it needs correcting in three places.**

**Scope:** website, Google/Bing/Apple/MapQuest, 40+ directories, Facebook/Instagram/TikTok/X/YouTube, eBay ×5, GunBroker, BBB/Yelp reviews, competitive position in all 5 markets.
**Method:** every finding below was verified against the live surface (fetched pages, live Publer API, live Google Maps embed payloads, live eBay store pages), not against run records or prior STATUS files (Rule 12). Where a surface was unreachable it is marked UNVERIFIED rather than guessed.

---

## THE ONE-PARAGRAPH ANSWER

Valley Pawn's internet presence is **strong where it is owned and weak where it is inherited**. The website, the five eBay stores, the Google review position, and the newly-rebuilt social pipeline are all in good shape or better than the competition. Nearly every real problem traces to **one root cause: the 2026 rebrand was never finished off-site.** "Dixie Pawn" and "Gold-N-Pawn" are still live on Yelp, BBB, MapQuest, Nextdoor, Waze, Facebook, and in the website's own image metadata — and **the only two markets where a competitor outranks us (Harrisonburg and Roanoke) are exactly the two markets where the legacy brand survives.** There is also a **phantom Staunton store** with nine live listings, several linking to thevalleypawn.com, pointing customers at an address we do not occupy. Fixing the rebrand tail is worth more than every other item on this list combined.

---

## SCORECARD

| Channel | Grade | One-line verdict |
|---|---|---|
| Google reviews / local rank | **A−** | 1,559 reviews, 4.88 avg, #1 in 4 of 5 markets. Roanoke is the only real fight and we're 453 reviews behind. |
| eBay | **B** | 514 listings, $82K/90d, 9,367 feedback. Undermined by default stock branding, short titles, and 4 of 5 stores running zero ads. |
| Website content/structure | **B−** | Real location pages, 20 city service pages, fresh blog, valid schema, excellent llms.txt. Held back by duplication and self-contradiction. |
| Website technical SEO | **C+** | 86 of 109 pages have no meta description; 545 duplicate LocalBusiness entities; an indexed page returning 404; zero click-to-call on the homepage. |
| Facebook / Instagram | **C+** | All 6 pages live and posting again after the rebuild — but the site's schema points at the wrong Harrisonburg page, and 3 legacy pages are still live. |
| Directories / citations | **D** | Legacy names on Yelp, BBB, MapQuest, Nextdoor, Waze, YellowPages. Nine phantom-Staunton listings. |
| Video (YouTube/TikTok) | **D−** | YouTube: 13 subscribers, 0 videos, not linked from the site. TikTok: first post in company history goes out 8/26. |
| GunBroker / firearms online | **F** | Five FFLs, zero online firearms channel. eBay bans guns, so this is entirely unserved revenue. |
| On-site commerce | **F** | 494 items on /shop, every one an outbound link to eBay. Zero product pages, zero Product schema, zero Google Shopping. |

---

## 1. THE REBRAND TAIL (highest priority — fix this first)

### 1a. A single stale description is syndicating the legacy names everywhere
This exact string is live, verbatim, on **MapQuest, Nextdoor Culpeper, Superpages, chamberofcommerce.com, and Loc8NearMe**:

> "Count on Valley Pawn, with locations in Waynesboro, Culpeper, **Salem** & Lexington, **Harrisonburg(Dixie Pawn)**, **Roanoke(GNP Pawn)**, Virginia."

Three violations in one sentence: a Salem store that doesn't exist, and both banned legacy brands. It is being pushed by an aggregator feed (the MapQuest listing carries a **Yext "PowerListings Synced" badge** — likely a pre-rebrand Yext or BrightLocal subscription still running). **Killing the feed at the source removes the most instances of legacy naming in one action.** This is the single highest-leverage fix in the entire audit.

### 1b. Live legacy listings, by surface

| Surface | Legacy listing | State |
|---|---|---|
| Yelp | `yelp.com/biz/dixie-pawn-harrisonburg` "DIXIE PAWN" | Live, updated May 2026, listed as a *separate business* from Valley Pawn in Yelp's Harrisonburg pawn category |
| Yelp | `yelp.com/biz/gold-n-pawn-roanoke` "GOLD-N-PAWN" | Live, updated April 2026, our address + our phone |
| BBB | `dixie-pawn-0613-14000312` | **B− rating, "Failed to respond to 1 complaint"** (04/05/2024, cracked camera lens) |
| BBB | `gold-n-pawn-inc-0613-11000478` | Still lists the **prior owners** (Russell/Jonella Harris) as management |
| BBB | Waynesboro profile | Shows **Lexington's phone number**, and displays "Full Circle Finance. INC" publicly |
| MapQuest | ID 410128854 "Dixie Pawn Inc." | Live, owner-verified, Yext-synced |
| Facebook | `facebook.com/dixiepawnhburg/` | Live, our address and phone |
| Facebook | `facebook.com/p/Gold-N-Pawn-100041735065936/` | Live, 17 likes, no profile picture |
| Waze | 3 name variants on one pin (`ChIJL5JLG5-StIkRgcQGBb2TnfI`) | Valley Pawn / Dixie Pawn / "Dixie Pawn, A Valley Pawn Company" |
| YellowPages | `dixie-pawn-inc-452862505` | **Claimed by us** — this is a login-and-type fix, no verification wait |
| Our own website | `harrisonburg-storefront.jpg` in the Media Library | alt text and JSON-LD caption both read *"Dixie Pawn Harrisonburg Virginia storefront"* — **verified live today** |
| Our own Facebook | Valley Pawn Harrisonburg page | Legacy post still visible ("...if so **Dixie Pawn** has you covered!") plus a `#dixiepawn` hashtag |

### 1c. The phantom Staunton store — nine live listings, several linking to our website
817 Richmond Ave, Staunton · (540) 885-0018 — appears on **Yelp, YellowPages (unclaimed, "28 Years in Business"), Nextdoor, Manta, CitySquares, Localmint, MBVT (accruing reviews at 4.4/61), and two FFLs.com records.** Yelp Staunton shows **3.0 stars with three 1-star reviews** — the worst-rated Valley Pawn property on the internet, for a store that doesn't exist. Several of these listings link to thevalleypawn.com, so we are actively sending customers to a dead address.

### 1d. The correlation that proves the point

| Market | Legacy brand still live? | Local rank |
|---|---|---|
| Culpeper | No | **#1** |
| Waynesboro | No | **#1** |
| Lexington | No | **#1** |
| **Harrisonburg** | **Yes — Dixie Pawn** | Loses to JBS Pawn; Yelp lists Dixie Pawn *above* Valley Pawn |
| **Roanoke** | **Yes — Gold-N-Pawn** | Loses to The PawnShop; a Gold-N-Pawn Yelp page outranks us at our own address |

---

## 2. WEBSITE — verified defects

### Critical (verified live 2026-08-22)
1. **`/contact` is indexed by Google and returns HTTP 404.** Confirmed: `curl` → `404`. Google still shows it titled "Need Money? We Can Help!" with a legacy `thevalleypawn@gmail.com` address. Needs a 301 to `/locations/`.
2. **Homepage has ZERO `href="tel:"` links.** Confirmed: count = 0. The only above-the-fold CTA is "View Map ↓". Our highest-traffic page has no way to call us in one tap.
3. **Three different loan amounts, two of them on the same page.** Confirmed: `/loans/` title and H1 say "up to **$100K**" (5 occurrences); its own body copy says "up to **$10,000**"; `llms.txt` says "up to **$25,000**".
4. **Heritage claim contradicts itself on all 109 pages.** Confirmed on the homepage: "Trusted **Since 1988**", "**Thirty-plus years**", and elsewhere "family-owned **since 2014**" with `foundingDate: "2014"` in schema. "Thirty-plus years" is unsupportable at 12 years and it's in the hero. The `llms.txt` framing ("locations serving the Valley since 1988; the company was formed in 2014") is the correct version — apply it everywhere.
5. **"Dixie Pawn" is live on the site** in image alt text and ImageObject JSON-LD — verified today. Because it lives on the Media Library attachment record, it will re-propagate to every future post using that photo.
6. **Harrisonburg address disagrees with itself inside one page.** The site-wide schema block says "1790 East Market Street, **Ste 22**"; the page-specific block says "1790 East Market Street". The wrong version is on all 109 pages and has already propagated to Yelp, YellowPages, and our own GBP listing name.

### High
7. **86 of 109 pages have no meta description** — including all 20 city service pages, all 4 hubs, `/shop/`, `/careers/`, `/ffl-transfer/`, and the FAQ. Google is writing its own snippets for 79% of the site.
8. **545 duplicate LocalBusiness entities.** Every page carries all 5 PawnShop schema blocks, and all 5 declare `"url": "https://thevalleypawn.com/locations/"`. Google receives 5 businesses claiming the same URL, 109 times.
9. **Two competing sets of city pages.** `/locations/{city}/` (the real store pages) and `/{city}/` (social link-in-bio pages with "WIN $100 EVERY MONTH" and no address or phone) — both indexable, both self-canonical, both carrying full PawnShop schema. The link-in-bio pages should be `noindex`.
10. **The 20 city service pages pass zero internal link equity.** Measured: `/sell-gold-{city}/` → `/locations/{city}/` link count = **0** for all five cities. Same for the hub pages. They are islands.
11. **72–76% template duplication** across those same 20 pages; only ~13–16% of each is unique. No landmarks, neighborhoods, or store-specific detail.
12. **The site's Harrisonburg schema points at the wrong Facebook page.** Verified live: `sameAs` = `facebook.com/people/Valley-Pawn-Harrisonburg/61584081596639/` — a page that has **never received a post**. The real, actively-posting page (`facebook.com/valleypawnharrisonburg/`, 756 likes) is never referenced in the footer at all. **Waynesboro's page is missing from the footer entirely**, and Waynesboro's schema `sameAs` points at the brand page.
13. **No review/aggregateRating schema anywhere** — despite "4.9 stars" appearing as plain text on 49 pages and 1,559 real Google reviews behind it.
14. **Geo coordinates on 1 of 5 location pages**; no embedded map and no storefront photo on any of them; 208–214 words each.

### Medium
15. Duplicate/conflicting sitemaps (robots.txt advertises Yoast; `/sitemap.xml` serves Jetpack).
16. WordPress default "Hello World!" post is live and in the sitemap.
17. ~15 near-duplicate blog posts across 7 topic clusters, cannibalizing each other.
18. `/in-store-inventory/` is an empty page sitting in the main nav ("New items are on the way").
19. 86–100 KB of inline CSS on every page (uncacheable), zero WebP images, 4 render-blocking scripts in `<head>`, 2560px-wide logo file, missing image dimensions (CLS risk).
20. A leaked developer comment about GTM setup is in production on 5 pages; GTM was never actually installed.

---

## 3. SOCIAL

**What's fixed:** the 8/22 rebuild is real and visible — 57 posts scheduled for the next 7 days including community, engagement, and video lanes; Harrisonburg up from 1.0 to 5 posts/week; TikTok's first post in company history scheduled for 8/26.

**What's still broken:**

| Item | Detail |
|---|---|
| Harrisonburg duplicate FB page | Two pages exist. Our own website's schema points at the dead one. Merge (don't delete — merging preserves followers and reviews). |
| Three legacy FB pages live | `dixiepawnhburg`, and two Gold-N-Pawn pages. Merge into their successors. |
| Legacy post + `#dixiepawn` hashtag | Still visible on the live Harrisonburg page. |
| Brand page has no phone, no email | Every store page has both. |
| Brand page shares Waynesboro's exact address | Meta treats co-located same-category pages as merge candidates and splits local ranking signal. |
| 3 of 6 pages have no vanity URL | Waynesboro, Culpeper, Roanoke are stuck on `/people/…/100026420539296/` — unshareable, unprintable. |
| Roanoke missing `roanoke@fcfpawn.com` | Only store without its email published. |
| **18 comments in 90 days, 0 replies ever** | The single largest untapped reach multiplier on Meta. Costs nothing but latency. |
| YouTube | 13 subscribers, **0 videos**, not linked from the site — while Lane B1 now produces 6 vertical videos a week that already fit Shorts. |
| TikTok fragmented | Official `@thevalleypawn` (3 followers, in our schema) vs orphan `@valleypawnva` (6 followers, clearly ours). 9 combined. |
| X / Twitter | 25 posts → **40 total reach, 9 likes, 0 followers.** Posts under the display name "Joshua Davis". Either commit or stop spending pipeline slots. |
| Nextdoor | 1 of 5 stores, and it's misspelled "Valley Pawn-**Wayneboro**" with the **old 313 W Main St address**. Nextdoor Roanoke has the street number transposed (2632 instead of 2362). |
| No LinkedIn, no Pinterest | LinkedIn's name is taken by an unrelated Idaho company. Neither is worth the maintenance — recommend skipping both. |
| GBP photos | Harrisonburg and Culpeper show Publer's placeholder avatar, suggesting no profile photo on those two listings. |

**Engagement reality (90 days, live Publer):** median engagement is **0 on 8 of 9 measurable accounts**. Best single post in 90 days: 9 interactions. Reach was −64% vs the prior period as of 8/17. Notable: **Harrisonburg has the highest median reach of any page (46) on the lowest volume (1/wk)** — its audience is the least fatigued, which is why scaling it first is right.

---

## 4. MARKETPLACES

### eBay — five separate stores, all healthy, all under-optimized

| Store | Username | Feedback | Pos% | Active | Listed value |
|---|---|---|---|---|---|
| Roanoke | `valley_pawn_roanoke` | 5,665 | 100% | 106 | $11,939 |
| Lexington | `valley_pawn_lexington` | 1,270 | 98.9% | 27 | $4,119 |
| Culpeper | `valley_pawn_culpeper` | 1,196 | 99.8% | 307 | $47,077 |
| Waynesboro | `valley_pawn_waynesboro` | 619 | 99.6% | 39 | $13,305 |
| Harrisonburg | `valley_pawn_harrisonburg` | 617 | 100% | 35 | $7,002 |
| **Total** | | **9,367** | | **514** | **$83,441** |

90-day revenue $82,064 on $13,617 of fees (**16.6%**).

**Note on a conflicting report:** a search-snippet source suggested an active `ebay.com/usr/dixie-pawn` seller with "1.4K items sold". **Verified directly today — that URL returns "not found."** There is no legacy Dixie Pawn eBay account. All five stores are correctly rebranded on eBay.

Defects:
- **All five stores still run eBay's stock default tagline** ("Your shopping destination for the best selection and value in electronics and accessories"). No store has a custom description.
- **Culpeper's store page contains zero occurrences of "Valley Pawn"** — it's branded only "VP Culpeper".
- Titles average **60.7 of 80 characters**; 35% are under 60. One sampled Harrisonburg title is 39 characters with no model number and no category keyword.
- **Roanoke puts internal SKUs in 18% of its titles** (e.g. `(ROA011696)`) — pure wasted keyword space.
- Photos average 5.8 per listing (71% below the 8-photo threshold); median 4 item specifics.
- **Promoted Listings: $314 in 90 days, 100% of it Culpeper.** Four stores at **$0** on $56,737 of unpromoted revenue. This was flagged eight weeks ago and hasn't moved. There's an unread 50%-off Promoted Listings offer in the Roanoke inbox from 7/12.
- Three open negative/neutral feedbacks with **zero seller replies** — two are description-accuracy failures.

### GunBroker — the biggest single gap in the audit
Five Type-02 FFLs, and **no GunBroker seller presence found**. eBay bans firearms outright, so this is not cannibalization — it's an entire product line with no online outlet. GunBroker fees run ~6–7.5% vs the 16.6% we pay eBay. Pawn shops are a core seller archetype there. *Caveat: GunBroker blanket-403s automated fetching, so absence is unproven — step one is a login check with the store emails, not a build.*

### The website is donating its own commerce to eBay
`/shop` carries **494 unique eBay item IDs**, every one an outbound link. Zero product pages, zero Product schema, zero Google Shopping presence. WooCommerce is already installed and already emits valid Product/Offer JSON-LD — on exactly **one** product. Converting this unlocks Google Shopping free listings, **Local Inventory Ads** (the genuinely valuable one for a 5-store chain — "used [item] near me" converts to foot traffic), a Meta/Instagram catalog, and recapture of the ~13% eBay final-value fee on traffic we already own.

### Channels correctly skipped
Etsy (prohibited item mix), Amazon (no ASINs for one-of-one used goods), Craigslist ($5/posting against $30 items), Poshmark, Mercari, TheRealReal, Worthy (a competitor, not a channel). **Reverb is the one worth adding** — musical instruments are a named retail category, the single live WooCommerce product is a $2,099 Warwick bass, and pawn shops verifiably succeed there. Low volume, high dollars per listing.

---

## 5. REVIEW POSITION — live Google data

| City | Valley Pawn | Top competitor | Gap |
|---|---|---|---|
| Culpeper | **4.9 · 409** | *no competitor with a live Google listing* | **Leader** |
| Waynesboro | **4.9 · 357** | *no competitor with a live Google listing* | **Leader** |
| Harrisonburg | **4.9 · 328** | Pawn Emporium 3.7 · 48; JBS Pawn 4.3 · 25 | **Leader (+280)** |
| Lexington | **4.8 · 191** | Rockbridge Pawn & Guns appears closed | **Leader** |
| **Roanoke** | **4.9 · 274** | **The PawnShop 4.9 · 727** (+166 at a 2nd location) | **−453 single-site, −619 combined** |

Chain total: **1,559 reviews, ~4.88 average.**

**Four of five markets are uncontested.** Roanoke is the only real fight, and the deficit is volume, not quality — identical 4.9 rating, 2.7× the review count. That is a solicitation-throughput problem, and Roanoke is also the store with the worst eBay configuration on the second-highest revenue. Same location, two axes, one fix pattern.

**Reputation liabilities:** the unanswered BBB complaint (the B− is explicitly and solely for non-response); three BBB profiles across three legacy entity names that should be one; the Staunton Yelp ghost at 3.0 stars; three unanswered eBay negatives.

**Historical item, flagged not asserted:** a [2017 VA AG settlement with "Dixie Pawn, Incorporated"](https://oag.state.va.us/consumer-Protection/index.php/news/215-june-12-2017-attorney-general-herring-reaches-settlement-with-dixie-pawn-incorporated) ($22,706.74 refunded to 1,139 borrowers). Corporate succession to Full Circle Finance is circumstantial — matching incorporation date and Harrisonburg address on the current BBB record, SCC records unreachable. It surfaces on any "Dixie Pawn" search, which is one more reason to retire the name everywhere.

---

## 6. WHAT I COULD NOT VERIFY

Stated explicitly rather than assumed clean:
- **Apple Business Connect / Apple Maps** — no public place URL surfaced; whether Harrisonburg still shows Dixie Pawn on Apple Maps (and therefore in Siri and every iOS map query) is **unresolved and needs a console login**.
- **Bing Places** — bing.com/maps returns a JS shell with no business payload. Prior sessions confirmed all 5 Bing listings are Published and correct, but the Harrisonburg lead photo was reported as the old Dixie Pawn storefront sign. Needs a console check.
- **Google Business Profile console** — lives on a different Google account than the one signed into Mac Chrome. Post cadence and location IDs were verified via Publer; ratings, photos, Q&A, and review-response status were not.
- Facebook Messenger response rates and review-response status (login-gated).
- Whether the four unclaimed eBay handles (`valley_pawn`, `dixie_pawn`, `valleypawn`, `goldnpawn`) are our defensive registrations or third parties.
- **Roanoke suite letter conflict:** canonical says "Suite C"; three independent sources including the **ATF FFL record** say **"2362-D"**. Resolve this internally before pushing any mass address correction — otherwise we propagate an error into the FFL record.

---

## 7. THE PLAN — ranked by value per hour of effort

### TIER 1 — do this week (biggest return, smallest effort)
1. **Find and kill the Yext/aggregator feed** pushing the "Salem / Dixie Pawn / GNP Pawn" description. One action cleans MapQuest, Nextdoor, Superpages, chamberofcommerce.com and Loc8NearMe simultaneously.
2. **Rename the YellowPages Harrisonburg listing** from "Dixie Pawn Inc" to Valley Pawn and drop "Ste 22". **We already own the claim** — login-and-type, no verification wait.
3. **Answer the open BBB complaint** and request the name change on all three BBB profiles. The B− exists solely because of non-response.
4. **Fix the website's Harrisonburg `sameAs`** to point at `facebook.com/valleypawnharrisonburg/`, and add Waynesboro to the footer. Pure website edit, no Meta token needed.
5. **301 `/contact` → `/locations/`** (and `/directions-and-contact/`). An indexed, Google-surfaced page is 404ing right now.
6. **Add click-to-call above the fold on the homepage.** Zero tel: links on our highest-traffic page.
7. **Purge "Dixie Pawn" from the WordPress Media Library** attachment record — not just the one post, or it recurs.
8. **Kill the phantom Staunton cluster** — nine listings, several linking to our live site.

### TIER 2 — next two weeks
9. **Merge the legacy Facebook pages** into their successors (merging carries followers and reviews; deleting throws them away). Same for the Harrisonburg duplicate.
10. **Reconcile the loan amount** ($100K vs $10,000 vs $25,000) and the **1988/2014/"thirty-plus years"** contradiction site-wide.
11. **Write the 86 missing meta descriptions**, prioritizing the 20 city service pages.
12. **Collapse the schema** — one Organization site-wide, one PawnShop per location page with correct `url`, plus `geo`, `priceRange`, storefront `image`, and correct `sameAs`. `noindex` the 5 link-in-bio city pages.
13. **Internally link the 20 city service pages** to their own location page and hub. Currently zero.
14. **Turn on Promoted Listings at the four dark stores** and write real eBay store descriptions (kill the stock tagline; get "Valley Pawn" onto the Culpeper store page).
15. **Ship the comment-reply watcher.** 18 comments / 0 replies over 90 days.
16. **Connect YouTube** to the video pipeline and link it from the site. 6 vertical videos a week are already being produced and already fit Shorts.
17. **Concentrate review solicitation on Roanoke** — it's the only contested market and the gap is 453.

### TIER 3 — this quarter
18. **Stand up GunBroker** for all five FFLs (login check first, then build). An entire product line currently has no online outlet at half the fee rate we pay eBay.
19. **Convert `/shop` into real product pages** — unlocks Google Shopping, Local Inventory Ads, a Meta catalog, and fee recapture. WooCommerce is already installed and already works.
20. **Differentiate the city service pages** to ≥40% unique — landmarks, neighborhoods, store photos, local review quotes.
21. **Verify Apple Business Connect and Bing Places directly**, including the Harrisonburg lead photo.
22. **Correct the FFL records** — expired Waynesboro "313 West Main St", Lexington "439 East Nelson", and resolve the Roanoke Suite C / 2362-D conflict. This is compliance exposure, not just marketing.
23. **Reconsider publishing 282 Bald Rock Rd** as the FFL mailing address — it ties the rental property to the firearms licenses.
24. **Add Reverb** for musical instruments. Best labor-to-dollar ratio of any new channel.
25. **Join the 5 local chambers of commerce** — highest-authority local backlinks available to a multi-location retailer, and we're in none of them.
26. **Restore or drop the NPA membership claim.** The website publicly claims NPA membership; no entry appears in the NPA member directory.
27. **Decide on X** (40 reach from 25 posts) and **skip LinkedIn and Pinterest**.

---

*Sources: live fetches of thevalleypawn.com (109 pages, robots.txt, both sitemaps, llms.txt, /loans/, /contact, media attachment records) · live Publer API (15 accounts, 554 posts, 90-day analytics, forward queue) · live Google Maps embed payloads for all 5 stores + 8 competitors · live eBay store pages ×5 · MapQuest 410128854 · BBB ×3 profiles · YellowPages, Nextdoor, Yahoo Local, FFLs.com, pawnshops.net, MasterFFL · Virginia AG complaint API · prior work: AUDIT-2026-08-21.md, SOCIAL_AUDIT_AND_PLAN_THROUGH_DEC_2026.md, eBay_Channel_Audit_2026-08-22.md, CHANGELOG.md.*
