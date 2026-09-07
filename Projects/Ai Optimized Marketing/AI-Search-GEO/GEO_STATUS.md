# AI-Search / GEO — Current Status (single source; replaces the checklist + went-live files)
**Last verified:** 2026-09-05 · **Owner tasks:** `vp-ai-search-health-check` (Mon 6:10), `vp-ai-search-autofix` (Mon 8:30), `vp-ai-visibility-metrics` (Fri 6:30), `vp-ai-visibility-autofix` (Fri 9:30), `vp-presence-audit-weekly` (Sun 4:20 PM)
**Open items of record:** `../register/MARKETING_OPEN_ITEMS.json` (lane `geo`) — not this file, not the scorecard's `needs_joshua`, not any audit's §7.

> Drift protocol (from PLAN-2026-08-03, now enforced): contradiction beats omission. When something here is superseded, the old line is deleted, not layered. `README-publish-checklist.md` and `STATUS-what-went-live.md` were retired to `_archive/` on 2026-09-05 because both had gone stale (unchecked boxes for things live since 6/19; a ✅ line retracted 44 lines later).

## LIVE (verified against the site, not against our own notes)
| Asset | Since | How it's verified weekly |
|---|---|---|
| JSON-LD schema sitewide — Organization + 5× PawnShop + FAQPage (WPCode snippet 738) | 2026-06-19 | health check: 7/7 blocks valid |
| `thevalleypawn.com/llms.txt` (WPCode PHP snippet 742) | 2026-06-19 | health check; repo copy `llms.txt` here is a **snapshot of live** (re-taken 2026-09-05) — the site is the source, never regenerate the site from this folder |
| FAQ page `/frequently-asked-questions/` | 2026-06-19 | health check |
| robots.txt allows GPTBot, ClaudeBot, PerplexityBot, Google-Extended | 2026-06-19 | health check |
| 20 city × metal service pages, internal-linked | 2026-08-23 | presence audit `city_pages_linked = 20` |
| Per-location schema URLs `/locations/{city}/`; `/contact` 301; homepage `tel:` links + sticky Call/Text/Directions bar | 2026-08-23 | health audit |
| Yoast fields writable via REST (WPCode 1135) — enables all meta/noindex automation | 2026-08-23 | — |
| Google + Bing NAP clean 10/10 (public listings) | ongoing | health check Mon |
| "Dixie Pawn" purged from owned content (site, media library, WP) | 2026-08-23 | presence audit `legacy_name_pages = 0` |

## Metrics (latest)
- **AI Visibility Index 83%** (8/28) — match-or-beat top local rival on 25/30 answers. Trajectory 63% (7/24) → 75% (8/7) → 71% (8/21) → 83% (8/28). **9/4 scorecard MISSED** (task fired, no post) — register `FIX-VISIBILITY-MISS-0904`.
- Weak spots: Roanoke (The PawnShop outranks on every engine); Harrisonburg gold query (Coin & Gift Shop, since 8/7).
- AI referral traffic: 1–4 sessions/week.
- Presence grades (8/30): Google reviews A−, technical SEO B+, content B, FB/IG C+, directories D, video D−, GunBroker F, on-site commerce F. Every on-site number flat since 8/23; the only mover is the needs-Joshua count.

## Settled facts (do not "fix")
- Roanoke occupies Suite C **and** D; ATF "2362-D" is correct; customer-facing canonical is "Suite C".
- Harrisonburg has **no** suite number — "Ste 22" is a defect wherever it appears (GBP still shows it → `LOGIN-GBP-CONSOLE`).
- "Trusted Since 1988" is correct.
- Bing map renders ("Toni St", missing "Suite C") are TomTom render quirks, console is correct.
- Max loan amount: live says $100,000, **unconfirmed** (`DEC-MAX-LOAN`). Do not touch until answered.

## Not done — see the register for owner and age
Logins: Bing Places · Apple Business Connect · MapQuest + Yext cancel · GBP console · BBB · YellowPages.
Builds: Wikidata enrichment (spec `wikidata-entity.md`) · aggregateRating schema · Harrisonburg gold page · directory-listing-monitor as a real task · schema scoping per page · location-page depth · NPA claim (restore or drop) · city-answer-snippets (`content/`, drafted 6/19, never published).

## Known defects in this lane's own plumbing (umbrella plan §2)
- Two site auditors (presence-audit vs weekly-website-health-audit) crawl different sitemaps with different auto-fix authority → consolidate (wk3).
- `vp-ai-search-autofix` / `vp-ai-visibility-autofix` parse the previous task's Slack prose → move to JSON handoff (wk2).
- Review counts and Roanoke gap carried unverified since 8/25 (Maps scrape broke) → Chekkit client (wk1–3).
- Guardian skipped Friday-cadence entries on the 9/4 Friday pass → flagged in `fleet/expected_outputs.json`.
