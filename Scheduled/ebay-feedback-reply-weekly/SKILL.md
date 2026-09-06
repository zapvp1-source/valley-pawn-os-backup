---
name: ebay-feedback-reply-weekly
description: Weekly — replies to unanswered negative/neutral eBay feedback across all 5 Valley Pawn stores via the Trading API, and DMs Joshua a plain-language summary.
---

Reply to unanswered eBay buyer feedback for Valley Pawn (Full Circle Finance Inc), all 5 stores.

Read first: `valley-pawn-context` (brand voice) and `vp-operating-rules` (Rules 16 and 18 govern
anything posted or sent). Background on why this task exists and what is already known:
`~/Documents/Claude/Projects/eBay/EBAY_ACCOUNT_HEALTH_2026-09-05.md`.

## Step 1 — pull the open items (read-only)

    cd ~ && /usr/bin/python3 "$HOME/Documents/Claude/Projects/eBay/ebay_feedback_replies.py"

Writes `~/ebay_feedback_open.json`. IMPORTANT: eBay's GetFeedback does NOT return our own replies,
so "unanswered" cannot be read from the API. The script filters against its own record at
`~/ebay_feedback_answered.json`, which is written whenever a reply posts AND whenever eBay says one
already exists. Never delete that file — without it this task will re-answer old feedback.

## Step 2 — decide what to answer

Only reply to feedback left in the LAST 12 MONTHS. Older items are settled history and replying now
only resurfaces them publicly. If nothing qualifies, stop: DM Joshua one line saying there was
nothing to answer, and post nothing.

## Step 3 — write the replies

eBay replies are PERMANENT — they cannot be edited or deleted. 500 character limit. Joshua's
standing direction on tone (2026-09-05): take ownership, and make clear we don't like that the
buyer had a bad experience.

- Name the specific thing that went wrong and own it plainly. Never argue, never imply the buyer is
  wrong, never use their name.
- Offer a concrete remedy where one fits — refund the difference, send the missing accessory,
  accept a return — and invite them to message the store.
- NEVER claim an internal process change ("we've since changed how we test items") unless it
  actually happened and you can verify it. Rule 18 applies to reassuring claims too.
- Reply in the buyer's language first if they wrote in another language, then English.
- Two or three sentences. No corporate filler.

Write them to `~/Documents/Claude/Projects/eBay/feedback_replies_<YYYY-MM-DD>.json` as a list of
{"store", "feedback_id", "item_id", "text"} objects. Anything that would commit more than a routine
remedy does NOT get posted — hold it and put it in the DM for Joshua to decide.

## Step 4 — post

    cd ~ && /usr/bin/python3 "$HOME/Documents/Claude/Projects/eBay/ebay_feedback_replies.py" --post "<that file>"

Each line prints POSTED, ALREADY ANSWERED, or FAILED. ALREADY ANSWERED is not an error — it means
eBay already has a reply we couldn't see, and the id is recorded so it won't come back. The run can
take several minutes; if the shell call appears to time out, wait and read the output file rather
than re-running (a re-run is safe but wasteful).

## Step 5 — report

Slack DM to Joshua only (D03BHQH5VGT). Plain language, no jargon, no error text (Rule 16). How many
replies went out, which stores, and anything deliberately held back and why. Nothing to any channel.

Then append one line to `~/Documents/Claude/Projects/Valley Pawn OS/CHANGELOG.md` if replies posted,
and log anything held back or any remedy we owe a buyer in
`~/Documents/Claude/Projects/Life OS/OPEN_ITEMS_REGISTER.md` per Rule 14.
