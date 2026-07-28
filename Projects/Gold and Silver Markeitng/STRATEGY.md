# Valley Pawn — "We Buy Gold" Landing Page Strategy

**Goal:** Generate gold-buy leads (calls, texts, walk-ins) from local search traffic across the 5 store catchments by deploying 5 high-converting, locally-optimized landing pages on `thevalleypawn.com` that combine an open-access gold calculator with SMS-first lead capture.

---

## 1. Hosting & URL Strategy

### Recommendation: Subfolders on `thevalleypawn.com` (not subdomains, not a microsite)

**Why:**
- `thevalleypawn.com` already has domain authority, GBP citations, and an existing index footprint. Subfolders inherit all of that authority directly. A new microsite would start from zero and take 6–12 months to rank.
- Subdomains are treated by Google as semi-separate properties — they fragment authority. Subfolders consolidate it.
- WordPress handles subfolder pages natively with no plugin gymnastics.

### URL Architecture — Hub + Spoke

```
/sell-gold/                        ← HUB: non-geo "we buy gold" page
  ├── /sell-gold-culpeper/         ← SPOKE 1
  ├── /sell-gold-waynesboro/       ← SPOKE 2
  ├── /sell-gold-harrisonburg/     ← SPOKE 3
  ├── /sell-gold-lexington/        ← SPOKE 4
  └── /sell-gold-roanoke/          ← SPOKE 5
```

**Why this pattern:**
- The hub captures non-geo and broad queries: *"sell gold virginia,"* *"valley pawn gold,"* *"sell gold near me"* (when location is ambiguous).
- The 5 spokes capture geo-specific queries: *"sell gold harrisonburg va,"* *"we buy gold roanoke,"* *"cash for gold lexington."*
- Internal links from spokes → hub → spokes pass authority efficiently through the cluster.
- Avoid deeper paths like `/locations/sell-gold/culpeper/` — too deep, keyword distance hurts ranking, breadcrumb dilution.

### URL slug rule
Use `sell-gold-[city]` (verb + noun + city) rather than `[city]-gold` or `we-buy-gold-[city]`. Reason: search behavior heavily favors the verb "sell" in transactional queries (people who want to sell type "sell gold," not "buy gold").

---

## 2. Per-Store Targeting — ZIP Codes & Demographics

Valley Pawn's ideal customer profile from `valley-pawn-context`: working-class corridors, $30K–$50K median HHI, higher poverty rates, military proximity, growing population. The ZIP plans below are sequenced from primary catchment outward, weighted by drive time and demographic fit.

### 1. Culpeper — `/sell-gold-culpeper/`
**Store:** 571 James Madison Highway, Culpeper, VA 22701 · (540) 445-5510

| Tier | ZIPs | Notes |
|---|---|---|
| **Primary** | 22701 | Town of Culpeper — direct catchment |
| **Secondary** | 22714, 22729, 22735, 22737, 22741 | Brandy Station, Mitchells, Reva, Rixeyville, Stevensburg — Culpeper County |
| **Tertiary** | 22727, 22732, 22747, 22942, 22960 | Madison, Locust Dale, Sperryville, Gordonsville, Orange |

**Local hook:** Culpeper is a Northern Piedmont growth corridor — proximity to Quantico/Warrenton drives military/contractor traffic. Position around *"trusted local gold buyer — drive less than 30 minutes from Madison, Orange, Brandy Station, Sperryville."*

**Key competitors (Culpeper market):** very few dedicated gold buyers; mostly traveling buyers and Northern VA jewelry chains. **Major opportunity — low local supply, high search demand.**

---

### 2. Waynesboro — `/sell-gold-waynesboro/`
**Store:** 1321 West Broad Street, Waynesboro, VA 22980 · (540) 221-6346

| Tier | ZIPs | Notes |
|---|---|---|
| **Primary** | 22980 | Waynesboro city |
| **Secondary** | 22939, 24477, 24431, 22952 | Fishersville, Stuarts Draft, Crimora, Lyndhurst |
| **Tertiary** | 24401, 22920, 22922, 24440 | Staunton, Afton, Batesville, Greenville |

**Local hook:** I-64 / I-81 corridor — accessible from both Staunton and Charlottesville. Position around *"the closest fair gold buyer to Staunton, Fishersville, Stuarts Draft."* Avoid C'ville-direct keyword targeting (too competitive) — instead capture the *"closest to me"* searcher in the Augusta County triangle.

---

### 3. Harrisonburg — `/sell-gold-harrisonburg/`
**Store:** 1790 East Market Street, Harrisonburg, VA 22801 · (540) 574-4500

| Tier | ZIPs | Notes |
|---|---|---|
| **Primary** | 22801, 22802 | Harrisonburg city core |
| **Secondary** | 22812, 22821, 22815, 22840, 22846, 22853 | Bridgewater, Dayton, Broadway, McGaheysville, Penn Laird, Timberville |
| **Tertiary** | 22827, 22841, 22842, 22835 | Elkton, Mt. Crawford, Mt. Jackson, Linville |

**Local hook:** Largest urban catchment in the 5-store network; JMU population brings transient gold-jewelry sellers (grad gifts, broken pieces). **Critical:** zero "Dixie Pawn" references on page or in schema — this is Valley Pawn-Harrisonburg.

**Key competitors:** Pawn Emporium, The Velvet Case, Henebry's Diamond, several coin shops. **Differentiator messaging:** real-time appraisal calculator + 5-store buying power = better offers than coin-shop-only buyers.

---

### 4. Lexington — `/sell-gold-lexington/`
**Store:** 125 Walker Street, Lexington, VA 24450 · (540) 461-8349

| Tier | ZIPs | Notes |
|---|---|---|
| **Primary** | 24450 | Lexington |
| **Secondary** | 24416, 24555, 24578, 24435, 24472 | Buena Vista, Glasgow, Natural Bridge, Fairfield, Raphine |
| **Tertiary** | 24439, 24483, 24579 | Goshen, Vesuvius, Newport |

**Local hook:** Smaller market, but Rockbridge County customers will drive 30+ minutes for a fair offer. Capture *"sell gold near me"* + *"sell gold rockbridge county"* + *"sell gold buena vista."* Lean into local heritage — VMI/W&L community, family-owned-since-2014 plays well here.

---

### 5. Roanoke — `/sell-gold-roanoke/`
**Store:** 2362 Peters Creek Road, Suite C, Roanoke, VA 24017 · (540) 562-0776

| Tier | ZIPs | Notes |
|---|---|---|
| **Primary** | 24017, 24012, 24013, 24014, 24015, 24016, 24018, 24019 | All Roanoke city ZIPs |
| **Secondary** | 24153, 24179, 24083, 24175 | Salem, Vinton, Daleville, Troutville |
| **Tertiary** | 24070, 24090, 24018 | Catawba, Cloverdale, Cave Spring |

**Local hook:** Most competitive market in the network — Gold-N-Pawn, multiple coin shops, several pawn competitors. **Differentiator:** transparent live calculator (most competitors hide their math) + the 30-day warranty trust signal + 5-store buying power.

**Critical Roanoke rule (from `valley-pawn-context`):** This page must NOT mention firearms or weapons anywhere. Focus exclusively on gold, silver, coins, scrap, jewelry — never reference the firearms side of Roanoke inventory on this page or in any meta description.

---

## 3. Keyword Strategy — Per-Page Target Set

Each spoke page targets one **primary money keyword**, 3 **secondary keywords**, and a long-tail cluster.

### Money keyword pattern (highest commercial intent)
`sell gold [city] va` · `we buy gold [city]` · `cash for gold [city]`

### Secondary keywords per page
- `where to sell gold [city]`
- `[city] gold buyer`
- `sell gold jewelry [city] va`
- `sell scrap gold [city]`

### Long-tail capture (FAQ + body copy)
- `how much is my gold worth`
- `gold price per gram today`
- `sell broken gold jewelry`
- `sell gold coins [city]`
- `sell wedding ring [city]`
- `sell 14k gold near me`
- `how do pawn shops appraise gold`
- `do I need an appointment to sell gold`

### Hub page targets
`sell gold virginia` · `shenandoah valley gold buyer` · `valley pawn gold` · `we buy gold near me`

---

## 4. Page Architecture — Conversion-First Layout

The above-the-fold zone must show the visitor that they're (a) in the right place, (b) talking to a real local business, and (c) can get an offer right now without filling out a form. The gold calculator is the centerpiece.

```
┌─────────────────────────────────────────────────┐
│ HEADER: Valley Pawn logo · Phone · Text          │
├─────────────────────────────────────────────────┤
│ H1: We Buy Gold in [City], VA                    │
│ Subhead: Family-owned since 2014 ·               │
│   Walk out with cash today                       │
│ [📞 Call (540) XXX-XXXX] [💬 Text (540) XXX-XXXX]│
├─────────────────────────────────────────────────┤
│  ╔═══════════════════════════════════════════╗  │
│  ║   LIVE GOLD CALCULATOR                    ║  │
│  ║   Karat: [10k 14k 18k 22k 24k]            ║  │
│  ║   Weight: [______] [grams/dwt/oz]         ║  │
│  ║                                            ║  │
│  ║   Your estimated offer range:             ║  │
│  ║   $XXX – $YYY                             ║  │
│  ║                                            ║  │
│  ║   [Text me this offer →]                  ║  │
│  ╚═══════════════════════════════════════════╝  │
├─────────────────────────────────────────────────┤
│ HOW IT WORKS — 3 steps with icons               │
├─────────────────────────────────────────────────┤
│ WHY VALLEY PAWN — trust signals                 │
│ (warranty, family-owned, modern tech)           │
├─────────────────────────────────────────────────┤
│ WHAT WE BUY — gold types grid                   │
├─────────────────────────────────────────────────┤
│ REVIEWS — social proof                          │
├─────────────────────────────────────────────────┤
│ THIS STORE — address, hours, map embed          │
├─────────────────────────────────────────────────┤
│ OTHER LOCATIONS — all 5 (per email standard)    │
├─────────────────────────────────────────────────┤
│ FAQ — long-tail keyword capture                 │
├─────────────────────────────────────────────────┤
│ FINAL CTA — phone + text + Chekkit              │
└─────────────────────────────────────────────────┘
```

### Why the calculator is open (not gated)

A gated calculator (must give email/phone to see offer) lifts the form-fill conversion rate but tanks the *qualified* lead rate. Most people who would convert from a gated form will simply bounce — and they tell their friends "I had to give my info just to get a number." An open calculator builds trust, gets the prospect emotionally committed to the offer they see, and then the soft CTA captures the hot lead at peak interest. We then track bounces *after* the calculator runs as a "considered but didn't text" signal (see Section 8 — Tracking).

### Why SMS-first, not form-first

From `valley-pawn-context`: **customers text store numbers as much as they call.** Forcing them through an email form adds friction and routes the lead to an inbox no one watches in real-time. Texting the store number routes directly into Chekkit, where the team already has a tested inbox workflow.

---

## 5. Lead Capture — How Chekkit Fits

Three lead-capture surfaces on every page, ranked by intent:

1. **Header + sticky-mobile Call/Text buttons** — for visitors who already trust Valley Pawn (returning customers, those who clicked from GBP).
2. **Gold calculator → "Text me this offer" CTA** — captures the hot lead who just saw a real number and wants to act. This pre-fills an SMS with their karat/weight/offer so the conversation starts with context.
3. **Chekkit text widget (bottom-right corner)** — for the curious browser who wants to ask a question without committing. Chekkit aggregates these into the same inbox the team already uses for Google/Facebook messages, so no new workflow.

### Chekkit deployment
- Embed the Chekkit widget script on all 5 landing pages + the hub (and ideally site-wide so it follows visitors who navigate around).
- Configure routing so that messages from `/sell-gold-[city]/` pages tag with the originating city, sending to the right store's queue.
- Wire the calculator's "Text me this offer" CTA to a pre-composed SMS payload (see master template) so the team gets context, not "hi."

---

## 6. Trust & Conversion Elements (Per Page)

| Element | Purpose | Source |
|---|---|---|
| Valley Pawn logo (canonical) | Brand recognition | thevalleypawn.com/wp-content/uploads/2026/03/vp_logo_name-no-tag.png |
| "Family-owned since 2014" | Trust signal | valley-pawn-context |
| "30-day warranty on everything we sell" | Stand-behind signal | valley-pawn-context |
| "Fair, transparent appraisals" | Anti-stereotype | valley-pawn-context |
| Real Google reviews (3–5 per page) | Social proof | Pull from each store's GBP |
| Real storefront photo | Local credibility | Use canonical Maps URLs to source |
| 5-star rating badge | At-a-glance trust | GBP aggregate rating |
| LocalBusiness schema (JSON-LD) | SEO + rich result eligibility | Built into template |
| BBB / NPA badges | Industry trust | Valley Pawn is NPA member |

---

## 7. Technical SEO Checklist (Per Page)

- [ ] Unique `<title>`: `Sell Gold in [City], VA | Get a Fair Offer Today | Valley Pawn`
- [ ] Unique meta description (150–155 chars) including primary keyword + CTA
- [ ] H1 contains primary keyword + city + state
- [ ] H2s contain secondary keywords naturally (not stuffed)
- [ ] LocalBusiness + WebPage + FAQPage JSON-LD schema
- [ ] OpenGraph + Twitter card tags
- [ ] Canonical URL set
- [ ] hreflang not needed (US English only)
- [ ] Mobile-first responsive — every CTA usable with one thumb
- [ ] Core Web Vitals: LCP < 2.5s, CLS < 0.1, INP < 200ms
- [ ] Image alt text references gold/jewelry/store/city
- [ ] Internal link from hub `/sell-gold/` to each spoke
- [ ] Internal link from each spoke back to hub + to other spokes (footer)
- [ ] Page added to XML sitemap and submitted via Search Console
- [ ] Page linked from the site's main nav (under Services or Sell to Us)
- [ ] GBP "We Buy Gold" posts deep-linked to the matching spoke page

---

## 8. Conversion Tracking — Funnel & Events

The user explicitly wants to monitor conversions and bounces after calculator engagement. Here is the event schema:

| Event Name (GA4) | Trigger | Why It Matters |
|---|---|---|
| `page_view` | Default | Traffic baseline |
| `calc_started` | First input change in calculator | "Considered an offer" |
| `calc_quoted` | Calculator displays an offer | "Saw a real number" |
| `cta_call_click` | Phone button tap | Hot lead — call |
| `cta_text_click` | SMS button tap (header or footer) | Hot lead — text |
| `calc_text_offer` | "Text me this offer" tap (post-calc) | **Hottest lead** — captured at peak intent |
| `chekkit_open` | Chekkit widget opens | Browse-level lead |
| `chekkit_message_sent` | Chekkit message submitted | Confirmed lead |
| `scroll_75` | Scrolled 75% of page | Engaged but didn't convert |
| `bounce_after_quote` | Calculator quoted, then exit within 30s | **"Quote shopper" — possibly compared elsewhere** |

### Funnel definitions

- **Top of funnel:** sessions
- **Mid of funnel:** `calc_started`
- **Quote view:** `calc_quoted`
- **Conversion:** `cta_call_click` OR `cta_text_click` OR `calc_text_offer` OR `chekkit_message_sent`

### Key ratios to watch weekly
- **Quote-to-action rate** = (calls + texts + chekkits) / `calc_quoted` — if this drops below 8%, the offer math may be too low or the CTA isn't compelling enough.
- **Bounce-after-quote rate** — if > 50%, the quote may be too vague or visitors are price-shopping; consider tightening the range.
- **Calc-start rate** = `calc_started` / sessions — if < 25%, the above-the-fold isn't pulling visitors into the calculator.

Full tracking implementation lives in `TRACKING_PLAN.md`.

---

## 9. Implementation Roadmap

| Phase | Timeline | Deliverable |
|---|---|---|
| **1. Build** | Day 0 | Master template + 5 spokes + hub page ready |
| **2. Deploy** | Day 1–2 | Pages live on `thevalleypawn.com`, Chekkit embedded, GA4/GTM events firing |
| **3. Index** | Day 3–7 | Sitemap submitted, GBP posts deep-linking to spokes, internal nav links live |
| **4. Promote** | Week 2 | Email campaign drives existing customers to the calculator (Brevo) |
| **5. Iterate** | Week 4 onward | Weekly review of conversion ratios; A/B test headline + calculator payout range |

### Promotion plan (first 30 days)
1. **Brevo email** — single send to the full list announcing the calculator: *"Curious what your gold is worth? Try our new calculator and text us to lock in your offer."* Link button to `/sell-gold/` (hub).
2. **GBP posts** — one post per store, linking to that store's spoke. Soft-sell tone (per GBP guidelines in `valley-pawn-context`).
3. **Instagram** — 30-second Reel: someone bringing in scrap gold, calculator gives a number, employee counts cash. Link in bio rotates to `/sell-gold/`.
4. **Facebook (5 per-store pages)** — share the IG Reel; pin the calculator post for 14 days.

---

## 10. Files in This Project

- `STRATEGY.md` (this file) — the full strategy
- `master-landing-page-template.html` — gold master template
- `master-silver-template.html` — silver master template
- `master-coins-template.html` — coins master template
- `master-jewelry-template.html` — jewelry master template
- `store-instances/gold/sell-gold-*.html` — 5 gold spokes
- `store-instances/silver/sell-silver-*.html` — 5 silver spokes
- `store-instances/coins/sell-coins-*.html` — 5 coins spokes
- `store-instances/jewelry/sell-jewelry-*.html` — 5 jewelry spokes (20 store-level pages total)
- `generate_store_pages.py` — re-runnable generator for all 4 categories
- `WORDPRESS_DEPLOYMENT.md` — step-by-step WP deployment
- `TRACKING_PLAN.md` — GA4 + GTM + Looker Studio setup

## 10b. Category Expansion — Silver, Coins, Jewelry

The original 5-page gold plan has been extended to **4 categories × 5 stores = 20 store pages**, plus 4 category hubs. Each category targets a different searcher intent and uses a calculator tuned for that category.

### URL Architecture (expanded)

```
/sell-gold/                  ← gold hub
  ├── /sell-gold-culpeper/
  ├── /sell-gold-waynesboro/
  ├── /sell-gold-harrisonburg/
  ├── /sell-gold-lexington/
  └── /sell-gold-roanoke/

/sell-silver/                ← silver hub
  ├── /sell-silver-culpeper/
  ├── /sell-silver-waynesboro/
  ├── /sell-silver-harrisonburg/
  ├── /sell-silver-lexington/
  └── /sell-silver-roanoke/

/sell-coins/                 ← coins hub
  ├── /sell-coins-culpeper/
  ├── /sell-coins-waynesboro/
  ├── /sell-coins-harrisonburg/
  ├── /sell-coins-lexington/
  └── /sell-coins-roanoke/

/sell-jewelry/               ← jewelry hub
  ├── /sell-jewelry-culpeper/
  ├── /sell-jewelry-waynesboro/
  ├── /sell-jewelry-harrisonburg/
  ├── /sell-jewelry-lexington/
  └── /sell-jewelry-roanoke/
```

Every spoke cross-links to the 3 other categories for the same city, so a visitor on `/sell-gold-roanoke/` who has silver too sees a one-click jump to `/sell-silver-roanoke/`.

### Per-Category Calculator Logic

| Category | Calculator | Payout Range | Key Differentiator |
|---|---|---|---|
| Gold | Karat + weight → live spot math | 70–85% of melt | Open calculator, transparent math |
| Silver | Purity (.999/.925/.900/.800/40% Kennedy) + weight | 70–85% of melt | Handles flatware, sterling, junk silver in one tool |
| Coins | Multi-input (pre-1965, Kennedy 40%, Silver Eagle, Gold Eagle) → total | 75–90% of melt | Most online "coin calculators" only do one coin at a time; ours tallies a whole bag |
| Jewelry | Karat + weight (metal only) + stones-CTA | 70–85% of melt + stones extra | Sets honest expectation: metal is the floor, stones add to the offer |

### Per-Category Money Keywords

| Category | Primary Keywords | Long-tail |
|---|---|---|
| Gold | `sell gold [city] va`, `we buy gold [city]`, `cash for gold [city]` | `sell broken gold jewelry`, `sell 14k gold near me`, `how much is my gold worth` |
| Silver | `sell silver [city] va`, `sell sterling silver [city]`, `we buy silver flatware [city]` | `how much is sterling worth`, `sell silver coins [city]`, `silver buyer near me` |
| Coins | `sell coins [city] va`, `coin buyer [city]`, `sell silver dollars [city]` | `sell pre-1965 coins`, `sell silver eagles [city]`, `numismatic appraisal near me`, `where to sell coin collection` |
| Jewelry | `sell jewelry [city] va`, `sell diamond ring [city]`, `we buy jewelry [city]` | `sell engagement ring [city]`, `sell rolex [city]`, `sell estate jewelry`, `where to sell diamonds` |

### Why This Captures More Market Than Generic Lead-Gen Sites

The previous strategy doc argued against running parallel "generic gold buyer" satellite sites — Google now treats those as doorway pages and demotes them, and they can't carry GBP/local-pack signals. The category expansion captures more market the *right* way: more **intent-specific** spokes inside the existing domain. This:

1. **Multiplies keyword footprint 4×** without diluting brand authority
2. **Targets different searcher mindsets** — the jewelry seller is a different person than the bullion stacker
3. **Strengthens internal linking graph** — every page reinforces every other page
4. **Keeps everything eligible for Local Pack** — same GBP, same address, same phone
5. **Adds zero maintenance burden** — same WordPress install, same Chekkit widget, same GA4 setup, same weekly spot-price update workflow
6. **Builds a competitive moat** — competitors who only have a "we buy gold" page can't compete for `sell sterling flatware harrisonburg` queries

### Phased Launch Recommendation

Don't launch all 20 pages at once — Google may flag the dump as low-quality content. Stagger:

1. **Week 1:** Launch 5 gold spokes + gold hub (highest commercial value, broadest demand)
2. **Week 3:** Launch 5 jewelry spokes + jewelry hub (high lead value, drafts off gold ranking momentum)
3. **Week 5:** Launch 5 coins spokes + coins hub (specialty intent)
4. **Week 7:** Launch 5 silver spokes + silver hub (smallest market but valuable to capture)

Request indexing after each launch wave. Run a Brevo email blast and GBP-post round at each wave.

---

## 11. Critical Rules (Copied Forward)

These rules are enforced in every page generated for this project:

1. **No "Dixie Pawn" references anywhere** — Harrisonburg is Valley Pawn.
2. **Roanoke page never mentions firearms.**
3. **Call AND Text buttons everywhere** — both visible, both showing the phone number on the button face (per the email standard, this applies to web too).
4. **All 5 stores listed at the bottom of every page** (per the email cross-store discovery principle).
5. **Canonical Google Maps URLs only** — `maps/search/?api=1&query=Valley+Pawn+[City]+VA` — never raw-address URLs.
6. **Hours displayed correctly** — Culpeper: Mon–Sat 10am–6pm; all others: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun). No store closes at 5pm.
7. **Tone:** warm, confident, honest — never "fast cash" / predatory framing.
8. **Address format consistency** — use canonical addresses from `valley-pawn-context`; never the stale variants (313 W Main Waynesboro, 439 E Nelson Lexington, Roanoke without "Suite C").
