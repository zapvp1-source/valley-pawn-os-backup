---
name: vp-staff-video-prompt
description: Tuesday 9 AM — post the weekly staff phone-video prompt to Slack with a concrete one-line ask and a Wednesday deadline. Clones the deal-of-the-week mechanic that gets 10/10 submissions.
model: claude-haiku-4-5
---

---
model: claude-haiku-4-5-20251001
---

# vp-staff-video-prompt — Lane B2a, the ask

**Why this exists.** `Valley Pawn Studios/casual-video-inbox/` has been **empty since 2026-07-06**.
`vp-casual-video-daily` has been firing every night at 7:44 PM against nothing, for 47 days. The
folder was never the problem — nobody was ever asked, given a deadline, or chased.

Right next to it, `#deal-of-the-week` gets **10 of 10 submissions two weeks running** because it
has a Monday prompt, an 11 AM reminder that names the stores who haven't submitted, and a noon
cutoff. This task is that exact mechanic, cloned onto video. Nothing more clever than that.

**Read first:** `valley-pawn-context` (store list, manager names, brand voice),
`my-writing-style` — this posts as Joshua and must sound like him.

## Step 0 — OPEN-ASK GUARD (added 2026-08-23 — run this before anything else)
An off-cycle or manual fire can put an ask in the channel days before the Tuesday cron. If a
second, *different* ask then posts while the first is still open, managers get two competing asks
with the same deadline — which reads as noise and kills the credibility the deal-of-the-week
mechanic runs on.

Before picking an ask, read the channel (`#casual-video`, else `#deal-of-the-week` C0AVCANK7E3)
and look for a staff-video ask posted in the **last 5 days whose stated deadline has not yet
passed**. Also check `ASK_LOG.md` in this folder. If an open ask exists:
- **Do NOT post a new ask. Post nothing at all** — a silent skip, not a "reminder." The chase
  task (`vp-staff-video-chase`) owns reminders; a second voice here double-chases.
- Append the skip and the open ask's deadline to `ASK_LOG.md`, and treat the open ask as this
  week's ask for the 8-week rotation.
- Stop here. Steps 1-3 do not run.

Only if there is no open ask do you continue to Step 1.

*Why:* on 2026-08-22 the first proving fire posted "the weirdest thing that walked in" at 4:07 PM
Saturday with a Wednesday 2 PM deadline. The Tuesday 9 AM cron would have posted a second,
different ask into that same open window. Caught by vp-staff-video-chase on 2026-08-23 before it
happened.

## Step 1 — Pick this week's ask
**One concrete ask, not a category.** "Send us a video" gets nothing. These get replies:
- "30 seconds — the weirdest thing that walked in this week."
- "Show us the best deal on your counter right now. Phone video, hold it upright, 20 seconds."
- "What's the one item on your floor you'd take home yourself? Tell us why."
- "Show us something that came in that you had to look up."
- "Quick tour of what's new on the jewelry counter this week."

Rotate — never repeat an ask inside 8 weeks. Check the last 8 weeks of the channel before choosing.

## Step 2 — Post it
Post to `#casual-video` in Slack. If that channel does not exist, create it and invite all 5 store
managers plus Preston; if you cannot create it, post to `#deal-of-the-week` (C0AVCANK7E3) instead
and note the fallback — **do not skip the week over a missing channel.**

Message shape — short, specific, human, in Joshua's voice:
- the one-line ask
- **hold the phone upright (vertical)** — horizontal video is unusable on Reels and TikTok
- 15–45 seconds, no need to be polished, no script
- **deadline: Wednesday 2 PM**
- @-mention all 5 store managers by name

Say plainly that it's fine if it isn't perfect. The polish is our job; theirs is just to point the
camera. That framing is the difference between 0 submissions and 5.

## Step 3 — Log
Note in the run log which ask was used, so Step 1's 8-week rotation check works next week.
Silent on success — no DM to Joshua. This is a routine prompt, not an alert.
