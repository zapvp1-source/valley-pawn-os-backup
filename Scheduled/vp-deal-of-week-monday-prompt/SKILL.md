---
name: vp-deal-of-week-monday-prompt
description: Every Monday 8am ET — post Deal of the Week submission prompt to Slack #deal-of-the-week
model: claude-sonnet-5
---


> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are running the Monday 8 AM kickoff for Valley Pawn's Deal of the Week submission window.

CONTEXT:
- Valley Pawn has 5 stores (Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke). Each store manager can submit ONE item per week to be featured in Thursday's email to ~11,159 subscribers.
- Submissions close at 12:00 PM ET. EVERY qualifying submission (one per store) goes in this Thursday's send — all of them, not just one winner.
- A companion task `vp-deal-of-week-monday-pick` runs at 12:30 PM today to compile all submissions, fill the campaign draft, and schedule it for Thursday 10 AM.

WHAT TO DO RIGHT NOW:

Your #1 essential output is the Slack prompt post — do it FIRST, before anything else, and never let any other step (credentials, Brevo lookups) block it or run before it. Even if every other step fails, the prompt post MUST still go out.

1. Post the following message in the Valley Pawn Slack channel `#deal-of-the-week` using `mcp__f92ce7c6-0353-4419-8491-f0843b182ff2__slack_send_message`. Look up the channel ID first with `slack_search_channels` if you don't have it.

Message (post EXACTLY as written, including the prep guidance):

```
:wave: Good morning, managers — Deal of the Week submissions open now.

Submit by 12:00 PM ET today. Reply in this thread with:
   1. Photo (clear, well-lit, item is the focus)
   2. Item name + brand
   3. Your price (under retail — that's the whole point)
   4. Your store + your name
   5. One sentence on why it's a good deal

Every store's deal goes in Thursday's email to ~11K subscribers — one submission per store, all featured. Get yours in.
```

2. After posting, log the post timestamp by posting a follow-up DM to Joshua's Slack (zapvp1@me.com). Find Joshua's user ID via `slack_search_users` then `slack_send_message` to his DM:

DM to Joshua:
```
Deal of the Week submission window is open. Compiler runs at 12:30 PM today and will feature every qualifying store submission. Scheduled Thursday send: [find the upcoming Thursday's campaign name from Brevo, e.g. "W2 — Gold Pulse + First Deal — June 11, 2026"].
```

(Best-effort and NON-BLOCKING — this is only for the DM's campaign name; it must never delay or precede step 1.) If you need the Brevo key and `~/.config/valley-pawn/brevo_api_key` is empty (the sandbox home differs from the Mac's), self-heal it: bridge from the Mac via the Control-your-Mac osascript tool (`do shell script "base64 < ~/.config/valley-pawn/brevo_api_key"`) and base64-decode it into that path. If the key still can't be read, SKIP the lookup and use the fallback text below.

To find the upcoming Thursday's campaign name: call Brevo API `GET https://api.brevo.com/v3/emailCampaigns?status=draft&limit=30` with `api-key` header read from `~/.config/valley-pawn/brevo_api_key`. Look for a draft whose name matches the upcoming Thursday's date (search names containing month/day strings). If no match found, just say "(no draft staged for this Thursday — will create from calendar at 12:30 PM)".

ONLY do these two posts. The compiler task handles the rest at 12:30. Do not block; do not wait for replies. Report success/failure as a brief one-line summary.

<!-- migrated to working model 2026-06-15 -->