# Valley Pawn — Listing Management: Audit + Rebuild Plan ("Listings OS")
**Prepared:** 2026-09-05 · **Status:** PLAN — awaiting Joshua's go (nothing built or changed yet)
**Domain:** 1 — Full Circle Finance Inc DBA Valley Pawn
**Scope:** Google Business Profile, Apple Business Connect, Bing Places, Yelp, Facebook Pages, BrightLocal + data aggregators, MapQuest/YP/BBB/GPS long tail, AI-search visibility, Google reviews (Chekkit), website NAP/schema.

---

## 1. What exists today (verified against files, Slack output, and email — not run records)

### 1a. Execution inventory
| Lane | Task / skill | Cadence | Method | Output | State |
|---|---|---|---|---|---|
| Presence | `vp-presence-audit-weekly` | Sun 4:20 PM | curl + Chrome + WP REST | #ai-marketing, `presence_scorecard_latest.json`, `PRESENCE_HISTORY.csv` | ✅ running (8/23, 8/25, 8/30) |
| Presence | `vp-ai-search-health-check` | Mon 6:10 AM | Chrome (public Google/Bing maps) | #ai-marketing | ✅ running; Bing console "couldn't verify" every run |
| Presence | `vp-ai-search-autofix` | Mon 8:30 AM | browser + WP writes (whitelist) | #ai-marketing + Autofix Log sheet | ✅ running |
| AI | `vp-ai-visibility-metrics` | Fri 6:30 AM | Chrome across 5 AI engines + GA4 | #ai-marketing + Sheet | ✅ running (83% index 8/28) |
| AI | `vp-ai-visibility-autofix` | Fri 9:30 AM | browser | #ai-marketing | ✅ running |
| Website | `weekly-website-health-audit` | Mon 5:15 AM | crawl + WP REST | #website | ✅ running |
| Rollup | `marketing-ceo-briefing-weekly` | Mon 11:30 AM | Slack read | Joshua DM | ✅ running |
| Reviews | `chekkit-new-review-alert`, `nightly-chekkit-review-responses`, `chekkit-unanswered-*`, `review-obtained-last-week` (+watchdog), `chekkit-weekly-review-requests` | hourly / nightly / weekly | Chekkit UI (browser) | #google-reviews, #chekkit-* | ✅ running |
| GBP posts | Publer via `vp-content-batch` + quota watchdog | 7 posts/wk/store | Publer API | 5 store GBP pages | ✅ running; "do GBP text posts actually render" still unverified |
| **Directory NAP audit (Big-5)** | `brightlocal-weekly-sync-alerts-check` → skill `directory-listing-monitor` | Tue 9 AM | Chrome | #ai-marketing | ❌ **archived 8/21, never replaced.** Skill never scheduled on its own. |
| Change broadcast | skill `directory-listing-push` | on demand | Chrome (15 admin consoles) | #claude-notifications (dead channel) | ⚠️ never run; stale |
| Long tail | BrightLocal (Citation Builder + Active Sync) | annual (~$250) | SaaS | email alerts to jdavis@ | ⚠️ **aggregator listings for VALLEYPAWN-24450 (Lexington) EXPIRED 2026-08-08** — three renewal emails 7/9, 7/25, 8/7, then expiry 8/9. Nobody acted; not logged anywhere. |

**Zero APIs are used anywhere in this department.** Every read is a browser scrape or `curl` of a public page; every write is console-driving. There is no GBP API, Yelp API, Apple API, or Bing API client, key, or OAuth in the estate (grep-verified). Zero native launchd agents own any listing work.

### 1b. What's actually broken (ranked by customer impact)
1. **The weekly Big-5 NAP audit does not run.** Apple Business Connect, Yelp, and Facebook NAP are checked by nothing on a schedule. Google + Bing are checked by the Monday health check only — and Bing is checked on the public map surface that was ruled non-diagnostic on 8/3 ("five weeks of misattributed drift").
2. **The same 8–10 "needs Joshua" items have been re-reported weekly for 8+ weeks by four different tasks** (MapQuest "Dixie Pawn Inc." 410128854 · Yext feed · GBP Harrisonburg "Ste 22" · Apple suite numbers · YP Harrisonburg/Roanoke rename · Yelp Staunton ghost + Waynesboro duplicate · 9-listing phantom Staunton cluster · BBB three fragmented profiles + unanswered complaint (B−) · Bing Harrisonburg lead photo). Reporting throughput is high; closure throughput is zero. Every cloud-side attempt to file a form hit a privacy/permission gate and wrote "BLOCKED" back into the checklist.
3. **Long-tail seeding has lapsed.** BrightLocal was kept (7/22 decision) precisely for aggregator seeding; the Lexington aggregator submissions expired 8/8. The Roanoke location in BrightLocal still carries the legacy reference `GOLD-N-PAWNA-24017-1621` (6/29 sync-acceptance email; display name there is already "Valley Pawn, Roanoke"). Whether any aggregator payload still carries the old name is a plausible source for Gemini/ChatGPT resurfacing "Gold-N-Pawn" for Roanoke (8/21, 8/28 scorecards) — needs a console look at what was actually submitted, not a guess.
4. **The canon contradicts itself** — and every task reads the canon:
   - Harrisonburg "Ste 22": BUSINESS_OS 6/22 says canonical; presence scorecard + health check say defect; Bing Places still holds it (8/3, "correct"); GBP still shows it (8/31). Website purged it 8/23.
   - Apple Business Connect: 7/22 docs say "unclaimed, Dixie only"; 8/3 console check says "claimed, all 5 Verified, no Dixie"; 8/22 audit and 8/30 scorecard revert to "unverified/needs claim."
   - "Gold-N-Pawn"/"GNP Pawn" is banned only inside one task's prompt — `valley-pawn-context` never mentions it.
   - Staunton (sold July 2026, now Smart Pawn) and Salem (folded into Roanoke) are undocumented in canon; two tasks still list Staunton as a live store.
   - Waynesboro went Wednesday-open 7/29; `llms.txt` and `city-answer-snippets.md` still say closed Wed / "Culpeper is the only store open Wednesday." That is NAP drift in our own AI-facing files and no audit flags it.
5. **Measurement is soft.** Review counts "carried, not re-verified" (8/30). Yelp/BBB/GunBroker/Manta 403 the scraper → "UNVERIFIED." Bing "5/5 clean" measured on the wrong surface. Snapshot cache path in `directory-listing-monitor` points at a dead session mount, so week-over-week diffing never worked.
6. **Skills are stale.** Both listing skills post to `#claude-notifications` (does not exist), tell the runner to ask Joshua to log in (violates Rule 2), and lack the 3-bucket classification (listing defect / render mismatch / foreign listing) that the health check learned the hard way.
7. **No guardian net** on `chekkit-weekly-review-requests`, `nightly-chekkit-review-responses`, or either autofix task; no listing publication row in `PUBLICATION_CALENDAR.md`.

### 1c. What's working and must not be touched (Rule 4)
Visibility Index lane (63% → 83% in 5 weeks); website Tier-1 remediation (0 "dixie" pages, 0 broken JSON-LD, 5-store footer NAP); Chekkit review loop (1,561 reviews, 4.88 avg); Publer GBP/FB cadence; `fleet/expected_outputs.json` guardian.

---

## 2. Expert board

🧑‍⚖️ **EXPERT BOARD — How should Valley Pawn's listing management run so it "just works"?**

**PANEL:** local-SEO/martech engineer · SRE/automation lead (owns the launchd + guardian pattern) · brand-risk reviewer (legacy names, customer-facing accuracy)

**OPTIONS WEIGHED**
- **A. Patch the current browser-driven tasks** (re-register the archived Tuesday audit, fix the skills). For: cheapest today. Against: keeps every read on scrape-able public surfaces that 403, render wrong, or change DOM; keeps every fix behind a permission classifier; the "needs Joshua ×8 weeks" loop stays.
- **B. Buy a listings platform** (Yext / Semrush Listings / Moz Local, roughly $200–$400 per location per year). For: aggregator push + monitoring in one place. Against: $1,000–2,000/yr for 5 stores, does not touch MapQuest disputes, BBB, Yelp duplicates, or AI-engine answers; we would still need our own monitoring; and a Yext feed is already the suspected source of the bad syndicated description.
- **C. API-first native engine + thin Cowork posters** (the `daily-funds-verification` / `format_aged_inventory.py` pattern). For: deterministic reads from the actual source of record (GBP API, Yelp Fusion, Apple Business Connect API, Google Places), zero tokens for the audit itself, Rule-18 withhold gates, week-over-week diffs that survive sessions, and a state machine that closes items instead of re-reporting them. Against: one-time API enrollment (GBP API access request, Apple enrollment) needs Joshua's accounts; ~2 build weeks.

**DECISION:** **C**, with A's skill fixes folded in as week-one hygiene, and B rejected except for a one-time aggregator renewal through the BrightLocal account we already have.
Why: the failures above are not cadence failures — they are *method* failures (scraping instead of reading the record; reporting instead of closing). Only C changes the method.

**REJECTED**
- Re-registering `brightlocal-weekly-sync-alerts-check` as-is: it would post the same unverifiable scrape a fourth time.
- A new listings SaaS: cost without closing the actual blockers.
- Deleting or "cleaning up" the presence/health tasks now: additive first; retire duplicated sections only after two clean weeks of the new post.

**FOR JOSHUA (genuinely yours):** three money/account items in §5. Everything else proceeds additively on your go.

---

## 3. Target architecture — "Listings OS"

```
canonical_nap.json  ──►  listings_engine.py (native, launchd, Sunday)  ──►  listings_state.json
      ▲                       │ reads: GBP API · Yelp Fusion · Places API · Apple BC API      │  LISTINGS_HISTORY.csv
valley-pawn-context           │        HTTP grep of long-tail URLs (legacy strings)           │  legacy_register.json (state machine)
(single source)               │ writes: GBP (NAP/hours/photos/posts/reviews) · Apple BC       ▼
                              └────────────────────────────────────────►  format_listings_post.py → exit 0 body / exit 2 withhold
                                                                                   │
                                                          Cowork task `listings-weekly-post` (thin) ──► #ai-marketing  (+ guardian marker)
```

**1. One canonical file.** `Listing Management/canonical_nap.json` generated from `valley-pawn-context`: 5 stores (name, address, phone, hours incl. Waynesboro Wed-open, website, categories, description, social URLs), a **kill-list** (`Dixie Pawn`, `Gold-N-Pawn`, `GNP`, `Salem`, `Staunton`/`817 Richmond`, `641 James Madison`, `439 E Nelson`, `313 West Main`, `Ste 22`, `1790 Toni`), and **accepted variants** (`2362-D` on ATF/FFL records; Roanoke public-map render without Suite C; Harrisonburg TomTom "Toni St" render). Every task and skill reads this file; canon text in the skill is updated to match (Gold-N-Pawn ban, Staunton sold, Salem folded, Harrisonburg no suite, Roanoke C+D).

**2. API-first reads (source of record, not public render).**
- **Google Business Profile API** (account `fullcirclepawn@gmail.com`): locations (NAP, hours, attributes, description, photos), reviews + reply, local posts, performance. Bing syncs from GBP, so a clean GBP is a clean Bing. Also fixes GBP Harrisonburg "Ste 22" programmatically and verifies Publer's GBP posts actually rendered (closes the Lane C open item).
- **Yelp Fusion API** (free key): business details for the 5 stores **and** the legacy slugs (`dixie-pawn-harrisonburg`, `gold-n-pawn-roanoke`, Staunton, Waynesboro duplicate) — ends the 403/"UNVERIFIED" problem and detects the merge/rename the moment it happens.
- **Google Places API (Place Details):** review count + rating for us and the named rivals in all 5 markets (Roanoke gap becomes a real weekly number, ~10 calls/week, effectively $0).
- **Apple Business Connect API** (enrollment under the existing Apple Business account "Full Circle Finance inc."): read/write all 5 locations — fixes the three address defects and makes Apple part of the weekly audit for the first time. Fallback if enrollment stalls: monthly signed-in console pass.
- **Bing Places:** treated as a GBP mirror. Monthly signed-in console verification (local session) only; public bing.com/maps is never scored again.
- **Long tail** (MapQuest, YP/Superpages/DexKnows, BBB ×3, Nextdoor, Loc8NearMe, chamberofcommerce.com, CitySquares, Manta, PawnBat, pawnshops.net, FFLs.com ×2, MasterFFL, Arms Directory, Waze pin): plain HTTP fetch (Googlebot UA where the site allows it) + kill-list grep. Cheap, deterministic, no browser.

**3. Native engine, zero Claude tokens for the audit.** `bin/listings_engine.py` (Python, stdlib + requests) under `com.valleypawn.listings-audit` (Sunday 3:00 PM, before the presence audit). Writes `listings_state.json`, appends `LISTINGS_HISTORY.csv`, and emits the Slack body through `format_listings_post.py` (deterministic table; **exit 2 = post nothing** if any Big-5 source is missing — Rule 18). Any UNVERIFIED cell says so; nothing is "carried."

**4. Legacy-listing register with a state machine.** `legacy_register.json`: one row per ghost/legacy listing (platform, URL/ID, defect, status ∈ {live, reported, pending-moderation, verified-gone, accepted}, action taken + date, next-check date, owner). The engine re-checks every row weekly and flips status automatically when the page changes. "Needs Joshua" becomes a queue with ageing, delivered **once a month as one DM** (not weekly from four tasks). Rule 16 applies: no technical detail in Slack.

**5. One weekly publication.** `LISTINGS & PRESENCE — {date}` in #ai-marketing (Sunday) with three fixed sections: Big-5 NAP (5×5 grid, ✅/❌/❓ with the defect named), Legacy register (live / reported / gone counts + deltas), Reviews position (5 markets, us vs rival, weekly delta). Registered in `PUBLICATION_CALENDAR.md` and `fleet/expected_outputs.json` on day one. After two clean weeks the duplicated listing sections in `vp-presence-audit-weekly` and `vp-ai-search-health-check` are pointed at `listings_state.json` instead of re-scraping (additive edit with backups; the tasks keep their other jobs).

**6. Change propagation (`directory-listing-push` v2).** A change to `canonical_nap.json` → engine diff → GBP + Apple written via API, Yelp/Facebook/Bing via a local browser session, long-tail via BrightLocal Citation Builder (one-time aggregator submission per location) — with the register tracking each platform's propagation until verified.

**7. Reviews & schema tie-in.** Engine's live review counts feed a small WP snippet emitting `aggregateRating` on the 5 `/locations/{city}/` pages (currently 0 occurrences sitewide while the homepage claims 4.9★). GBP API reply path becomes the fallback for `nightly-chekkit-review-responses` when Chekkit's UI is down.

---

## 4. Cadences (steady state)
| When | What | Layer |
|---|---|---|
| Sunday 3:00 PM | Full Big-5 + long-tail audit, legacy register recheck, review position → `LISTINGS & PRESENCE` post | native launchd + thin Cowork poster |
| Monday (existing) | AI-search health check (schema/llms.txt) reads `listings_state.json` for its NAP section | existing task, additive edit later |
| Friday (existing) | AI Visibility scorecard — unchanged | existing |
| 1st of month | Signed-in console pass: Bing Places + Apple BC (until API) + BrightLocal citation report; one consolidated "needs Joshua" DM | local Cowork task |
| Quarterly | Deep long-tail sweep (40+ directories) + FFL directory block (per `Compliance/FFL_LISTINGS_STATUS.md`) + competitor benchmark refresh | native, extra list |
| On change | `directory-listing-push` v2 | on demand |
| Annual (Aug) | BrightLocal aggregator renewal decision, logged in the register 30 days ahead | register reminder |

---

## 5. Decisions that are Joshua's (money / accounts) — everything else I own
1. **BrightLocal.** Aggregator listings for Lexington expired 8/8; the other four locations' expiry dates need a console read. Recommendation: fix the Roanoke location record (drop the Gold-N-Pawn identity), then renew aggregator submissions for all 5 once (price shown at checkout in the BrightLocal dashboard — historically the whole account ran ~$250/yr), and drop the monitoring tier once the engine is live. Alternative: let it lapse entirely and rely on the engine + direct claims. **Your call on the spend.**
2. **API enrollment (free, one-time, your accounts):** GBP API access request on a Google Cloud project under `fullcirclepawn@gmail.com` (Google approves in days); Yelp Fusion key (instant); Apple Business Connect API enrollment (Apple Business account). I prepare everything; you approve the consent screens.
3. **One 30-minute signed-in sitting** (local session, you at the keyboard once): MapQuest Culpeper flag + Dixie 410128854 dispute; GBP Harrisonburg "Ste 22" removal (if the API isn't approved yet); Apple three address fixes; YP rename resubmits; Yelp Staunton ghost + Waynesboro duplicate escalation; BBB claim/merge + respond to the open complaint; Bing Harrisonburg lead photo; BrightLocal Roanoke rename. This one sitting closes 9 of the 10 items that have been re-reported for two months.

---

## 6. Build sequence (additive, reversible, proven before it posts)
**Phase 0 — this week (no code):** canon fixes in `valley-pawn-context` + `llms.txt` + `city-answer-snippets.md` (Waynesboro Wed, Gold-N-Pawn, Staunton/Salem, Harrisonburg no suite); `canonical_nap.json`; `legacy_register.json` seeded from the 8/30 scorecard + ACUTE-FIXES-CHECKLIST; both listing skills corrected (channel, login rule, snapshot path, classification, canonical file); Open Items Register rows; the 30-minute sitting scheduled.
**Phase 1 — week 2:** engine v1 (Yelp Fusion + Places + long-tail grep + register recheck) proven on the island; `format_listings_post.py` with withhold gate; launchd plist staged; first post to #ai-marketing; calendar + guardian rows.
**Phase 2 — week 3:** GBP API online (NAP/hours/reviews/posts verification; Ste 22 fixed via API); Apple API or console pass; presence/health tasks pointed at `listings_state.json` (backups kept).
**Phase 3 — week 4:** aggregator renewal executed; `aggregateRating` snippet; `directory-listing-push` v2; monthly console task registered; BUSINESS_OS + CHANGELOG updated; archived stale task files annotated.
**Definition of done:** two consecutive Sunday posts with 25/25 Big-5 cells verified (no ❓), legacy register trending to zero with every remaining row in `reported`/`pending` (not `live`), and the "needs Joshua" DM under 3 items.

---

## 7. Sources read for this plan
Project knowledge: `ACUTE-FIXES-CHECKLIST.md`, `DIRECTORY-MANAGEMENT-LONG-TERM-STRATEGY.md`, `ONLINE-PRESENCE-AUDIT-2026-07-22.md`. Skills: `directory-listing-monitor`, `directory-listing-push`, `valley-pawn-context`, `enterprise-map`, `expert-review-board`. Files: `Valley Pawn OS/CHANGELOG.md`, `BUSINESS_OS.md`, `PUBLICATION_CALENDAR.md`, `fleet/expected_outputs.json`, `Life OS/OPEN_ITEMS_REGISTER.md`, `Ai Optimized Marketing/AI-Search-GEO/*` (incl. `presence/` scorecards + history), `Website/AUDIT_2026-08-22/*`, `Refine Social Media/*` (GBP cadence), `Compliance/FFL_LISTINGS_STATUS.md`. Scheduled tasks (registry + SKILL.md via osascript): all 9 listing/presence/AI tasks, 7 review tasks, 4 archived tasks. Slack `#ai-marketing` (8/21 → 9/5 posts, read directly). Email (unified-search): BrightLocal renewal/expiry thread 7/9–8/9, Apple Business Connect insights, no Yext or MapQuest correspondence on file.
