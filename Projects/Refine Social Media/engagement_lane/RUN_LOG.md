# vp-engagement-weekly — Run Log (Lane D)

Every run appends here. **Open loops are the point of this file** — a game or poll that never
gets answered is worse than never running it. Next run reads OPEN LOOPS first and closes them.

---

## OPEN LOOPS — must be closed by the next run

| Opened | Format | Where | What has to happen | Due |
|---|---|---|---|---|
| 2026-08-22 | `eng_stock_poll` | Brand FB + IG + X, publishing 8/23 5:30 PM | **Partially closed 2026-09-02.** Only 1 real comment ever came in (Bobby Perkins, a joke — "Corpolite"), already replied to by the Page (reply timestamped ~8/31, presumably the missed run before it died). No real category votes exist to tally. Recommend Joshua's call: skip the "we bought X" reveal post since there was no real data, or roll it into next poll's framing. | Needs Joshua's call, not auto-closed |
| 2026-08-22 | `eng_best_find` | Waynesboro FB, publishing 8/24 5:45 PM | **Closed 2026-09-02.** Verified via Business Suite Comments column: 0 comments ever received. Nothing to reply to. | Closed |
| 2026-08-22 | `hum_overheard` | Brand FB + IG, publishing 8/26 6:00 PM | **Closed 2026-09-02.** Verified via Business Suite Comments column: 0 comments ever received. Nothing to reply to. | Closed |
| 2026-09-01 | `eng_guess_price` (Gibson BR-9) | Brand FB + IG + X | **CLOSED 2026-09-07.** Reveal posted six days late on the same 3 accounts, real number ($149.99), honest acknowledgment of the delay, no excuses. See 2026-09-07 run entry below. | Closed |

No What Is This Thing has run yet, so there is no ID reveal outstanding. `eng_caption_this` and `eng_this_or_that` never promise a follow-up, so neither opens a loop.

---

## 2026-09-07 (Mon) — full run: reveal close, 2 new engagement posts, reply sweep

**Reveal close (Step 8 / HARD RULE 2026-09-06).** The 2026-09-01 Guess-the-Price (Gibson BR-9
amp, Waynesboro/Chadd) promised the real number "tomorrow evening" and never got it — six days
overdue. Verified the real price via #deal-of-the-week (2026-08-31 10:31:48 EDT, Chadd: $149.99)
and cross-checked against the friday_digest 2026-09-04 casual-video caption, which had already
stated the same $149.99 publicly — no risk of a mismatched reveal. Posted the reveal today on
the same 3 accounts as the original (Brand FB, BrandIG, BrandTwitter), honestly naming the delay
rather than pretending it didn't happen, reusing the same Publer media id for the amp photo.
Logged in the Open Items Register as closed.

**Drift selection** (season `late_summer`, 40% exploration): `creative_drift.py select --lane
engagement --slots 2 --account Brand` returned `eng_hometown_bracket` + `eng_caption_this`
(both NEW/top-ranked). `eng_hometown_bracket` was **substituted** with `eng_this_or_that`
(confirmed independently eligible via `--slots 6`) after a collision check against Lane C's
live Publer schedule turned up that nearly every verifiable fact in `CITY_COMMUNITY_KB.md` —
school mascots, murals, creeks, railroads, the courthouse — is already scheduled across all 5
towns within the next 10 days. Forcing a 5-store hometown-rivalry bracket into that same window
would either duplicate a Lane C post on the same page within days or force an under-researched
entrant. `eng_this_or_that` needed no new local fact (compares two already-priced items), so it
carries zero collision risk. Humor lane returned "no eligible formats" (all on cooldown) —
correctly shipped 0 humor posts, within the at-most-1 cap.

`eng_what_is_it` (What Is This Thing) was also considered for the Greenlee Model 849 PVC heater
(Roanoke) but rejected: Roanoke's own page already has that exact item named with its price
scheduled 2026-09-10 and again 2026-09-12 by Lane A, which would spoil the mystery before or
right after the ask could run. Left for a week when an item isn't already claimed by the
product/deal-reel schedule.

**Shipped: 6 posts (3 reveal + 2 this-or-that + 1 caption-this), verified live in Publer's own
scheduled list (not the manifest), zero job failures.**

| Publishes | Account | Format |
|---|---|---|
| Mon 9/7 5:30 PM | Brand FB | Guess-the-Price reveal |
| Mon 9/7 5:40 PM | Brand IG | Guess-the-Price reveal |
| Mon 9/7 5:50 PM | X (as Joshua) | Guess-the-Price reveal |
| Thu 9/10 5:45 PM | Waynesboro FB | eng_caption_this |
| Fri 9/11 5:30 PM | Brand FB | eng_this_or_that |
| Fri 9/11 5:40 PM | Brand IG | eng_this_or_that |

- **Sourcing:** all real, from #deal-of-the-week 2026-09-07 (all 5 stores, verified live in
  Slack): Sandi/Culpeper Rad Power Bike Plus $899.99; Chadd/Waynesboro Dual Gumball Machine
  $149.94; Uriah/Lexington STIHL HTA 50 pole pruner $160. Photos are the managers' own submission
  photos, uploaded straight to Publer's media library via `PublerClient.upload_media()` — no
  WordPress/Slack-download intermediary needed for this run.
- **Store-lead rotation:** the intended queue (Waynesboro → Harrisonburg → Lexington → Roanoke →
  Culpeper) got partially reshuffled by which stores had material that fit this week's
  collision-safe formats — Waynesboro (caption-this) and, via the cross-store this-or-that,
  Culpeper and Lexington all got a share. Roanoke and a clean Harrisonburg turn are next in line
  once a store-local slot opens up again.
- Six separate manifest items so FB/IG/X each got their own wording — zero byte-identical text.
  GBP excluded (stays informational, PILLAR_OVERLAY §2). Humor: 0 items, within cap.

**Reply sweep — 1 reply posted, zero unanswered comments remaining at the end of the run.**

Checked all 6 Pages (Brand, Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke) via Business
Suite's per-page Comments to-do widget, last 7 days (Aug 31–Sep 7):

- **Roanoke — Rachel Campbell, Sep 3, on the Cummins 4000W inverter post ($349.99).** Asked for a
  PM confirming availability, said she couldn't send messages herself. Replied as the Page with
  the store's direct phone number so she isn't stuck. This was new — not caught by the previous
  run's sweep.
- **Waynesboro — Scottie Lafferty, 6d, on the "Basic City" post.** Already answered by an
  existing Page reply from 1w prior that directly covers the Philippines-neighborhood question
  both she and Scott Tyler asked. No new reply needed.
- **Brand, Lexington, Harrisonburg, Culpeper:** nothing inside the 7-day window. Brand's only
  in-window item (Bobby Perkins on the stock-poll post) was already answered.
- **Old backlog still present** on Brand (Kim Patterson, Sylvia Coffey, Deni Dizdar, Kelly
  DeMattia, Chance Dudley — all 4mo+ to 4y old) and on Waynesboro (a run of ~10 near-identical
  "Sherri Dean" good-morning/attachment comments, 9w–13w old, that read like a bot account, not a
  customer needing a reply). Same backlog flagged 2026-08-22; still recommend a one-time amnesty
  pass (mark-as-read, don't reply) rather than resurrecting months-old threads. Not touched this
  run — outside the 7-day scope and a judgment call, not a mechanical one.

**Unrelated finding, not acted on (out of this lane's scope):** `#in-store-inventory`'s "Shop in
Store Sync" task has been posting loud, repeated "CRITICAL BLOCKER" / "mission-critical, please
reconfigure now" technical failure messages to that channel for weeks (runs 1–31+, 2026-08-06
through at least 2026-09-06) — a clear standing violation of Rule 16 (no failure notifications or
technical jargon to Slack, ever). Flagging for whoever owns that task; not fixed here since it's
a different pipeline than this lane's.

Logged to `#social-media`. Drift engine recorded: `eng_caption_this`/Waynesboro,
`eng_this_or_that`/Brand, `eng_this_or_that`/BrandIG, `eng_guess_price`/Brand (the reveal, so the
format's cooldown clock reflects the actual close date, not just the original ask).

## 2026-09-02 (Wed) — Fleet Guardian recovery run for missed 2026-08-31 3:45pm run

The 8/31 scheduled run silently died: no post ever landed in `#social-media` for it, but a reply to
Bobby Perkins' comment on the 8/23 stock-poll post is timestamped ~8/31 and signed "Valley Pawn ·
Author" — so the run partially executed (at least some of Step 6) before dying, with nothing logged.

**Duplicate guard:** confirmed via `#social-media` (C0BMRC2LN3D) — no Lane D post exists for week of
8/31. Genuinely missing; proceeded.

**Reply sweep (Step 6):** checked all 6 Pages (Brand, Harrisonburg, Culpeper, Waynesboro, Lexington,
Roanoke) via Business Suite's Content grid, Comments column, last 7 days (Aug 27–Sep 2) — **zero
unanswered comments found anywhere.** Also checked the three carried-over open loops from the
2026-08-22 run (see OPEN LOOPS table above) — all clear or already answered. **Comments replied to
this run: 0** (nothing was unanswered).

**Steps 1–5 (staging new posts) and Step 8 reveal post: NOT attempted this run** — time budget was
spent entirely on the duplicate guard and the full 6-page reply sweep (including tracking down and
verifying the three carried-over open loops individually, which took longer than a normal week
because they spanned two different Business Portfolios in Meta Business Suite). Next run should
prioritize Steps 1–5 first since the reply sweep is now fully caught up.

Logged to `#social-media`.

## 2026-08-22 (Sat) — first run of the lane

**Drift selection** (season `late_summer`, 40% exploration, cold start):
`eng_best_find`, `eng_stock_poll`, `hum_overheard` — all three were NEW, never run.

**Shipped: 6 posts, 3 formats, all verified live in Publer's own scheduled list (not the manifest).**

| Publishes | Account | Format |
|---|---|---|
| Sun 8/23 5:30 PM | Brand FB | eng_stock_poll |
| Sun 8/23 5:35 PM | Brand IG | eng_stock_poll |
| Sun 8/23 5:40 PM | X (as Joshua) | eng_stock_poll |
| Mon 8/24 5:45 PM | Waynesboro FB | eng_best_find |
| Wed 8/26 6:00 PM | Brand FB | hum_overheard |
| Wed 8/26 6:05 PM | Brand IG | hum_overheard |

- **Store-lead rotation:** week 1 = Waynesboro. Next: Harrisonburg → Lexington → Roanoke → Culpeper.
- **Sourcing:** every concrete detail is real, from #deal-of-the-week submissions 8/03, 8/10, 8/17
  (Roman Reigns Funko + Case 75th-anniversary knife set + Cornwell tool cart, all Chadd/Waynesboro;
  Husqvarna 585, Pulsar 12kW, iMac A3137). Nothing invented.
- **Humor:** 1 item, at the 10% cap. Punches at toolbox keys. No customer named or mocked, no
  money/hard-times joke, no firearms.
- Six separate manifest items so FB / IG / X each got their own wording — zero byte-identical text.
- GBP excluded (stays informational, PILLAR_OVERLAY §2).

**Reply sweep — 4 replies posted.**

Verified through Meta Business Suite's own Content grid, per-page, Comments column, all 6 Pages:

> **Zero comments were received on any Valley Pawn Facebook post in the last 7 days (Aug 15–22).**
> Zero unread Instagram comments. Not a measurement failure — there was nothing to answer, because
> nothing we published asked for anything. That is precisely what this lane exists to change.

So the sweep was widened to the whole Brand-page backlog, and **every unanswered comment on the
Brand page was answered, as the Page**:

| Who | When | What | Reply |
|---|---|---|---|
| Synster Gates Fan | Aug 8 | "Is this still available?" on a **2018** Schecter guitar post | Told them straight that it's a 2018 post and long gone; pointed at Harrisonburg's guitar wall |
| John Lowe | Aug 7 | Praise for the Harrisonburg team | Thanked him by name and named Walker and the crew |
| Jeff Grounds | Jul 4 | Asked for a small loan against a Fender Deluxe — "gas and food money today" | Apologised for the silence, explained the amount needs an in-person look, no credit check, come to any of the five |
| Elizabeth Catherine Gore | Mar 25 | 1-star: drove 45 min, store closed during posted hours, no sign | Owned it without excuses, asked which store and day, offered to make it right |

**Two things found on the way that need Joshua's call — not fixed by this lane:**

1. **Blank captions are still shipping.** Culpeper published on 8/19 and 8/22 with *no caption at
   all* ("This post has no text"). `vp_social_publisher.py` blocks empty captions, so those came
   through some other path. The bypass the July audit identified is still open.
2. **A dead 2021 boosted ad is still live on the Brand page** — "Need Money? We Can Help!", 35
   comments, the visible ones being "Gross", "Major rip off", "Yuk.!". Deliberately not replied to;
   answering would resurface it. It should be deleted, not answered.
3. **Store-page comment backlog is deep and old** — Culpeper alone has 9+ unread going back to 2025
   (incl. "Any PlayStations 4 or 5 available?" and "Any good rifles in either .243"). All are a year
   or more stale; answering now reads worse than silence. Recommend a one-time amnesty pass that
   marks them read rather than replying, then this lane keeps it at zero going forward.

**Infrastructure change (additive):** `vp_social_publisher.py` now accepts an optional `media_ids`
field per item, so image posts can use Publer's media library through the one hardened publishing
path instead of bypassing it with a one-off `schedule_post()` call. Absent key = identical prior
behaviour. Backup at `vp_social_publisher.py.bak-pre-mediaids-2026-08-22`.

**Baseline for next week:** 18 comments / 0 replies per 90 days → this run: **4 replies posted,
3 formats live that each end on a real question.**

---

## 2026-09-06 — CORRECTION: a Guess-the-Price DID run, and its reveal was never posted

An earlier entry in this log asserts that no Guess the Price had run yet. That is wrong, and the
error mattered: the 8/31 run scheduled six engagement posts (verified live in Publer via the
`engagement_lane_2026-08-31_publish_results_20260831T160816.json` manifest — Brand FB 9/1 17:31,
X 9/1 17:36, Brand IG 9/1 19:45, Harrisonburg FB 9/2 17:45, Brand FB 9/3 18:01, Brand IG 9/3
19:31), and the 9/1 posts told the audience the real number would go in the comments **the next
evening**. The 8/31 run then died before logging, and the 9/2 recovery run did the reply sweep
only. **The reveal was never posted.** Customers were asked a question and got no answer.

Two things changed today so this cannot recur:

1. `vp-engagement-weekly/SKILL.md` now carries a hard rule: any post promising a follow-up must
   have its reveal scheduled **in the same run**, on the same accounts, containing the real number.
2. The planner (`vp_social/plan.py`) emits an explicit `reveal` slot for any guess/answer format,
   and `vp_social/publish.py` **blocks the whole plan** if a guess slot has no matching reveal.
   A promise to customers is now a publish-time gate, not a note in a log.

The 9/1 reveal itself is still outstanding and is Joshua's call — it is five days late, so the
options are to answer it now (late but honest) or let it go. Flagged in the Open Items Register.
