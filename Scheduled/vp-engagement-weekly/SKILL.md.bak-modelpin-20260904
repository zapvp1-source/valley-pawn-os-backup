---
name: vp-engagement-weekly
description: Monday 3:45 PM — stage the week's Engagement posts (Guess the Price, What Is This Thing, polls, caption contests) and the humor slot. Text/image only, zero image-pipeline dependency. Baseline to beat: 18 comments in 90 days.
---

---
model: claude-sonnet-5
---

# vp-engagement-weekly — Lane D, the lane that actually creates a community

**Why this task exists.** The 2026-08-22 audit's most damning number: across 485 measured posts in
90 days, Valley Pawn received **18 comments total** — and Publer's stored reply array is **empty
across all 554 posts**, meaning nobody has ever replied to a single customer comment. Not one post
in the sample asks a question, runs a poll, or invites a response.

There is no community because nothing was ever built to create one. That is this lane's entire job.

**Read first:** `CREATIVE_DRIFT.md`, `valley-pawn-context` (brand voice), `PILLAR_OVERLAY` (humor
guardrails), `bravo-context` (for real inventory to feature).

---

## Step 0 — File access
File tools first; if a Projects path is unreachable, do NOT call `request_cowork_directory` (nobody
is present to approve). Fall back to `mcp__Control_your_Mac__osascript` → `do shell script`.

Working dir: `~/Documents/Claude/Projects/Refine Social Media`

## Step 1 — Ask the drift engine
    /usr/bin/python3 creative_drift.py select --lane engagement --slots 2 --account Brand
    /usr/bin/python3 creative_drift.py select --lane humor --slots 1 --account Brand

**2 engagement posts + at most 1 humor post per week.** The humor cap is a hard 10% ceiling from
`PILLAR_OVERLAY`, with a 60-day cooldown per bit — the engine enforces it, don't override it.

## Step 2 — Source real material
Engagement posts must use **real items**. Pull from this week's #deal-of-the-week submissions,
#in-store-inventory, the eBay listings, or fresh Bravo inventory. Fabricating an item to make a
game work is a hard violation of the authenticity standard (`PILLAR_OVERLAY` §6).

Format notes:
- **Guess the Price** — real item, price hidden. You must come back and reveal it in the comments
  the next day. Put that reveal on the calendar; an unanswered game is worse than no game.
- **What Is This Thing?** — a genuinely odd item that walked in. Answer in comments.
- **This or That** — two real items, ask which they'd take.
- **Who Made This?** — macro shot of a maker's mark or hallmark.
- **Caption This** — one genuinely odd counter photo.
- **What should we stock more of?** — a straight poll. **Then actually act on the answer and say so
  later.** A poll you ignore teaches people not to answer the next one.

## Step 3 — Humor guardrails (non-negotiable)
Dry Shenandoah humor, `vp-brand-studio` STYLE-D only. **Never mock a customer. Never joke about
needing money, being broke, or hard times — that is our customers' actual life. Never firearms.
Punch at objects, never at people.** If a bit needs a disclaimer, it isn't the bit.

## Step 4 — Write for a reply, not for a like
Every post in this lane ends on a genuine question. No CTA to visit a store — the ask IS the post.
Hard rules that the audit found being violated constantly:
- **No empty captions. Ever.** (45% of the audited 90 days had none.)
- **No byte-identical text across accounts** — FB, IG, X and GBP each get their own wording.
- 76% of captioned posts in the audit reused a caption verbatim, several 3–4 times on the *same*
  page. The drift engine's cooldowns prevent format repeats; you prevent wording repeats.

## Step 5 — Publish via Publer
Route through `vp_social_publisher.py` / `PublerClient`, never a one-off script.
- Auth `Authorization: Bearer-API {key}` **plus a browser User-Agent** or Cloudflare returns
  `error code: 1010`. A 403 is not a dead key.
- Always pass explicit `from`/`to` when listing posts — `GET /posts` silently caps at ~15 without
  them.
- **No Meta Graph API** — all Page tokens died 2026-08-21.

Routing: engagement posts run **store-local** (that store's FB page) so the question comes from a
neighbor, not a corporation — rotate which store leads each week. Brand-level polls go to Brand FB
+ IG + X. Schedule for **late afternoon / early evening**, when people are actually on their phones,
not 2 AM.

## Step 6 — THE REPLY SWEEP (the part that matters most)
Before you finish, check every Valley Pawn post from the **last 7 days** for unanswered comments,
and reply to every single one, in brand voice, as a person.

- Publer exposes comment **counts** but not comment **bodies** for this workspace, and the Meta
  Graph API is dead — so read the comments through the **Chrome session on the Page itself**.
- Reply to all of them. A question gets an answer. A compliment gets a thank-you with something
  specific in it. A complaint gets a real, non-defensive response and a DM offer.
- **The first 60 minutes of comments is the single biggest reach signal on Meta.** The
  `reel-comment-alert` skill exists for the fast path on new Reels; this sweep is the backstop that
  guarantees nothing sits unanswered for a week.

Target: **zero unanswered comments at the end of every run.** Baseline to beat is 18 comments and
0 replies per 90 days.

## Step 7 — Record and log
    /usr/bin/python3 creative_drift.py record --format-id <id> --account <Account> --engagement 0 --reach 0

Log to `#social-media` (C0BMRC2LN3D): posts staged, formats used, **and how many comments you
replied to this week** — that number is the lane's real KPI, so put it in the post every time.

Verify against Publer's actual list, not your manifest (Rule 12). DM Joshua (`D03BHQH5VGT`) only if
the lane shipped nothing at all after remediation, in plain language. Never send failure notices to
a team channel or a manager.

## Step 8 — Close the loop on yesterday's games
If last week's run posted a Guess the Price or What Is This Thing, **reveal the answer in that
post's comments now** if it hasn't been done. Track open games in the run log so none is ever left
hanging.
