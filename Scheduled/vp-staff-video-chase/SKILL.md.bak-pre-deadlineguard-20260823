---
name: vp-staff-video-chase
description: Wednesday 11:15 AM — name the stores that haven't sent a video yet before the 2 PM cutoff, then at deadline collect whatever came in, process it, and schedule it. The chase step is what makes deal-of-the-week hit 10/10.
---

---
model: claude-sonnet-5
---

# vp-staff-video-chase — Lane B2b, the chase and the pick

**Why this exists.** The chase is the step that works. On 2026-08-10 the deal-of-the-week reminder
named two stores that hadn't submitted; **both complied within 12 minutes.** By 8/17 no chase was
needed at all — the habit had formed. Video gets the same treatment.

**Read first:** `valley-pawn-context`, `my-writing-style` (this posts as Joshua).

## Step 1 — Chase (11:15 AM)
Read `#casual-video` (or the fallback channel `vp-staff-video-prompt` used) since Tuesday 9 AM.
Identify which of the five stores — Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro — have
**not** submitted.

**CRITICAL TIMING BUG TO AVOID.** On 2026-08-10 the content batch declared "Uriah didn't submit"
at 2:12 AM — Uriah submitted at 11:17 AM that same day, nine hours later. Read the channel **at
run time**, right now, and never carry a stale "hasn't submitted" judgment forward from an earlier
run or an earlier task.

If any store is missing, post ONE short message @-mentioning only those managers: a few hours left,
one line, friendly, no guilt. If all five are in, post a genuine thanks and skip to Step 2.
Never DM a manager a failure notice, and never escalate a missing video to Preston or to Joshua —
a missed video is not a performance issue.

## Step 2 — Collect (after the 2 PM cutoff, same run)
Download every submitted video into
`~/Documents/Claude/Projects/Valley Pawn Studios/casual-video-inbox/`.
Pull them from Slack via the Chrome Slack web session — team **T03BL4W1DCL is Valley Pawn** (the
8/17 manifest's "wrong workspace" claim is obsolete and wrong).

If a file is horizontal, keep it: crop to 9:16 centered on the action rather than discarding it.
A usable imperfect video beats a missing one.

## Step 3 — Process
`vp-casual-video-daily` fires nightly at 7:44 PM and processes whatever is in that inbox
(captions + lower-third + end card + Publer scheduling). **Dropping the files in the inbox is
normally all this task needs to do** — do not duplicate its work.

Verify tonight's run actually picked them up (Rule 12 — check the output, not the run record). If
`vp-casual-video-daily` fails or the inbox is still full tomorrow, process them directly here:
`casual_video_processor.py` in `Refine Social Media/` does captions, lower-third and end card.
Note: `whisper` is **not currently installed** on this Mac. If auto-captioning fails, **write the
captions by hand from watching the video** — burned-in captions are mandatory (Reels and TikTok
autoplay muted), and a missing transcription tool is not a reason to ship an uncaptioned video or
to ship nothing.

## Step 4 — Publish
Route through `vp_social_publisher.py` / `PublerClient` — never a one-off script.
- Publer auth is `Authorization: Bearer-API {key}` **plus a browser User-Agent**, or Cloudflare
  returns `error code: 1010`. A 403 is not a dead key.
- Pass explicit `from`/`to` on any post listing — `GET /posts` silently caps at ~15 without them.
- **No Meta Graph API** — all Page tokens died 2026-08-21.

Route each store's video to **that store's FB page (as a Reel) + Brand IG + BrandTikTok**. Real
staff faces are the highest-trust content Valley Pawn can publish — give them the brand accounts,
not just the store page. Schedule Thursday–Saturday, evening slots.

## Step 5 — Close the loop with the person who sent it
Reply in-channel to each manager who submitted, telling them where their video is going and when.
People who see their work used send more next week. **This is the single highest-leverage line in
this task** — the whole reason the inbox sat empty for 47 days is that submitting once led nowhere.

## Step 6 — Record and log
    cd ~/Documents/Claude/Projects/Refine Social Media
    /usr/bin/python3 creative_drift.py record --format-id vid_walked_in --account <Account> --engagement 0 --reach 0

Log to `#vp-studio-queue` (C0BHTEUPADB): who submitted, what shipped, where.
DM Joshua (`D03BHQH5VGT`) only if **zero** stores submitted three weeks running — that is a real
signal the ask isn't landing and the format needs rethinking. One or two quiet weeks is normal and
not worth his attention.
