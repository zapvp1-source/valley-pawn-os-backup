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
