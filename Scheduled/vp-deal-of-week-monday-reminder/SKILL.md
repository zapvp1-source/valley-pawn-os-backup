---
name: vp-deal-of-week-monday-reminder
description: Every Monday 11am ET — check #deal-of-the-week for stores that haven't submitted a Deal of the Week yet and ping them directly before the noon cutoff
---


> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do.

You are running the Monday 11 AM "second reminder" check for Valley Pawn's Deal of the Week pipeline. This task exists because stores (most often Culpeper) have repeatedly missed the noon submission deadline, causing the Thursday email to go out short of a full 5-store lineup. The goal is to catch missing stores ONE HOUR before the cutoff and give them a direct nudge — not a generic channel-wide re-post.

CONTEXT:
- Companion task `vp-deal-of-week-monday-prompt` ran at 8 AM today and posted the submission prompt in Slack `#deal-of-the-week` (channel ID `C0AVCANK7E3`).
- Companion task `vp-deal-of-week-monday-pick` runs at 12:30 PM today and compiles whichever submissions came in by noon.
- Valley Pawn has 5 stores: Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke. Each store's manager submits at most once per week in that thread (photo + item name/brand + price + store + name + one-line pitch).

WHAT TO DO:

STEP 1 — FRESHNESS GUARD
Find the most recent "Deal of the Week submissions open now" post in `#deal-of-the-week` using `slack_read_channel` (channel ID `C0AVCANK7E3`) or `slack_search_public_and_private`. Confirm its timestamp is TODAY (this same Monday). If the most recent prompt is from a prior week (this week's 8 AM prompt didn't run or hasn't posted yet), do NOT post anything — stay silent and end the task.

STEP 2 — READ THIS WEEK'S THREAD REPLIES
Read the replies to today's prompt post with `slack_read_thread`. For each reply, identify which store it's from (look for the store name in the message text — Culpeper, Waynesboro, Harrisonburg, Lexington, or Roanoke). A reply only counts as a submission if it has both a photo attached and a price mentioned — same qualifying bar as the 12:30 PM compiler. Build the set of stores that HAVE already submitted a qualifying entry.

STEP 3 — DETERMINE WHO'S MISSING
Compare against all 5 stores. Build the list of stores that have NOT yet submitted a qualifying entry.
- If all 5 stores have already submitted: post nothing. End the task quietly (this is a success — no reminder needed).
- If 1+ stores are missing: continue to STEP 4.

STEP 4 — PING THE MISSING STORES' MANAGERS DIRECTLY
Known store manager Slack mappings (verify each still resolves via `slack_search_users` before using — a manager may have changed; if a name doesn't resolve, fall back to just naming the store in the channel post instead of an @mention):
- Culpeper — Sandi Cole
- Waynesboro — Chadd (Chadd McClintic)
- Harrisonburg — Walker Tapley
- Lexington — Uriah (Uriah Tiglao)
- Roanoke — Benjie Moore

Post ONE message in `#deal-of-the-week` (not a DM — visibility in-channel helps peer accountability), @mentioning only the manager(s) for the missing store(s):

```
:alarm_clock: One hour left — Deal of the Week closes at 12:00 PM ET.

{@mention for each missing store's manager}, we haven't gotten your store's submission yet ({list of missing store names}). Reply in the thread above with a photo, item + brand, your price, store + name, and one line on why it's a good deal — or your store won't be featured in Thursday's email.
```

If a manager's Slack user couldn't be resolved, just say "{Store name} — we haven't gotten your submission yet" without an @mention for that one.

STEP 5 — REPORT
Report a brief one-line outcome in your final message: which stores (if any) were missing and pinged, or "all 5 stores already in — no reminder needed."

Do not touch the Brevo draft or the campaign schedule — that is entirely the 12:30 PM compiler's job. This task only reads Slack and, if needed, posts one reminder message.
