# Search review — 2026-11-25 (Wed) — week 1 (baseline)

Window: last 28 days vs prior 28 days (Google). Bing has data only from 2026-11-20.

## Google Search Console — thevalleypawn.com
| Metric | Last 28d | Prior 28d | Change |
|---|---|---|---|
| Clicks | 1,140 | 900 | +27% |
| Impressions | 33.0K | 27.3K | +21% |
| CTR | 3.5% | 3.3% | +0.2 pt |
| Avg position | 7.6 | 7.9 | better |

| Page | Clicks (prev) | Impr (prev) | CTR |
|---|---|---|---|
| / (home) | 416 (765) | 16,696 (17,446) | 2.5% |
| /locations/harrisonburg/ | 179 (5) | 3,123 (1,384) | 5.7% |
| /locations/roanoke/ | 165 (23) | 5,368 (3,142) | 3.1% |
| /locations/culpeper/ | 163 (18) | 2,249 (1,034) | 7.2% |
| /locations/lexington/ | 69 (11) | 1,545 (730) | 4.5% |
| /locations/waynesboro/ | 62 (19) | 1,994 (1,769) | 3.1% |
| /sell-jewelry-roanoke/ | 5 (3) | 1,188 (783) | 0.4% |
| /sell-gold-roanoke/ | 3 (5) | 632 (678) | 0.5% |
| /sell-jewelry-harrisonburg/ | 3 (1) | 440 (444) | 0.7% |
| /sell-gold-harrisonburg/ | 2 (1) | 430 (676) | 0.5% |
| /sell-coins-waynesboro/ | 2 (0) | 414 (493) | 0.5% |

| Query | Clicks (prev) | Impr | CTR | Pos (prev) |
|---|---|---|---|---|
| pawn shop near me | 138 (106) | 5,811 | 2.4% | 7.3 (5.3) |
| valley pawn | 97 (86) | 861 | 11.3% | 2.6 |
| pawn shop | 48 (22) | 1,821 | 2.6% | 9.8 (7.8) |
| valley pawn culpeper | 43 (26) | 187 | 23% | 1.0 |
| valley pawn waynesboro | 27 (7) | 182 | 14.8% | 2.0 |
| pawn shop culpeper va | 17 (10) | 57 | 29.8% | 1.0 (5.1) |
| pawn shop harrisonburg va | 15 (19) | 131 | 11.5% | 2.0 |
| pawn shop roanoke va | 14 (10) | 404 | 3.5% | 5.3 |

## Bing Webmaster Tools
Data starts 2026-11-20: 0 clicks, 67 impressions (top: "valley pawn culpeper va", "valley pawn peters creek rd. roanoke va", pawn-vs-payday loan questions). Baseline only.

## Google Business Profile performance / Apple Maps
- GBP performance: not pulled this run (8-action cap reached). Next run.
- Apple: INSIGHTS_LOG.md 11/24 not read (Apple Business signed out).

## What changed (per store)
- Culpeper: location page clicks 18 -> 163; "pawn shop culpeper va" now position 1 (was 5.1).
- Harrisonburg: location page clicks 5 -> 179; page now ranks for the store queries.
- Roanoke: most location-page impressions (5,368) but CTR 3.1%; sell-* pages get impressions with <1% CTR.
- Lexington: location page clicks 11 -> 69.
- Waynesboro: "valley pawn waynesboro" clicks 7 -> 27; location page CTR 3.1%.
- Home page lost 349 clicks while location pages gained ~560: Google now sends store searches to /locations/ pages. Intended, no action.

## Changes made (max 3)
1. /sell-jewelry-roanoke/ (page 598): impressions up 52%, CTR 0.4%. Top non-brand queries: "where to sell engagement ring near me", "loose diamonds roanoke/cave spring", "diamond buyers". Yoast title was empty (default "Sell Jewelry in Roanoke | Valley Pawn") -> "Sell Engagement Rings & Diamonds in Roanoke, VA | Valley Pawn". Meta -> "Sell an engagement ring, loose diamonds, gold or a watch in Roanoke, VA. Free appraisal and same-day cash at Valley Pawn on Peters Creek Road." Verified live (cache-buster); IndexNow Success 15:43. Baseline to beat: 5 clicks / 1,188 impr / 0.4% / pos 16.9.

## Recommendations (not done)
- The other sell-* pages all run 0.4–1.1% CTR; repeat the title/meta rewrite one page per week if Roanoke jewelry improves.
- "pawn shop near me" slipped 5.3 -> 7.3 on more impressions; watch GBP performance next week.

## Measure next Wednesday (12/2)
- /sell-jewelry-roanoke/: CTR, clicks, position vs the baseline above. Keep / revert / iterate.
