# WordPress Deployment Guide — "Sell Your [Gold/Silver/Coins/Jewelry]" Landing Pages

Step-by-step deployment for `thevalleypawn.com`. Originally written for the 6 gold pages (hub + 5 spokes); now extended to cover all **4 categories × 5 stores = 20 store pages + 4 category hubs = 24 pages total**.

**Recommended:** stagger the launch across 4 waves (gold → jewelry → coins → silver). See the "Phased Launch" section at the bottom. Total deploy time per wave: ~60–90 minutes.

---

## Pre-Flight Checklist

- [ ] Admin access to `thevalleypawn.com` WordPress backend
- [ ] Chekkit account access (you already use it — just need the widget snippet ready)
- [ ] Google Tag Manager container access (or ability to add a GA4 tag directly)
- [ ] Google Search Console verified for `thevalleypawn.com`
- [ ] The 5 page HTML files from `store-instances/`

---

## Step 1 — Create the Pages in WordPress

**Single category (one wave):** 1 category hub + 5 store spokes = 6 pages.
**Full rollout (all 4 categories):** 4 hubs + 20 spokes = 24 pages.

The instructions below describe building one category. Repeat the section for each category in your launch wave (just swap "gold" for "silver", "coins", or "jewelry" — same procedure, different HTML files from `store-instances/{category}/`).

### Create the hub page

1. WP Admin → **Pages → Add New**
2. Title: `Sell Gold in Virginia`
3. Permalink slug: `sell-gold` (URL becomes `thevalleypawn.com/sell-gold/`)
4. Page Attributes → Template: **Full Width** or **Blank Canvas** (whichever your theme exposes — we want NO sidebar, NO default header bleed-through)
5. Content: a short intro paragraph + the 5 store landing-page links. Example body:
   ```
   Valley Pawn buys gold at all 5 of our Virginia locations — Culpeper, Waynesboro,
   Harrisonburg, Lexington, and Roanoke. Pick the store closest to you to get an
   instant offer with our live gold calculator and text us directly.

   • Culpeper — sell-gold-culpeper/
   • Waynesboro — sell-gold-waynesboro/
   • Harrisonburg — sell-gold-harrisonburg/
   • Lexington — sell-gold-lexington/
   • Roanoke — sell-gold-roanoke/
   ```
6. (Optional but ideal) — also add the gold calculator on this hub page, defaulting to a "we'll route you to your nearest store" CTA.
7. Publish.

### Create the 5 spoke pages

For each of: `culpeper`, `waynesboro`, `harrisonburg`, `lexington`, `roanoke`:

1. **Pages → Add New**
2. Title: `Sell Gold in [City], VA`
3. Permalink slug: `sell-gold-[city]`  (e.g. `sell-gold-culpeper`)
4. Page Attributes → Template: **Full Width** / **Blank Canvas**
5. In the block editor, add a single **Custom HTML** block (the `</>` icon)
6. Open the corresponding file from `store-instances/sell-gold-[city].html` in any text editor
7. Copy the ENTIRE file contents and paste into the Custom HTML block
8. **Preview** before publishing — confirm:
   - Page loads, no errors
   - Logo loads at the top
   - Calculator works (try 14k, 5g — should show roughly $295–$359 range at current spot)
   - Phone/Text buttons are correct for that city
   - All 5 store locations appear at the bottom
   - Map embed loads
9. **Yoast/RankMath SEO meta** (if installed):
   - Meta title: `Sell Gold in [City], VA | Get a Fair Offer Today | Valley Pawn`
   - Meta description: `Sell your gold in [City], VA. Use our free gold calculator to see your offer instantly, then text or call Valley Pawn. Family-owned since 2014.`
   - Focus keyword: `sell gold [city] va`
10. Publish.

---

## Step 2 — Site Navigation

Add a top-level menu item so the pages are discoverable and pass internal link equity.

1. **Appearance → Menus**
2. Add a parent menu item: **Sell to Us** (or **Get Cash for Gold**)
3. Under it, add 5 children — one per store landing page
4. Save menu

Also: add a link from the homepage hero or services section to `/sell-gold/`. Internal links from high-traffic pages dramatically speed up Google's recognition that these are important pages.

---

## Step 3 — Chekkit Widget

You already use Chekkit for incoming messages. Two options:

### Option A — Site-wide (recommended)
Add the Chekkit JS snippet once to the WordPress theme footer so it appears on every page.

1. **Appearance → Theme File Editor → footer.php** (or use a plugin like *Insert Headers and Footers* to avoid touching theme files)
2. Paste the Chekkit widget snippet just before `</body>`
3. Save

### Option B — Page-specific
If you only want Chekkit on these 6 landing pages, install the *Insert Headers and Footers* plugin (or *WPCode*) and use the per-page injection feature.

### Routing per page (optional refinement)
Chekkit's dashboard lets you map incoming messages to specific store inboxes. If their interface supports per-page tagging, configure each spoke page to tag incoming messages with the originating city. Otherwise, the URL the message came from is visible to your team in the message metadata.

### Tracking Chekkit events (optional)
The landing page JS already includes a commented-out block for `chekkit:open` and `chekkit:message_sent` events. Check Chekkit's developer docs for the exact event names they emit, then update the JS in the master template (and re-run `generate_store_pages.py`).

---

## Step 4 — Google Analytics 4 + Google Tag Manager

The landing pages already fire structured events through `window.gtag()` and `window.dataLayer`. You just need GA4 wired up.

### If you already have GTM + GA4 installed site-wide
The events will flow automatically. Go to **GA4 → Admin → Events** and you should start seeing:
- `page_view`
- `calc_started`
- `calc_quoted`
- `cta_call_click`
- `cta_text_click`
- `calc_text_offer`
- `scroll_25` / `scroll_50` / `scroll_75`
- `bounce_after_quote` (via dataLayer, set up the GTM trigger separately)
- `faq_open`

Mark the conversion events in GA4 (**Admin → Events → mark as conversion**):
- `cta_call_click`
- `cta_text_click`
- `calc_text_offer`
- `chekkit_message_sent`

See `TRACKING_PLAN.md` for the full GTM trigger/tag setup.

### If you don't have GA4 yet
Easiest path: install **Site Kit by Google** plugin, connect GA4. Then add a GTM container, route GA4 through GTM, and import the trigger configuration from `TRACKING_PLAN.md`.

---

## Step 5 — Sitemap + Search Console

1. If using Yoast/RankMath, the new pages appear in the XML sitemap automatically.
2. Go to **Google Search Console** → select `thevalleypawn.com` property
3. **Sitemaps** → confirm your sitemap (usually `sitemap_index.xml`) is listed and recently fetched
4. **URL Inspection** → paste each of the 6 new URLs in turn → click **Request Indexing**
5. Repeat over the next 7–10 days; Google may take 1–4 weeks to fully rank, but indexing should happen in days.

---

## Step 6 — Internal Linking from Existing Pages

Plant contextual internal links from existing high-traffic pages to the new landing pages. Examples:

| From (existing page) | Link to | Anchor text suggestion |
|---|---|---|
| Homepage hero or services strip | `/sell-gold/` (hub) | "We buy gold" |
| Each location page (existing) | matching `/sell-gold-[city]/` | "Sell your gold at our [City] store →" |
| Any "What we do" / about page | `/sell-gold/` | "Gold buying" |
| Footer (sitewide) | `/sell-gold/` | "Sell Gold" |

---

## Step 7 — Google Business Profile Posts

Within 48 hours of launch, post once on each store's GBP, linking to that store's spoke page. Use compliant tone (per `valley-pawn-context` GBP guidelines):

**Sample (Culpeper):**
> Curious what your old gold is worth? Our new live gold calculator gives you an honest estimate in seconds — based on today's actual spot price. Try it, then text or stop in to confirm your offer. Walk out with cash the same day. Family-owned, fair appraisals since 2014.

Add the spoke URL in the **Action button → Learn more**. Same pattern across all 5 stores, but rewrite the body so each post is unique (Google penalizes duplicate GBP content).

---

## Step 8 — Email Campaign

Use Brevo to announce the calculator to the existing list:
- Subject: *"Curious what your gold is worth? Try our new calculator."*
- Body: short, 3-line intro + a single CTA button to `/sell-gold/`
- Follow the standard email requirements from `valley-pawn-context` — logo header, all-5-store directory at the bottom, hours line at the foot.

---

## Step 9 — Operational: Update Spot Price Weekly

The calculator uses a global JavaScript variable, `window.VP_GOLD_SPOT`, defaulted to **$4,500/oz** (current as of 2026-05-21).

Gold moves. To keep offers accurate:

1. Once a week (Monday morning works well), check kitco.com or apmex.com for the current spot
2. **Pages → [each spoke page] → Edit**
3. In the Custom HTML block, find the line:
   ```js
   window.VP_GOLD_SPOT = window.VP_GOLD_SPOT || 4500;
   ```
4. Update `4500` to the current spot
5. Update on the 6 pages (hub + 5 spokes)

### Want to automate this?
Two paths:
- **Easy:** add a small WordPress snippet that fetches the current spot from a free API (e.g. metals-api.com free tier) once daily and writes the value to a `wp_options` entry, then echoes that value into the page header. Ask and I'll build it.
- **Easiest:** set the variable at the WordPress level via a single shortcode/snippet that all 6 pages reference. Then weekly updates are one edit, not six.

---

## Step 10 — Post-Launch: First 7 Days

| Day | Action |
|---|---|
| 0 | All 6 pages published, Chekkit live, GA4 events firing, sitemap submitted |
| 1 | Request indexing for all 6 URLs in Search Console |
| 1 | GBP post on each store (5 unique posts, no duplicates) |
| 2 | Brevo email blast announcing the calculator |
| 3 | Instagram Reel + 5 Facebook page shares |
| 5 | Check GA4 Real-Time — confirm `calc_quoted` and `cta_text_click` events firing |
| 7 | First weekly metrics review — open `TRACKING_PLAN.md` dashboard |

---

## Troubleshooting

**Calculator shows $0 or NaN.**
The weight input may have a comma or decimal-format issue. Confirm the input is set to `type="number"` and `inputmode="decimal"`. The template handles this — only an issue if WordPress has stripped/altered the markup.

**The Custom HTML block is stripping `<script>` tags.**
This happens on some WP installs with aggressive security. Use the *Insert Headers and Footers* or *WPCode* plugin instead, or paste the page into a `page-sell-gold-[city].php` template file in your child theme.

**Sticky mobile CTA covers content on tablets.**
The CTA only appears below 640px (`max-width: 640px`). If a tablet shows it, adjust the breakpoint in the inline CSS.

**Map embed shows wrong location.**
The embed uses `https://www.google.com/maps?q=Valley+Pawn+[City]+VA&output=embed` — the same business+city pattern as the canonical Maps URLs in `valley-pawn-context`. If wrong location shows, verify the GBP listing for that city.

**Phone numbers misformatted.**
All `tel:` and `sms:` hrefs use `+1` country code + 10 digits. If your carrier requires a different format, adjust the master template and re-run `generate_store_pages.py`.

---

## Phased Launch — 4-Category Rollout

Don't dump all 24 pages at once. Google flags large content drops as low-quality. Stagger:

| Wave | Week | Category | Pages | Why this order |
|---|---|---|---|---|
| 1 | Week 1 | **Gold** (hub + 5 spokes) | 6 | Highest search demand, broadest commercial intent |
| 2 | Week 3 | **Jewelry** (hub + 5 spokes) | 6 | High lead value; drafts off gold ranking momentum |
| 3 | Week 5 | **Coins** (hub + 5 spokes) | 6 | Specialty intent; numismatic SEO is its own niche |
| 4 | Week 7 | **Silver** (hub + 5 spokes) | 6 | Smallest market but high-margin and easy to dominate |

Between waves: monitor GA4, confirm indexation in Search Console, run a Brevo email blast and 5-store GBP post round each time.

### Weekly Spot Price Update (after multi-category launch)

You now have **two** spot prices to keep current:

- `window.VP_GOLD_SPOT` (used by gold, jewelry, coins-gold-eagle calcs) — set ~weekly off kitco.com
- `window.VP_SILVER_SPOT` (used by silver and coins calcs) — set ~weekly off kitco.com

You can hoist both into the WordPress header once via a snippet plugin (e.g. WPCode), so all 20 store pages share one source of truth:

```html
<script>
window.VP_GOLD_SPOT = 4500;    // update weekly
window.VP_SILVER_SPOT = 76;    // update weekly
</script>
```

Drop that into a site-wide header injection and you update twice a week in one place instead of 24 page edits.

---

## Final Verification Checklist (Per Wave)

Before considering each wave's deploy complete:

- [ ] All 6 pages of the wave live, accessible at the expected URLs
- [ ] Each page passes the Mobile-Friendly Test (Search Console)
- [ ] Each page passes the Rich Results Test — LocalBusiness + FAQ schema valid
- [ ] Calculator math sanity check by category (at $4,500 gold / $76 silver):
  - Gold/Jewelry: 14k 5g → ~$295–$359
  - Silver: Sterling 100g → ~$158–$192
  - Coins: 10 silver quarters → ~$103–$124 · 1 Silver Eagle → ~$57–$68 · 1 Gold Eagle → ~$3,375–$4,050
- [ ] Cross-category links work — clicking "Sell Silver" on a gold page lands on the matching silver page for the same city
- [ ] Text "Test text" to each store number — confirm it lands in Chekkit
- [ ] GA4 Real-Time shows `calc_quoted` event firing with the correct `category` parameter (gold/silver/coins/jewelry)
- [ ] GBP posts published, all 5 unique per category wave
- [ ] All pages added to the WordPress menu under "Sell to Us"
- [ ] Email scheduled in Brevo announcing the new category
- [ ] Spot price config (gold + silver) live in WP header snippet
- [ ] Weekly spot-price update reminder scheduled
