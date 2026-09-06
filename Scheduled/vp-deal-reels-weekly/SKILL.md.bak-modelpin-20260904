---
name: vp-deal-reels-weekly
description: Monday 2:30 PM — render 5 store Deal Reels + 1 brand compilation from the week's manager deal photos via ffmpeg, publish to store FB Reels + Brand IG Reels + TikTok through Publer. Zero human input required.
---

---
model: claude-sonnet-5
---

# vp-deal-reels-weekly — Lane B1, the machine video engine

**Why this task exists.** The 2026-08-22 audit found the content pipeline produced TWO videos in
90 days and ZERO in the last 49, because the only video path (`vp-casual-video-daily`) depends on a
human dropping a file into `Valley Pawn Studios/casual-video-inbox/`, which has been empty since
2026-07-06. Meanwhile #deal-of-the-week delivers 5 real product photos with real prices EVERY
Monday, 10/10 two weeks running. This task turns that reliable input into video with NO human
involvement. It is the floor under Valley Pawn's video output — if every other video path fails,
this one still ships 6 videos a week.

**Read first:** `vp-brand-studio` (palette/type are locked), `valley-pawn-context`,
`vp-operating-rules` (Rule 12 verify-against-output, Rule 15 FIX-FORWARD).

**FIX-FORWARD IS THE STANDING RULE HERE.** Joshua: *"iterations can't be to explain failure but to
overcome it."* Every step below has a remediation path. Do NOT end a run by reporting a problem you
did not first try to solve. A DM without a preceding remediation attempt is a task failure.

---

## Step 0 — File access
Try the file tools first. If a path under `~/Documents/Claude/Projects` is unreachable, do NOT stop
and do NOT call `request_cowork_directory` (nobody is present to approve it at 2:30 PM on a
schedule — that exact stall killed a run on 2026-08-18). Fall back immediately to
`mcp__Control_your_Mac__osascript` with `do shell script "..."` for all file access. Launch anything
long-running detached (`nohup ... &`) and poll a log file — the osascript tool times out around 30
seconds and will falsely report failure. Never retry a launch without checking `ps` first.

Working dir: `~/Documents/Claude/Projects/Refine Social Media`

## Step 1 — Gather this week's deals
Read the last 7 days of Slack `#deal-of-the-week` (C0AVCANK7E3) for the manager submissions. Each
carries: product name, our price, retail price, store, manager, and a one-line "why it's a great
deal". Extract all of them.

**Photo retrieval — proven paths, in order (from the 2026-08-21 hardening):**
1. **Primary (no browser):** the website deal-image mirror — `curl` the images from
   `thevalleypawn.com/wp-content/...` via the deal_store.json feed. The deal-of-week pipeline
   re-hosts manager photos there.
2. **Secondary:** Chrome Slack web session downloads. Team T03BL4W1DCL IS Valley Pawn — the 8/17
   manifest's "wrong workspace" claim is obsolete and wrong.
3. **Tertiary:** reuse the most recent photo already in `deal_of_week_uploads/` for that store,
   and say so in the log.

"No reachable photo" is NOT a valid reason to ship zero reels. Exhaust all three.

## Step 2 — Render
Write a spec JSON (list of `{store, photo, product, price, retail, hook}` — see the docstring in
`vp_deal_reel.py`) and run:

    /usr/bin/python3 vp_deal_reel.py --spec <spec.json> --outdir reels/

The engine handles the rest. Two things it does that you should not second-guess:
- It **auto-classifies each source as `photo` or `flyer`.** Managers sometimes submit a finished
  vendor marketing flyer that already carries the product name, price and a Valley Pawn logo
  (Culpeper and Lexington did on 8/21). Flyers get a slow read-pan with NO overlay cards; raw
  photos get the full product/price/trust treatment. Overriding this with `force_mode` is almost
  always wrong.
- It **renders to scratch and atomically moves the finished file into place, retrying once.** This
  was added after a live render left a truncated 2 MB .mp4 that looked like a real deliverable.
  Never treat the presence of a file as proof of success — check the run output.

**If a store fails to render:** the engine already skips it and continues (degraded mode). Try that
store once more with a different photo source from Step 1 before giving up on it. Ship the ones
that worked. **Partial output always beats zero output.**

## Step 3 — Captions
One caption per reel, per store, in Valley Pawn voice (see `valley-pawn-context`). Hard rules from
`PILLAR_OVERLAY` §6, all of which the audit found being violated:
- **No empty captions. Ever.** 45% of the audited 90 days shipped with none.
- **No byte-identical text across accounts.** The store FB caption and the store GBP caption must
  be genuinely different sentences, not the same string. Same for Brand FB / IG / TikTok.
- Every caption needs at least one concrete, specific, real detail from the submission.
- Include the store address and "30-day warranty, free layaway" naturally — never as a bolted-on
  boilerplate block identical across all five.

## Step 4 — Publish via Publer
**Route everything through `vp_social_publisher.py` / `PublerClient`** — never a one-off script
(that rule exists because the 8/21 catch-up bypassed it). Use `publer_client.py`:
- `upload_media(path, direct_upload=True)` to upload the mp4, then pass the returned usable URL as
  `video_url` in `schedule_post`.
- Publer auth is `Authorization: Bearer-API {key}` AND **requires a browser User-Agent header** —
  Cloudflare returns `error code: 1010` without one. A 403 does NOT mean the key is dead.
- When listing posts to verify, **always pass explicit `from`/`to` date params** — `GET /posts`
  silently caps at ~15 results without them, which has caused two false "the post is missing"
  reports already.

**Do NOT use the Meta Graph API.** Every Facebook Page token died on 2026-08-21 when the password
changed. Publer is the only working path.

Routing per store reel: that store's **FB page** (as a Reel) + **Brand IG** (as a Reel). The brand
compilation reel goes to **Brand FB + Brand IG + BrandTikTok**. TikTok has published ZERO posts in
its entire history — this task is what finally activates it. Account IDs are in
`publer_accounts.json`.

Stagger publish times across Tue–Sat so five reels don't stack on the same afternoon.

## Step 5 — Brand compilation reel
Build one 20–25s brand reel that strings the week's five items together (one card each) and routes
to Brand FB + IG + TikTok. If fewer than 3 store reels rendered, skip the compilation and log why —
a 2-item "week's deals" reel is not worth the slot.

## Step 6 — Record into the drift engine
For each reel published, record it so the creative engine learns:

    /usr/bin/python3 creative_drift.py record --format-id vid_deal_reel --account <Account> --engagement 0 --reach 0

(Engagement is backfilled later by the Friday analytics pass — record the post now so the count is
right.)

## Step 7 — Log and verify (Rule 12)
Post a short log card to `#vp-studio-queue` (C0BHTEUPADB): how many reels rendered, how many
published, which stores, which platforms, and **any store that fell back to an older photo**.
Verify against Publer's actual scheduled/published list — not against your own manifest. A manifest
saying "5 published" is not evidence.

**Silent on clean success beyond the channel log.** DM Joshua (`D03BHQH5VGT`) ONLY if fewer than 3
reels shipped after you exhausted every remediation above — and then in plain language, no
technical detail. Technical detail goes in the run log. Never post a failure notice to a team
channel or to any store manager.

## Step 8 — Housekeeping
Close any Chrome tabs this run opened. Keep `reels/` trimmed to the last 6 weeks.
Append a dated one-line entry to `~/Documents/Claude/Projects/Valley Pawn OS/CHANGELOG.md` only if
something material changed (a new failure mode, a fix applied) — not for a routine successful run.
