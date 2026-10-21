# Valley Pawn Social — Full Audit (2026-10-20)
Source: live Publer API, 90 days (7/22–10/20), every published post on 15 accounts with per-post analytics (paginated — 519 posts with analytics, not the 10-per-account slice older reports used); live FB/IG/TikTok profiles; benchmarks (Socialinsider 2026, Buffer 2026).

## Scoreboard (90 days)
| Account | Posts | Total reach | Median reach/post | Engagements | Followers |
|---|---|---|---|---|---|
| Lexington FB | 40 | 12,925 | 305 | 112 | ~1,620 |
| Culpeper FB | 75 | 6,776 | 47 | 166 | ~880 |
| Brand FB | 73 | 6,615 | 41 | 80 | 1,700 |
| Waynesboro FB | 45 | 6,476 | 99 | 74 | ~1,240 |
| TikTok | 35 | 3,699 | 104 | 28 | 9 |
| Harrisonburg FB | 43 | 3,109 | 58 | 57 | ~760 |
| Brand IG | 111 | 1,878 | 6 | 17 | 104 |
| Roanoke FB | 48 | 578 | 11 | 8 | 37 |
| X | 42 | 45 | 1 | 0 | ~0 |
| Blog (as social slot) | 17 | 13 | 0 | 0 | — |
| 5 GBPs | 182 | not measured | — | — | — |
Workspace followers 6,300 (Aug) → 6,400 (Oct): flat. 24 comments total across 324 Facebook posts.

## What's working
1. Local community text posts on store pages: avg reach 125 vs 63 for product/deal posts and 44 for deal photos (2.8x). Top 15 posts by reach are all store-page text posts (Depot, Hull's Drive-In, murals, VMI). Matches 2026 benchmark: status posts have the highest engagement rate (0.20%).
2. Lexington and Waynesboro pages reach 20–30% of followers per post — healthy.
3. Hiring posts: avg reach 386, 243 link clicks from 6 posts — best-performing category.
4. Staff videos (managers on camera): avg reach 191 on FB, best video format.
5. TikTok: ~106 reach per video with 9 followers — the algorithm is distributing to non-followers.
6. Engine/QA: 0 failed posts in 90 days, no firearms, no stale hours, no duplicate captions shipping.

## What's not working
1. Brand FB page identity: cover photo is ammunition boxes (contradicts the no-firearms-on-social rule and hurts Meta recommendation/ad eligibility), profile picture is the old cropped "Valley Pawn & Guns" logo, bio is truncated mid-word ("What's Righ").
2. Output collapses whenever the fleet is touched: weeks of 7/27, 8/10, 9/21, 9/28 had 2–8 posts vs 50–144 normal. Consistent posters get ~5x engagement per post (Buffer).
3. Dead weight: X (42 posts, 45 total reach), Blog-as-social (17 posts, 13 reach), Brand IG (111 posts, median reach 6 — IG gets store deal photos that don't fit the platform).
4. Roanoke page has 37 followers — effectively no audience for a full store.
5. Deal photo posts underperform everything else (44 avg reach) yet are a core weekly lane.
6. Almost no conversation: 24 comments in 90 days. Few posts ask anything; no reply loop running.
7. Timing: queue clusters at 10:45, 12:15, 17:45. Measured FB reach peaks 2–3 PM (203–262 avg) and Sundays (204); 4 PM (30) and Saturdays (77) are worst.
8. Measurement blind spots: Friday digest says "hold current mix — insufficient signal" every week (10-posts-per-account threshold never met); GBP posts (35% of volume) are never measured; old analytics reader saw only 10 posts per account.
9. Giveaway: public since June, never drawn — trust/legal exposure, and Meta deprioritizes giveaway posts anyway.

## Optimization plan
### Claude executes (no decision needed)
1. Mix: shift store pages to ~60% local/community text, 20% staff video/reels, 20% product. Deal photos become multi-photo albums (albums lead views/shares for pages under 10K).
2. Routing: drop X and the Blog slot from routing; Brand IG gets only vertical video (reels/staff clips), not store deal stills. Frees ~70 placements per 90 days.
3. Timing: move planner slots to 1–3 PM weekdays plus a Sunday slot; retire 4 PM and Saturday slots.
4. Every community post ends with a real local question; add a twice-weekly reply sweep (Business Suite in Chrome).
5. Hiring posts: run on store pages whenever any store's hiring row is ON.
6. Measurement: rebuild the digest on the paginated pull (done in this audit's method), pool signal by content type across accounts, add GBP performance (calls, direction requests) via BrightLocal/GBP.
7. Mark the social lanes Tier-1 so a fleet freeze can't zero output again.
### Needs Joshua (one decision each)
A. Approve new Brand FB cover + profile picture (on-brand storefront/staff image, current logo) and fixed bio.
B. Roanoke page: grow it (Chekkit text with page link to Roanoke customers + in-store QR) — recommended — or merge.
C. Giveaway: draw the owed months and automate, or end it publicly.
D. Paid: $5/day boost on each store's best community post per week (~$600/mo) — test 30 days.
E. Meta login items still open: Business Verification, legacy Harrisonburg shell page, 2021 boosted post with hostile comments.
