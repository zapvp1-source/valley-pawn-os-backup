# AI-Search / GEO — Current Status (single source; replaces the checklist + went-live files)
**Last verified:** 2026-09-05 · **Owner tasks:** `vp-ai-search-health-check` (Mon 6:10), `vp-ai-search-autofix` (Mon 8:30), `vp-ai-visibility-metrics` (Fri 6:30), `vp-ai-visibility-autofix` (Fri 9:30), `vp-presence-audit-weekly` (Sun 4:20 PM)
**Open items of record:** `../register/MARKETING_OPEN_ITEMS.json` (lane `geo`) — not this file, not the scorecard's `needs_joshua`, not any audit's §7.

> Drift protocol (from PLAN-2026-08-03, now enforced): contradiction beats omission. When something here is superseded, the old line is deleted, not layered. `README-publish-checklist.md` and `STATUS-what-went-live.md` were retired to `_archive/` on 2026-09-05 because both had gone stale (unchecked boxes for things live since 6/19; a ✅ line retracted 44 lines later).

## LIVE (verified against the site, not against our own notes)
| Asset | Since | How it's verified weekly |
|---|---|---|
| JSON-LD schema, scoped — WPCode snippet **1529** (PHP): Organization sitewide; 5× PawnShop on / and /locations/ only; FAQPage on the FAQ page only. Snippet 738 (old sitewide version) is **inactive**, kept for rollback | 2026-10-05 (738 since 2026-06-19) | health check: 7/7 blocks valid |
| `thevalleypawn.com/llms.txt` (WPCode PHP snippet 742) | 2026-06-19 | health check; repo copy `llms.txt` here is a **snapshot of live** (re-taken 2026-09-05) — the site is the source, never regenerate the site from this folder |
| FAQ page `/frequently-asked-questions/` | 2026-06-19 | health check |
| robots.txt allows GPTBot, ClaudeBot, PerplexityBot, Google-Extended | 2026-06-19 | health check |
| 20 city × metal service pages, internal-linked | 2026-08-23 | presence audit `city_pages_linked = 20` |
| Per-location schema URLs `/locations/{city}/`; `/contact` 301; homepage `tel:` links + sticky Call/Text/Directions bar | 2026-08-23 | health audit |
| Yoast fields writable via REST (WPCode 1135) — enables all meta/noindex automation | 2026-08-23 | — |
| Google + Bing NAP clean 10/10 (public listings) | ongoing | health check Mon |
| "Dixie Pawn" purged from owned content (site, media library, WP) | 2026-08-23 | presence audit `legacy_name_pages = 0` |
| 5 location pages rebuilt ~75 → ~800 words (quick answer, services, loan steps, hours table, Google rating, areas served, 7-Q local FAQ) + PawnShop/FAQPage JSON-LD with `@id` and aggregateRating | 2026-10-05 | builder `../bin/geo_2026-10-05/build_locations.py` |
| All 20 city spokes: quick-answer opener + verified aggregateRating in JSON-LD + fake testimonials replaced with real rating/review; selling-gold guide on Harrisonburg + Roanoke gold pages | 2026-10-05 | builder `../bin/geo_2026-10-05/build_spokes.py` |

## Metrics (latest)
- **AI Visibility Index 87%** (10/2, 20/23 answers). Google reviews verified in Maps 10/5: CUL 4.9/425, WAY 4.9/375, HAR 4.9/336, LEX 4.8/197, ROA 4.9/292 (chain 1,625). Roanoke gap vs The PawnShop (4.9/725) = −433.
- Prior: **AI Visibility Index 83%** (8/28) — match-or-beat top local rival on 25/30 answers. Trajectory 63% (7/24) → 75% (8/7) → 71% (8/21) → 83% (8/28). **9/4 scorecard MISSED** (task fired, no post) — register `FIX-VISIBILITY-MISS-0904`.
- Weak spots: Roanoke (The PawnShop outranks on every engine); Harrisonburg gold query (Coin & Gift Shop, since 8/7).
- AI referral traffic: 1–4 sessions/week.
- Presence grades (8/30): Google reviews A−, technical SEO B+, content B, FB/IG C+, directories D, video D−, GunBroker F, on-site commerce F. Every on-site number flat since 8/23; the only mover is the needs-Joshua count.

## Settled facts (do not "fix")
- Roanoke occupies Suite C **and** D; ATF "2362-D" is correct; customer-facing canonical is "Suite C".
- Harrisonburg is **1790 East Market Street, Suite 22** (Joshua, 2026-10-05). "Ste 22" is correct — never flag or remove it (supersedes the 8/23 rule).
- "Trusted Since 1988" is correct.
- Bing map renders ("Toni St", missing "Suite C") are TomTom render quirks, console is correct.
- Max loan amount is **$25,000** (Joshua, 2026-10-05). Live everywhere (/loans/, homepage, FAQ, llms.txt). Any $100,000/$100K/$10,000 maximum is a defect.
- NPA membership claim stays (NPA staff worked Joshua's SB749 request as a member, May 2026).
- Never publish testimonials that are not real, attributed Google reviews. The 60 invented "Google Review · {city}" cards were removed 2026-10-05.

## Not done — see the register for owner and age
Logins: Bing Places · Apple Business Connect · MapQuest + Yext cancel · BBB · YellowPages · FFLeasy · MasterFFL Culpeper FFL# · GunNook Harrisonburg hours.
Builds: Wikidata enrichment (spec `wikidata-entity.md`, needs a Wikidata login) · directory-listing-monitor as a real task. (Done 10/5: ratings schema, Harrisonburg gold page, schema scoping, location-page depth, NPA claim kept, city answer snippets published as page openers.)

## Known defects in this lane's own plumbing (umbrella plan §2)
- Two site auditors (presence-audit vs weekly-website-health-audit) crawl different sitemaps with different auto-fix authority → consolidate (wk3).
- `vp-ai-search-autofix` / `vp-ai-visibility-autofix` parse the previous task's Slack prose → move to JSON handoff (wk2).
- Review counts and Roanoke gap carried unverified since 8/25 (Maps scrape broke) → Chekkit client (wk1–3).
- Guardian skipped Friday-cadence entries on the 9/4 Friday pass → flagged in `fleet/expected_outputs.json`.
