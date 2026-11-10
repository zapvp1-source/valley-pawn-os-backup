# Valley Pawn community-post campaign — scorecard

Newest run first. Written by the `Social campaign scorecard` scheduled task (Mondays 8:35 AM ET).
Measurement: `campaign_scorecard_measure.py FROM TO OUT.json` (read-only Publer post_insights, paginated, tagged
against `state/plans/*.json`); raw output in `state/scorecard/`. Followers: `state/store_followers.json` +
`follower_growth_by_store.csv`.

Baseline (90 days to 10/20, community text posts — median reach / % of followers): Lexington 458 / 28% ·
Culpeper 149 / 17% · Waynesboro 145 / 12% · Harrisonburg 84 / 11% · Roanoke 11 / ~30% of 37. Deal photos ~43 avg reach.

Tuning rule: only once a new format has ≥6 posts pooled; >30% below the store's other community posts for 2
consecutive runs → lower its rotation (never delete); >30% above → give it priority.

---

## 2026-11-02 (run 2 — week 1, 10/26–11/1)

**Biggest finding — the Monday proven-format post has never gone out.** The weekly plan builds Mon 14:30 (`social-weekly`),
an hour AFTER the Monday 13:30 debate/history slot it schedules, so that slot is always skipped ("empty caption" in
`plan_<week>_results.json`) — every week since at least 10/5 (old 08:30 slot) and again 10/26 (all 5 stores). Result: 0
debate/history posts this week on the 4 rolled-out stores, and the 4 history topics assigned 10/26 (State Theatre, Basic
City vote, Crooked/Weedy, Big Lick rename) are marked used by the 45-day cooldown without ever posting. Today's (11/2)
debate topics and the Roanoke Star (held for Mon 11/23 13:30) will hit the same wall. Fix is in `vp_social/plan.py` /
the build time (hardened infra — outside this task's edit scope): either build the week before Monday 13:30 or move the
proven topic to a later weekday 13:30 slot. Flagged to Joshua (HUMAN_QUEUE + phone notification). Not changed here.

### Per store (Publer post insights, store FB pages, posts 10/26–11/1; Sat/Sun posts still accruing reach)
| Store | Posts | Median reach | % followers | Community posts | Community median | Community % | Baseline % | Eng. | Comments | Shares |
|---|---|---|---|---|---|---|---|---|---|---|
| Culpeper | 6 | 63.5 | 7.2% | 4 | 85 | 9.6% | 17% | 12 | 0 | 0 |
| Waynesboro | 6 | 93 | 7.5% | 4 | 111 | 9.0% | 12% | 9 | 0 | 0 |
| Harrisonburg | 6 | 32 | 4.2% | 4 | 37 | 4.9% | 11% | 5 | 0 | 0 |
| Lexington | 5 | 231 | 14.3% | 4 | 254.5 | 15.7% | 28% | 10 | 0 | 0 |
| Roanoke | 7 | 7 | 18.4% | 5 | 7 | 18.4% | ~30% | 1 | 0 | 0 |
vs week 0 (10/18–10/25) community %: Culpeper 10.3 → 9.6, Waynesboro 7.6 → 9.0, Harrisonburg 8.6 → 4.9, Lexington 39.9 → 15.7,
Roanoke 14.5 → 18.4. All five below the 90-day mark; Lexington's drop is its first week without a big-reach post.

### Per format (pooled across stores)
| Format | Posts | Median reach | Note |
|---|---|---|---|
| HS game week (Fri 13:05) | 4 | 50 | CUL 69 / WAY 84 / HAR 31 / ROA 7 — each below that store's other community posts (−32% / −30% / −24% / ≈) |
| Debate (Lexington, Thu) | 1 | 312 | Lexington's best post of the week |
| History | 0 | — | Monday slot skipped (above) |
| Other community | 16 | 79.5 | |
| Deal video | 5 | 13 | below the ~43 deal-photo baseline |
| Other (Sat Halloween photos) | 4 | 17.5 | |
| Hiring / staff video | 0 | — | |

### Followers (Facebook page headers, 11/2)
| Store | 10/26 | 11/2 | Change |
|---|---|---|---|
| Culpeper | 882 | 883 | +1 |
| Waynesboro | 1.2K | 1.2K | — (rounded on page) |
| Harrisonburg | 760 | 759 | −1 |
| Lexington | 1.6K | 1.6K | — (rounded on page) |
| Roanoke | 38 | 39 | +1 |

### Outbound engagement (engagement_outbound/ledger.jsonl, 10/31–11/2)
| Page | Comments | Shares | Follows | Watchlist active / unresolved |
|---|---|---|---|---|
| Culpeper | 1 | 2 | 6 | 14 / 1 |
| Waynesboro | 2 | 1 | 6 | 5 / 9 |
| Harrisonburg | 2 | 1 | 6 | 6 / 8 |
| Lexington | 2 | 0 | 2 | 5 / 7 |
| Roanoke | 2 | 1 | 8 | 8 / 10 |
| Brand | 2 | 0 | 4 | 4 / 0 |
11/1 unattended run could not post (permission check); Joshua chose prep mode + post-on-request (HUMAN_QUEUE row closed
11/1); shares now autopost via the new `community-share-autopost` agent (CHANGELOG 11/2). Too early to tie to followers.

### Tuning
None. HS game week has 4 posts (<6). Watch: it ran below the store's other community posts this week on 3 of 4 stores —
if it is still >30% below at ≥6 posts next run, lower its rotation. Debate/history: no signal (0–1 posts).

### Measurement fix
`campaign_scorecard_measure.py` read the format from a top-level key that plan files don't have (it lives in
`contract.format`), so run 1's tagger would have filed every campaign post as "other community". Fixed (also reads
`contract.topic.id`); backup `fleet/_backups/campaign_scorecard_measure.py.bak-pre-scorecard-20261102`. Output
`state/scorecard/measure_2026-11-02_campaign.json`.

### Topic bank (self-heal)
- Dated games were at 1 future per store (11/6 only) → **17 winter basketball Fridays added**: Culpeper 12/4, 12/11 (at
  Eastern View, girls 5:30/boys 7:00), 1/8, 1/15 (school's 2026-27 team pages); Waynesboro 1/8, 1/15, 1/29; Harrisonburg
  12/18, 1/8, 1/15, 1/22, 1/29; Roanoke 12/4 (Northside girls), 12/18, 1/8, 1/22, 1/29 (Patrick Henry girls) — MaxPreps
  2026-27 pages, read in Chrome; each says re-verify the morning before posting. Gap: no verified Friday game 11/13–11/27
  anywhere and Waynesboro none until 1/8 — football playoff pairings post ~11/8; next run adds any playoff games.
  Not published yet: Waynesboro/Northside/Patrick Henry boys on school sites, Eastern View site down.
- Debate/history: test build showed all 4 stores "resting" the week of 12/7 → **4 history topics added** (verified today):
  Culpeper — Washington commissioned Culpeper County surveyor at 17, 1749 (mountvernon.org); Waynesboro — 1818 Rockfish
  Gap meeting that chose UVA's site (UVA Today); Harrisonburg — JMU began 1909 with 110 women (jmu.edu timeline);
  Roanoke — Hotel Roanoke 1882 / 1899 / 1938 / reopened 1995 (Virginia DHR). Also appended to `CITY_COMMUNITY_KB.md`.
- **Test build** (copy of ledger + plans in a scratch folder, real planner, weeks 11/2 → 12/21): **0 collisions**, no
  resting week, new topics land (12/4, 12/7, 12/11, 12/18 games and histories). Copy deleted.

### Changes made
- `community_topics.json` (+17 games, +4 history), `CITY_COMMUNITY_KB.md` (+dated section), `state/store_followers.json`
  (as_of 11/2), `follower_growth_by_store.csv` (+11/2 row), `campaign_scorecard_measure.py` (tag fix).
- Backups: `Valley Pawn OS/fleet/_backups/{store_followers.json,follower_growth_by_store.csv,community_topics.json,
  CITY_COMMUNITY_KB.md,CAMPAIGN_SCORECARD.md,CHANGELOG.md,campaign_scorecard_measure.py}.bak-pre-scorecard-20261102`.
- Report to Joshua: not due (first report 11/9). No Slack messages sent.

---

## 2026-10-26 (run 1 — launch morning, week 0)

**Campaign posts measured: 0.** The run fires at 8:35 AM; the new plan builds at 14:30 today and the first
campaign posts land this week (Mon 13:30 debate/history, Thu 13:30 5th community post, Fri 13:05 verified game).
Publer check 10/26 → 10/27 returned 0 posts on all 5 store pages (expected). First real read: Mon 11/2.

### Week-0 reference (10/18–10/25, the last week before launch — old formats)
| Store | Posts | Median reach | % followers | Community posts | Community median | Community % | Eng. | Comments | Shares |
|---|---|---|---|---|---|---|---|---|---|
| Culpeper | 7 | 67 | 7.6% | 4 | 90.5 | 10.3% | 21 | 0 | 3 |
| Waynesboro | 5 | 96 | 7.7% | 4 | 94.5 | 7.6% | 6 | 0 | 1 |
| Harrisonburg | 7 | 34 | 4.5% | 4 | 65.5 | 8.6% | 6 | 1 | 1 |
| Lexington | 5 | 625 | 38.6% | 4 | 647 | 39.9% | 14 | 6 | 1 |
| Roanoke | 7 | 5 | 13.2% | 4 | 5.5 | 14.5% | 2 | 0 | 0 |

Per format (pooled, week 0): other community 20 posts / median 92 · hiring 3 / 82 · deal photo 3 / 23 ·
deal video 3 / 10 · other 2 / 40. New formats (debate / history / HS game): 0 posts yet.

Note: the 10/19 08:30 community slots (incl. Waynesboro and Roanoke "Settle it for us") do not appear in Publer
insights for 10/18–10/25 — outside this campaign's window; not acted on.

### Followers (Facebook page headers, 10/26)
| Store | 10/24 | 10/26 | Change |
|---|---|---|---|
| Culpeper | 881 | 882 | +1 |
| Waynesboro | ~1,240 (1.2K) | 1.2K | — |
| Harrisonburg | 760 | 760 | 0 |
| Lexington | ~1,620 (1.6K) | 1.6K | — |
| Roanoke | 38 | 38 | 0 |
Waynesboro/Lexington show only rounded counts on the page header; estimates kept until the rounding moves.

### Tuning
None — no format has 6 posts of signal yet.

### Topic bank check
- Debate/history: 6 unused per store (3+3), one used per week → ~6 weeks of runway (bank rests week of 12/7,
  as the 10/24 test build showed). Roanoke Star held for 11/23. Threshold (<3 weeks) not hit — nothing added.
- Dated games: 2 future per store (10/30, 11/6) — at threshold, not below. **Next run (11/2) will see 1 per store
  and must add games:** VHSL playoff brackets post after the 11/6 regular-season finale (first round ~11/13), then
  winter sports (basketball) schedules from each school's own athletics page.
- No changes to `community_topics.json`; plan.py test build not needed (no additions).

### Changes made
- `state/store_followers.json` refreshed (as_of 2026-10-26); NEW `follower_growth_by_store.csv` (10/24 baseline + 10/26).
- NEW read-only `campaign_scorecard_measure.py`; outputs `state/scorecard/measure_2026-10-26_{campaign,week0}.json`.
- Backups: `Valley Pawn OS/fleet/_backups/{store_followers.json,community_topics.json,CHANGELOG.md}.bak-pre-scorecard-20261026`.
- Report to Joshua: not due (first report 11/9). No messages sent.
