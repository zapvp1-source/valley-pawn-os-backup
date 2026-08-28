---
name: ebay-markdown-terminal-weekly
description: Weekly — closes the "pull" half of eBay's Listing-Age Standard: flags/pulls listings that hit the 30%-off markdown floor with no sale, so they don't sit there forever.
model: claude-sonnet-5
---

Run the eBay markdown terminal-action check for Valley Pawn. This closes a gap found in the
2026-08-22 eBay Channel Audit: `ebay_markdown_engine.py` cuts listing prices 10%/month up to 3
times (30% off baseline) via the monthly `ebay-markdown-monthly` job, then does nothing further.
154 items channel-wide were projected to hit their final cut on 2026-09-01 with no next step —
the "pull" half of the "eBay Listing-Age Standard (Reprice & Pull)" policy was unimplemented.

## What to run
`~/Documents/Claude/Projects/eBay/ebay_markdown_terminal.py --apply`

This script (built 2026-08-22, do not modify its core logic without checking with Joshua first —
it makes a real business call about when to pull inventory off eBay) does NOT touch the existing
markdown engine or its state file — it only reads `~/ebay_markdown_state.json` to find items at 3
cuts (30% off), and tracks its own two-stage process in `~/ebay_markdown_terminal_state.json`:

- **Stage 1** (item newly seen at 30% off, unsold): posts to Slack #ebay-performance that the item
  hit the floor and will be pulled from eBay in 14 days unless someone intervenes. No eBay write.
- **Stage 2** (14+ days after Stage 1, still unsold, no manual override): ends the eBay listing
  (`EndFixedPriceItem`) and posts to #ebay-performance that it needs a Bravo-side decision
  (in-store clearance, bundle, donate, scrap).

## After running
1. Read the script's output. Report what happened this run (items newly flagged at Stage 1, items
   pulled at Stage 2, anything still in its grace period, any errors) in a short Slack post to
   #ebay-performance if the script itself didn't already post a per-item message (it posts
   individually per item; you don't need to duplicate that, but DO post a one-line rollup if
   nothing happened, e.g. "eBay markdown terminal check: 0 items at 30% floor this week" so the
   channel shows the job ran).
2. For every item newly pulled (Stage 2) this run, DM the responsible store manager directly — use
   the same store-manager Slack lookup / DM pattern as the `ebay-weekly-quality-fix` task (read its
   SKILL.md at `~/Documents/Claude/Scheduled/ebay-weekly-quality-fix/SKILL.md` if you need the
   manager-mapping reference) — telling them plainly: item pulled from eBay, needs a Bravo decision
   (clearance/bundle/donate/scrap), item ID and title included.
3. Append a one-line entry to `Projects/Valley Pawn OS/CHANGELOG.md` only if something actually
   happened this run (a Stage 1 flag or a Stage 2 pull) — skip the changelog entry on a fully quiet
   "0 items" run to avoid noise, but note the quiet run isn't a failure.
4. If anything failed (an EndFixedPriceItem call errored, a store token expired, etc.), log it to
   `Projects/Life OS/OPEN_ITEMS_REGISTER.md` per Rule 14 and DM Joshua a plain-language one-liner —
   do not just print the error and stop.

## Safety
This task performs real eBay writes at Stage 2 (ending a listing) and real Slack posts/DMs — this is
intentional and by design, not the exec()-verification mistake from the 2026-08-22 incident. Only
ever run `ebay_markdown_terminal.py` itself for this purpose; never `exec()` or run any OTHER
`~/ebay_*.py` script "to check" something — if you need to inspect one, read it or `py_compile` it,
never execute it.