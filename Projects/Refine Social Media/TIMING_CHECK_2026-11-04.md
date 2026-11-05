# Valley Pawn Social — Timing Check (2026-11-04)

Scheduled one-time check of the 2026-10-21 move of all slots into 1–3 PM ET.
Source: live Publer API, `publer_client.PublerClient().post_insights()` (paginated) for every non-GBP account in publer_accounts.json.
Window A (baseline) = 2026-07-22..2026-10-20. Window B (new timing) = 2026-10-22..2026-11-03.
Reach = analytics.reach.value. Engagements = likes + comments + shares + post_clicks. Hours are ET (Publer's local offset).

## Verdict: ADJUSTED

Pooled store-Facebook average reach per post fell from 120.3 (A) to 84.1 (B) = 69.9% of baseline, below the 90% bar.
Rule applied: only the hour that underperformed in B was moved. That was 3 PM (15:xx), the weakest B hour with 5+ posts (59.1 avg reach vs 81.9 at 1 PM and 2 PM), driven by the 15:10 deal-video slot.

Change made: `vp_social/plan.py` deal-video slot (store FB + Brand IG, Tue–Sat by store) 15:10 → **10:40** (new constant `DEAL_VIDEO_TIME`).
Why 10 AM: it is the best video hour in A+B measured on all 5 store pages (17 posts; 0.56x page average vs 0.25x at 3 PM).
Nothing else moved. Community 15:00 (Sunday) stayed: like-for-like, B community posts at 3 PM did as well as at 1–2 PM (0.81x vs 0.77x / 0.75x page average). Brand lanes stayed: Brand FB fell at every hour, including its old 6 PM slot (see below), so timing does not explain it.

Backup: `Valley Pawn OS/fleet/_backups/vp_social_plan.py.bak-pre-timingcheck-20261104`.
Test build (`VP_SOCIAL_LEDGER=/tmp/t.sqlite`, week 2026-11-09, seed 1): 33 slots, 0 duplicate (account, scheduled_at). Second build with the 11/02 deals file to exercise the moved lane: 42 slots, 0 duplicates, deal videos at 10:40 Tue–Sat, no slot on :50 (hiring). Test plan file moved to `Valley Pawn OS/fleet/_backups/plan_2026-11-09.json.testbuild-timingcheck-20261104` so Monday's run builds fresh.

## Read this before trusting the hour numbers

Store-FB reach per post vs each page's own A average (index 1.00 = page's normal):

| Period | Posts | Avg reach | Index vs page avg |
|---|---|---|---|
| Jul 22–31 | 34 | 133.9 | 1.04 |
| Aug | 72 | 130.7 | 1.15 |
| Sep | 87 | 113.6 | 0.90 |
| Oct 1–20 (old timing) | 58 | 109.2 | 0.94 |
| B, Oct 22–Nov 3 (new timing) | 50 | 84.1 | 0.66 |

- Against the last four weeks of old timing (9/22–10/20: 59 posts, 108.3 avg) B is 78% — still below 90%.
- The B drop is broad: every content type fell (community 201 → 120, photo 52 → 23, video 36 → 16) and every store fell. Content also changed inside B (10/24: deal stills retired on store FB, proven community formats).
- Community posts in B that still went out at old times did somewhat better than the 1–3 PM ones (Fri 10/23 5:45 PM: 1.10x page avg; Sun 10/25 10:46 AM: 0.86x; 1–3 PM: 0.75–0.81x). The 5:45 PM figure rests on one post (Lexington, 699 reach); without it 5 PM is 0.85x, level with the rest. So among community posts no B hour clearly beat another, and community times were left alone.
- The 10/20 audit's "1–3 PM peak" was partly page mix — Lexington (avg 328/post) posted mostly at 2–3 PM. Adjusted for page, the strongest A hours were 9 AM (Culpeper community, Aug–Sep), 8 AM (Harrisonburg community) and 5 PM (mostly Friday posts).
- The deal-video move rests on few posts (6 at 3 PM in B; 17 at 10 AM, mostly in A). Treat it as a test, re-measured at the next check.

## Pooled store Facebook (Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro)

| Window | Posts | Avg reach/post | Avg engagements/post |
|---|---|---|---|
| A | 251 | 120.3 | 7.07 |
| B | 50 | 84.1 | 2.80 |
| B, posts through 11/1 only (reach settled) | 46 | 87.7 | 2.83 |

By content type:

| Type | A posts | A reach | B posts | B reach |
|---|---|---|---|---|
| Community/text (status) | 119 | 201.0 | 32 | 120.1 |
| Photo | 96 | 51.8 | 10 | 23.2 |
| Video | 36 | 36.0 | 8 | 16.2 |

Average reach by posting hour (posts, avg reach, avg engagements):

| Hour ET | A | B |
|---|---|---|
| 7 AM | 1 · 36.0 · 1.0 | — |
| 8 AM | 17 · 98.2 · 4.5 | — |
| 9 AM | 21 · 165.2 · 11.5 | 1 · 29.0 · 2.0 |
| 10 AM | 51 · 78.2 · 4.5 | 8 · 71.0 · 2.1 |
| 11 AM | 43 · 110.0 · 4.6 | — |
| 12 PM | 21 · 140.2 · 10.0 | 1 · 51.0 · 4.0 |
| 1 PM | 16 · 152.6 · 13.9 | 15 · 81.9 · 2.1 |
| 2 PM | 17 · 262.6 · 12.2 | 7 · 81.9 · 2.1 |
| 3 PM | 15 · 203.7 · 8.7 | 13 · 59.1 · 2.2 |
| 4 PM | 22 · 17.1 · 0.6 | — |
| 5 PM | 15 · 165.5 · 14.5 | 5 · 197.2 · 8.4 |
| 6 PM | 6 · 39.8 · 1.8 | — |
| 7–9 PM | 6 · 47.5 · 2.5 | — |

Per store (avg reach/post): Culpeper 91.2 → 69.9 · Harrisonburg 73.8 → 33.8 · Lexington 327.8 → 288.0 · Roanoke 13.5 → 7.2 · Waynesboro 143.7 → 102.7.

## Brand Facebook

| Window | Posts | Avg reach/post | Avg engagements/post |
|---|---|---|---|
| A | 72 | 90.4 | 3.68 |
| B | 10 | 16.9 | 0.50 |

By hour — A: 9 AM 2 · 49.5 | 10 AM 5 · 107.6 | 11 AM 2 · 35.5 | 12 PM 1 · 167.0 | 1 PM 2 · 167.5 | 4 PM 4 · 23.8 | 5 PM 8 · 53.4 | 6 PM 42 · 101.9 | 7 PM 4 · 102.8 | 8–9 PM 2 · 43.5.
B: 1 PM 1 · 15.0 | 2 PM 5 · 14.2 | 4 PM 1 · 20.0 | 5 PM 1 · 24.0 | 6 PM 2 · 19.5.
Brand's B posts at its old 6 PM hour also got ~20 reach (vs 102 in A), so moving Brand back to 6 PM would not fix this. Not moved.

## Brand Instagram, TikTok, X

| Account | A posts | A reach | A eng | B posts | B reach | B eng |
|---|---|---|---|---|---|---|
| Brand IG | 112 | 17.1 | 0.19 | 0 | — | — |
| Brand TikTok | 35 | 106.8 | 0.80 | 3 | 93.3 | 0.33 |
| X (Joshua Davis) | 42 | 1.1 | 0.00 | 3 | 0.7 | 0.00 |
| Blog (WordPress, for reference) | 17 | 1.2 | 0.06 | 4 | 0.5 | 0.00 |

Brand IG shows 0 posts with analytics in B because Publer lost its Instagram authorization: the last posts published 10/21 and 10/22 (10:31 AM), then every post since has failed with "Authentication failed. Please reauthorize this account." This is already on Life OS/HUMAN_QUEUE.md (2026-10-26, [SIGN-IN] Publer → Social Accounts → Instagram → Reauthorize) and FAILURE_LEDGER. IG timing cannot be judged until that is fixed.
TikTok by hour — A: 10 AM 1 · 257 | 4 PM 2 · 85 | 5 PM 1 · 102 | 6 PM 16 · 107.3 | 7 PM 12 · 96.5 | 8–9 PM 3 · 111.7. B: 1 PM 1 · 94 | 4 PM 1 · 78 | 6 PM 1 · 108. Steady; no change.
X by hour — A mostly 6 PM (25 posts, 1.0); B 2 PM 2 · 1.0, 6 PM 1 · 0. Reach near zero at every hour; timing is not the issue.

## Next check
Re-measure after 3 more weeks (posts through ~11/24) with the deal video at 10:40, comparing like-for-like content types and against the 9/22–10/20 baseline, not the whole 90 days.
