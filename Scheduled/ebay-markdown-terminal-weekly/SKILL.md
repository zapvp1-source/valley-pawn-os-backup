---
name: ebay-markdown-terminal-weekly
description: Weekly — closes the "pull" half of eBay's Listing-Age Standard: flags/pulls listings that hit the 30%-off markdown floor with no sale. Posts ONE concise Slack summary (company + per-store) with a linked spreadsheet for full detail.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> **REWRITTEN 2026-09-07.** The script used to post directly to Slack via webhook, one message
> per store with every item bulleted (capped at 40 lines). That flooded #ebay-performance with
> long, illegible messages the first time it ran for real (2026-09-07 — 4 messages, one listing
> 101 items). Joshua's correction: Slack gets ONE concise message (company total + one line per
> store: count + dollar value), never an item bullet-dump. Full item detail goes in a linked
> spreadsheet instead. The script itself no longer touches Slack at all — see "After running"
> below for the new, mandatory steps that replace what the script used to do on its own.

Run the eBay markdown terminal-action check for Valley Pawn. This closes a gap found in the
2026-08-22 eBay Channel Audit: `ebay_markdown_engine.py` cuts listing prices 10%/month up to 3
times (30% off baseline) via the monthly `ebay-markdown-monthly` job, then does nothing further.

## What to run
`~/Documents/Claude/Projects/eBay/ebay_markdown_terminal.py --apply`

This script (built 2026-08-22, rewritten 2026-09-07 — do not modify its core eBay logic without
checking with Joshua first, it makes a real business call about when to pull inventory off eBay)
does NOT touch the existing markdown engine or its state file — it only reads
`~/ebay_markdown_state.json` to find items at 3 cuts (30% off), and tracks its own two-stage
process in `~/ebay_markdown_terminal_state.json`:

- **Stage 1** (item newly seen at 30% off, unsold): flags it — will be pulled from eBay in 14 days
  unless someone intervenes. No eBay write.
- **Stage 2** (14+ days after Stage 1, still unsold, no manual override): ends the eBay listing
  (`EndFixedPriceItem`).

It no longer posts to Slack itself. Instead it writes, every run:
- `~/Documents/Claude/Projects/eBay/markdown_floor_detail_latest.csv` — full item-level detail
  (store, item ID, title, price, status, eBay link) for every item flagged or pulled this run.
  Only written/overwritten if there's at least one row this run.
- `~/ebay_markdown_terminal_summary.json` — compact counts: `company_flag_count`,
  `company_flag_value`, `company_pull_count`, and `by_store: {store: {flag_count, flag_value,
  pull_count}}`.

## After running — build the report yourself, every run

1. Read `~/ebay_markdown_terminal_summary.json`.
2. **If `company_flag_count` and `company_pull_count` are both 0:** post a single one-line rollup
   to #ebay-performance ("eBay markdown terminal check: 0 items at the 30% floor this week — all
   quiet.") so the channel shows the job ran. Skip steps 3-4.
3. **Otherwise**, read `markdown_floor_detail_latest.csv` and build/update a Google Sheet from it
   via the Drive connector (create as CSV content, let it convert to a native Sheet; title it
   `eBay Markdown Floor Detail — <run_date>`). Share it as reader with the store email address
   (`<Store>@fcfpawn.com`, e.g. `Culpeper@fcfpawn.com` — see the `store-credentials` skill for the
   full list) for every store that appears in `by_store` this run. Do not share with stores that
   had zero activity.
4. Post ONE message to #ebay-performance (channel ID `C0ANVN5KX4Y`) shaped like this — company
   total first, then one line per store (count + dollar value), then the Sheet link. No item
   bullets in Slack, ever — that's the whole point of this rewrite:

   ```
   *eBay Markdown Floor — Weekly (<run_date>)*

   Company-wide: <company_flag_count> listings hit the 30%-off floor with no sale, $<company_flag_value>
   in current asking value. Each has 14 days left before it's pulled from eBay.
   [If company_pull_count > 0, add a line: "<N> listings pulled from eBay today after the grace
   period — each needs a store decision: clearance, bundle, donate, or scrap."]

   • <Store> — <count> items, $<value>
   • <Store> — <count> items, $<value>
   [one line per store in by_store, sorted by value descending; omit stores with 0]

   Full detail (item, price, item ID, eBay link, pull date) by store: <Sheet link>
   ```

5. For every item newly pulled (Stage 2) this run, DM the responsible store manager directly — use
   the same store-manager Slack lookup / DM pattern as the `ebay-weekly-quality-fix` task (read its
   SKILL.md at `~/Documents/Claude/Scheduled/ebay-weekly-quality-fix/SKILL.md` if you need the
   manager-mapping reference) — telling them plainly: item pulled from eBay, needs a Bravo decision
   (clearance/bundle/donate/scrap), item ID and title included. This DM is separate from the
   channel post and unaffected by the concise-format rule (it's one item, one manager).
6. Append a one-line entry to `Projects/Valley Pawn OS/CHANGELOG.md` only if something actually
   happened this run (flag_count or pull_count > 0 company-wide) — skip the changelog entry on a
   fully quiet run.
7. If anything failed (an EndFixedPriceItem call errored, a store token expired, the script itself
   errored, etc.), log it to `Projects/Life OS/OPEN_ITEMS_REGISTER.md` per Rule 14 and DM Joshua a
   plain-language one-liner — do not just print the error and stop.

## Safety
This task performs real eBay writes at Stage 2 (ending a listing) and real Slack posts/DMs — this is
intentional and by design, not the exec()-verification mistake from the 2026-08-22 incident. Only
ever run `ebay_markdown_terminal.py` itself for this purpose; never `exec()` or run any OTHER
`~/ebay_*.py` script "to check" something — if you need to inspect one, read it or `py_compile` it,
never execute it.