# Valley Pawn Studios — STATUS

## 2026-09-06 — social engine shipped; four of the six items below are now resolved

`Refine Social Media/vp_social/` is the new deterministic engine (spec:
`Refine Social Media/SOCIAL_SYSTEM_SPEC.md`). Effect on the preflight backlog:

- **#1 (deal_store.json mirror does not exist)** — still true, and now harmless: the planner takes
  deal photos from `deal_of_week_uploads/` (path 3), which has always worked. Path 1 should be
  dropped from the check rather than fixed.
- **#2 (no upload_media helper)** — RESOLVED. `vp_social/publish.py` uploads media by file path and
  references it by library id (the only shape Publer actually honours for video).
- **#3 (publer-session.json missing)** — RESOLVED by removal: the Publer reachability check is now
  `python3 -m vp_social sync --back 1 --forward 7`, which tests the API path the lanes really use.
  The cookie file was gating on something that never existed.
- **#5 (Check 1 greps `inventory_export`)** — RESOLVED in the preflight prompt: it now looks for
  `_items-to-price.csv` / `_aged-inventory-summary.csv`.
- **#4 and #6** — unchanged, still worth a look.

**Known limitation logged today:** the nightly ledger-sync launchd agent
(`com.valleypawn.social-ledger-sync`) is installed but parked as
`...plist.disabled-needs-fda`. A launchd process cannot read `~/Documents` on this Mac (TCC), so
`import vp_social` fails there. Not blocking — every report and the planner sync inline when the
ledger is >6 h stale. One Full Disk Access grant for `/usr/bin/python3` would let the agent run.

## Run holds
_(Rule 16: scheduled tasks write failures here, never to Slack. Empty is good.)_

### 2026-09-07 — this week's videos and community posts didn't go out; the store deal posts did
Plain language: this week's five store deal photos and the "how it works" brand post published
fine. But the five store deal videos, the five-store video wrap-up, and all nine community posts
across the stores never got written -- they were left blank and the system correctly refused to
post something with no words on it rather than post empty. Nothing went out broken publicly;
these nine-plus items just didn't go out at all this week.

Technical detail: `python3 -m vp_social postflight plan_2026-09-07` (run via osascript on the
host -- the Cowork sandbox mount can't do sqlite locking against this share, disk I/O error every
time) shows 11/49 account-placements live, 38 skipped, all with reason "empty caption". Per-lane:
deal_photo 10/10 live (healthy), brand 1/5 live, deal_video 0/13 live, community 0/19 live.
Inspected `state/plans/plan_2026-09-07.json` directly: `vp_social/plan.py` always seeds
`captions: {account: None}` per slot for a later fill-in step to complete; that fill-in ran for
deal_photo and one brand slot but left all 17 deal_video/deal-compilation/community slots at
caption_len 0. Not a Publer or routing bug -- routing matches the 2026-08-04 redesign correctly
(store items to store FB+GBP only). Media files for the 5 reels + compilation exist on disk
(`reels/*.mp4`); only the caption-writing step for those lanes is missing this week.
Full diagnostic: `Refine Social Media/output/2026-09-07/postflight_FAILED.json` and
`postflight_result.json`. Did not attempt to backfill -- writing 17 new captions and publishing
them counts as new outgoing posts, which needs Joshua's go-ahead per the hard platform rule, and
regenerating them was out of scope for this verification-only task anyway. Worth a look at why
the Monday `vp-content-batch-weekly` caption-fill step completed for 2 of 6 lanes and not the
other 4, so this doesn't repeat next week.

### 2026-09-09 (vp-casual-video-daily nightly run) — Sandi's Culpeper brooch clip posted to 3 of 4 channels; Facebook silently did not go out despite two "successfully scheduled" confirmations
Plain language: one new manager clip came in this week (Sandi, Culpeper store, a vintage diamond
brooch). It's live and correct on Instagram, TikTok, and X, going out tomorrow (Thu 9/10) at
6:00 PM ET. The Facebook copy of the same post did not make it out. The scheduling screen said
"successfully scheduled" both times it was tried (once at 6:05 PM, once at 6:20 PM), but the post
never actually appeared anywhere in the real schedule afterward -- checked the live calendar
directly both times, not just the on-screen confirmation message. No third attempt was made
tonight to avoid the risk of creating a hidden duplicate later.

Also worth flagging: the auto-transcription that gets burned into the video itself misheard
Sandi's name and store name ("Sandy" / "Valley Pong Co. Pepper" instead of "Sandi" / "Valley Pawn
Culpeper"). All the written captions posted alongside the video were hand-corrected before
posting, so nothing customer-facing reads wrong except the burned-in on-video text on this one
clip. Re-rendering the video to fix that text was judged out of scope tonight.

Technical detail for whoever picks this up: this is the same "job reports complete but creates no
post" landmine already logged in this file for 2026-09-07 (Publer job status lies about success),
but this is the first time it's been confirmed happening through the Chrome UI composer path
specifically (not just the API path `publer_upload_media()`/`schedule_post()` already had a fix
for). Reproduced twice in a row on the Brand Facebook account only -- Instagram, TikTok, and X all
posted correctly via the same UI flow in the same session. Verified via the Publer calendar's
Failed and Drafts filters (empty on both) and a manual scroll of the live Sep 10 schedule at both
attempted times (6:05 PM and 6:20 PM) -- the post is not sitting anywhere, it's just gone. Next
session should try scheduling Facebook alone, first, before any other network, to rule out a
same-minute-collision side effect, and/or reach out to Publer support with the two timestamps
above if it recurs.

## PERMANENT-FIX-NEEDED (from preflight 2026-08-24)

1. Store-photo website mirror (Check 8, path 1) does not exist. No deal_store.json feed is reachable on thevalleypawn.com — checked WP-JSON route list (no deal routes) and three guessed static paths (all 404). No file anywhere on this Mac references deal_store.json either. This is the same class of blind assumption that zeroed out store-local content for three straight weeks (8/3, 8/10, 8/17) per the check's own history. Next interactive session should either (a) find/build the real feed endpoint on the WordPress site and document its actual URL, or (b) drop path 1 from the check entirely and rely on paths 2 (Slack) + 3 (local deal_of_week_uploads/), which both verified healthy today.
2. No PublerClient.upload_media helper script exists on this machine. Check 8's last-mile test (upload a test image, confirm a usable media URL) couldn't be run as specified — there's no local Python client for it. Verified Publer reachability via the live Chrome session instead (logged in, dashboard loads). Next interactive session should either build the helper script the check assumes, or rewrite the check to test via the Chrome/Publer UI path that's actually in use.
3. ~/.vp-studio/publer-session.json (saved cookie backup) does not exist. Today's Publer check passed on a live Chrome session, so this wasn't a blocker, but if that session ever drops, the documented auto-restore-from-file remediation has nothing to restore from. Next interactive session should export current Publer cookies to that path.
4. ~/.vp-studio/patches/MANIFEST.sha256 did not exist before this run. Generated it fresh from the three canonical patch files (publisher, reel-publisher, ai-text) since no manifest was present to verify against. Worth confirming in the next interactive session that these are in fact the intended/trusted versions of those patches.
5. Check 1's literal filename pattern (inventory_export) doesn't match anything Bravo Data Extraction actually produces (real outputs are named aged-inventory-summary, buys-from-public, end-of-month, etc.). Freshness was confirmed via aged-inventory-summary (today's date) instead. Preflight's grep pattern should be corrected so this isn't a lucky pass.
6. Check 4's literal grep pattern (graph.facebook.com/facebook-post) matches on purpose in vp-content-batch/SKILL.md — the 11 hits are all "DO NOT use this, it's retired" warnings, not live calls. File is healthy; the check's pass/fail logic is too naive to tell the difference. No patch was applied.

## Preflight run log
See output/preflight_2026-08-24.json for the full structured report.


## 2026-09-07 — casual-video: 5 backlogged manager clips downloaded from Slack and published; upload/schedule bug fixed
The 61-day-empty casual-video-inbox lane got its first 5 real submissions 9/1-9/2 (Walker,
Benjie, Chadd, Uriah, Rob-filling-in-for-Sandi) but they sat in Slack untouched -- nobody
had a mechanism to pull them from Slack into casual-video-inbox/. Manually downloaded all 5
via Chrome + Slack file URLs, verified content (no firearms, on-brand) by frame-extraction,
dropped into the inbox, and ran casual_video_processor.py.

**Bug found and fixed (additive, in casual_video_processor.py):** publer_upload_media() was
POSTing to /media and handing schedule_post() a raw hosted *url*. Publer's job_status reports
that as "complete" but creates no post -- real per-account error is "Calling Document.find
with nil is invalid" (confirmed live: 5/5 jobs, 20/20 account-attempts, zero real posts
created on the first pass today). Rewrote it to use PublerClient.upload_media() -> real media
library id -> {"type":"video","id":media_id}, and to schedule per-account via a
wait_for_job-verified call (same pattern as vp_social/publish.py), instead of trusting a
returned job_id as success. This matches the SOCIAL_SYSTEM_SPEC.md landmine table -- this
lane just had not been updated to the fix vp_social already carries.

**Result, verified against Publer live /posts list (not just job status):** 20 real
"video"-type posts in state "scheduled", 5 items x 4 accounts (Brand FB, BrandIG, BrandTikTok,
BrandTwitter), staggered 12 min apart, 6:00-6:48 PM ET today 2026-09-07.

**Still open:** the #casual-video channel still does not exist (Preston has not created it,
flagged since 8/22); the ask still runs in #deal-of-the-week as a fallback. The nightly
vp-casual-video-daily scheduled task will now work correctly against future submissions
since the code fix is in place -- no separate action needed there.


## 2026-09-07 - weekly product batch shipped on the vp_social engine (11/11 placements)
Ran `vp-content-batch-weekly` end to end through `python3 -m vp_social` (sync -> plan -> validate ->
publish --live -> sync to verify). 5 store Deal-of-the-Week photo posts x FB+GBP for Thu 9/10, plus a
Brand FB explainer for Tue 9/8. 0 failed, 0 blocked, 0 photo gaps - every store photo is the real
manager submission from today pick, pulled from `vp-website-deals-weekly/deal_store.json` and
uploaded with `upload_media()`.

**Landmine worth adding to the SOCIAL_SYSTEM_SPEC.md table:** scheduling a post to an account at a
timestamp that already holds another post for that same account makes Publer return job status
`complete` while creating nothing. Hit it on Brand FB at 2026-09-07T18:00:00 (the casual-video lane
owned that exact minute). Only a `sync` + ledger check catches it. Fixed by moving the slot to
2026-09-08T17:30.

**Minor engine friction:** retrying a single slot by re-running `publish` on the same plan is blocked
by the identical-caption guard, because that plan own freshly published captions are now live.
Publishing a one-slot copy of the plan under the same plan_id is the workaround used today.

## 2026-09-07 (evening, vp-casual-video-daily nightly run) — closed a 5-of-20 gap the earlier session's own verification missed, found and fixed the root-cause bug
Plain language: earlier today's casual-video catch-up (logged above) said all 20 posts (5 staff clips x Facebook/Instagram/TikTok/X) were scheduled and verified live. Tonight's nightly run re-checked Publer directly and found only 15 of 20 had actually gone out -- Rob's clip hadn't posted anywhere, and Benjie's clip was missing Facebook. Both gaps are now closed; all 20 are confirmed live with real Publer post links (Facebook/Instagram/TikTok) or post URLs (x.com). No new Slack files needed pulling -- the 5-clip ledger (.collected_file_ids.txt) already covered everything posted in #deal-of-the-week since 8/30.

Two distinct root causes, both real, both fixed:
1. **Bug in `publer_client.py`'s `wait_for_job()` (shared by casual_video_processor.py and ~15 other publishing scripts in this folder)**: it only exited its polling loop on status strings "completed"/"failed", but Publer's real API returns "complete" (no -d). So `wait_for_job` always burned its full 90s and returned `{"status":"timeout"}` even when the job had finished -- which the caller then reports as "failed". This is why the earlier session saw 5 of 20 combos looking like failures when 3 of those 5 (Benjie/FB + 2 of Rob's 4) had likely actually succeeded quietly; the other 2 (Rob's TikTok + X) needed an actual retry (see below). **Fixed additively**: `publer_client.py` line ~256 now also accepts "complete"; backup at `publer_client.py.bak-20260907-waitforjob`. This should reduce false-failure/timeout reports across every other script that calls `wait_for_job` too, not just this lane -- worth a next-session spot-check on `friday_close_engagement_publer.py` and `quota_watchdog.py`, which use the same call.
2. **X/Twitter rejected Rob's tweet outright** (real per-account error, correctly surfaced once actually read): "You may not post duplicative or substantially similar Tweets across one or more accounts." All 5 tonight's X captions are built from the same template ("Hey this is {name} here at the Valley... #ValleyPawn") and X's dedup filter flagged Rob's as too similar to the 4 that had already posted. Worked around tonight by hand-writing a differently-structured caption for just that one post (now live). **PERMANENT-FIX-NEEDED**: `build_captions()` in `casual_video_processor.py` should vary sentence structure per clip (not just swap the name) so this doesn't recur on a future 5-for-5 night -- a templating tweak, not a one-line fix, left for a dedicated pass.

Verification method: queried Publer's `/posts` list directly for both `state=scheduled` and `state=published`, matched by media filename against the outbox files, and required a real `post_link`/post id before counting anything as done (Rule 12) -- did not trust `job_status` alone a second time given finding #1 above.

No Slack notification sent tonight: Joshua's own 1:32pm message to the 5 managers already covered this (accurate at the time, and the gap it left was invisible until this run's direct-Publer check), and per Rule 16 the failure/fix detail belongs here, not in chat. Nothing forward-looking is blocked -- tomorrow's run will behave correctly against the wait_for_job fix.

### 2026-09-10 (vp-casual-video-daily nightly run) — closed a 4-clip gap: Uriah/Benjie/Martin/Walker were rendered 9/8 but never scheduled
Plain language: no new Slack submissions this run (all clips currently in #deal-of-the-week are
already in the collection ledger). But a direct Publer check turned up 4 clips from the 9/8 batch
(Uriah's pressure washer - Lexington, Benjie's Valve Index VR kit - Roanoke, Martin's tile saw -
Waynesboro, Walker's e-bike - Harrisonburg) that had been transcribed and rendered into outbox/ on
9/8 evening but were never actually scheduled to Publer -- no matching post existed anywhere in
Publer's scheduled or published lists, and no STATUS.md entry logged that night's run at all. Root
cause not fully diagnosed (no log survives from that run), but the effect is a real gap: rendered-
but-never-scheduled clips are invisible to future nightly runs because casual_video_processor.py's
inbox check only looks for raw video files in the folder root, and these had already been moved to
outbox/processed by the render step.

Fix applied tonight: safety-checked a frame from each of the 4 outbox finals (no firearms/off-brand
content), wrote fresh hand-corrected captions (the burned-in auto-transcription mangled names/prices
on all 4 -- "Valley Pond", "Wainsboro", implausible digit-dropped prices like "$9.99" for a VR kit --
so captions were written from the real transcripts+visuals rather than trusting the raw ASR text,
same approach used for Sandi's brooch clip on 9/9), uploaded each already-rendered final.mp4 to the
Publer media library, and scheduled all 4 across Brand FB/IG/TikTok/X for tomorrow 9/11, staggered
6:00/6:12/6:24/6:36 PM ET to avoid the known same-minute collision landmine.

**New landmine found:** `_schedule_one_account`'s job_status check reported "failed" for all 16
of tonight's schedule calls (a "one minute gap required" collision message for FB/IG/TikTok, and
an X duplicate-content policy message for Twitter) -- but a direct `/posts?state=scheduled` check
(paginated via `page=N`, since the API caps each page at 15 regardless of the `limit` param) showed
all 16 posts actually exist, correctly, at the intended times. This is the same "job reports the
wrong thing" family as the 2026-09-07 and 2026-09-09 landmines, but inverted: those were false
successes, this is a false failure. Did not change `wait_for_job`/`_schedule_one_account` tonight --
flagging for next session to add a `/posts` re-check fallback when a schedule call reports failed,
before treating it as real (mirrors the "needs_ui_upload"/"partial_or_failed" fallback already in
place for the true-failure cases).

Slack: replied in-thread to Uriah, Benjie, Martin, and Walker with their post time. One DM to
Joshua per Rule 16 (plain, no technical detail).
