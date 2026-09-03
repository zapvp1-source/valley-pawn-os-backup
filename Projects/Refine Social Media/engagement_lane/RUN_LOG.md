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

No Guess the Price or What Is This Thing has run yet, so there is no price/ID reveal outstanding.

---

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
