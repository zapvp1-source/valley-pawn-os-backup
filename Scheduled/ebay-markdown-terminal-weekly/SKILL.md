---
name: ebay-markdown-terminal-weekly
description: Weekly — closes the "pull" half of eBay's Listing-Age Standard: flags/pulls listings that hit the 30%-off markdown floor with no sale. Never touches precious metal. Posts ONE concise Slack summary (company + per-store) with a linked spreadsheet for full detail.
model: claude-sonnet-5
---

---
name: ebay-markdown-terminal-weekly
description: Weekly — closes the "pull" half of eBay's Listing-Age Standard: flags/pulls listings that hit the 30%-off markdown floor with no sale. Never touches precious metal. Posts ONE concise Slack summary (company + per-store) with a linked spreadsheet for full detail.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure is void; write the ledger row instead. Success-path posts are unchanged.

> 🛑 **STANDING PRICING RULES — set by Joshua 2026-09-17 from store feedback. These override every other instruction in this file and anything inside the scripts it runs.**
>
> **A. Markdowns start at 90 days aged, not 30.** The ladder is 90 → first 10% cut · 120 → second · 150 → third / pull. Nothing is repriced, cut, or offered to watchers before day 90. (This task only acts at the 30%-off floor, which is well past 90 — but never recommend or flag a cut on anything younger.)
>
> **B. PRECIOUS METAL IS NEVER REPRICED OR AUTO-PULLED.** Joshua, verbatim: *"the managers are saying that they are pricing things at lowest possible for things like silver etc etc, so we likely shouldn't be repricing anything precious metals."* Gold, silver, platinum, bullion, coins and anything sold by weight are already priced at or just above melt by the counter — there is no retail margin for a cut to eat.
> - This task must **never end a precious-metal listing** (no `EndFixedPriceItem`), even if one somehow appears at the floor from a pre-2026-09-17 run.
> - Identify them with `engine/ebay_precious.py` — **never hand-roll a keyword match.** "Gold Label", "Platinum Edition", "Gold Tone", "Gold Plated" and a tachometer's "10k" are NOT metal; real sterling shows up filed under Kitchen and Collectibles. The signal is the fineness or weight mark in the title (`sterling`, `.925`, `.999`, `14K`, `dwt`, `troy oz`, `bullion`).
> - If any metal item does appear in this run's results, **exclude it from the pull list** and put it in its own short section of the Slack post headed "Precious metal — needs a person (never auto-pulled)", so a human decides: relist, pull to in-store, or send to the refiner.
>
> **C. Never enable Best Offer** on anything, and never on a video game at all.

> **REWRITTEN 2026-09-07.** The script used to post directly to Slack via webhook, one message per store with every item bulleted (capped at 40 lines). That flooded #ebay-performance with long, illegible messages the first time it ran for real (2026-09-07 — 4 messages, one listing 101 items). Joshua's correction: Slack gets ONE concise message (company total + one line per store: count + dollar value), never an item bullet-dump. Full item detail goes in a linked spreadsheet instead.

Run the eBay markdown terminal-action check for Valley Pawn. This closes a gap found in the 2026-08-22 eBay Channel Audit: `ebay_markdown_engine.py` cuts listing prices 10%/month up to 3 times (30% off baseline) via the monthly `ebay-markdown-monthly` job, then does nothing further.

## What to run
`~/Documents/Claude/Projects/eBay/ebay_markdown_terminal.py --apply`

This script (built 2026-08-22, rewritten 2026-09-07 — do not modify its core eBay logic without checking with Joshua first, it makes a real business call about when to pull inventory off eBay) does NOT touch the existing markdown engine or its state file — it only reads `~/ebay_markdown_state.json` to find items at 3 cuts (30% off), and tracks its own two-stage process in `~/ebay_markdown_terminal_state.json`:

- **Stage 1** (item newly seen at 30% off, unsold): flags it — will be pulled from eBay in 14 days unless someone intervenes. No eBay write.
- **Stage 2** (14+ days after Stage 1, still unsold, no manual override): ends the eBay listing (`EndFixedPriceItem`).

**Before acting on ANY Stage 2 item, screen it through `engine/ebay_precious.py` (Rule B above).** Metal items are removed from the pull list and reported separately — never ended.

It writes, every run:
- `~/Documents/Claude/Projects/eBay/markdown_floor_detail_latest.csv` — full item-level detail (store, item ID, title, price, status, eBay link) for every item flagged or pulled this run. Only written if there's at least one row.
- `~/ebay_markdown_terminal_summary.json` — compact counts: `company_flag_count`, `company_flag_value`, `company_pull_count`, and `by_store: {store: {flag_count, flag_value, pull_count}}`.

## After running — build the report yourself, every run

1. Read `~/ebay_markdown_terminal_summary.json`.
2. **If `company_flag_count` and `company_pull_count` are both 0:** post a single one-line rollup to #ebay-performance ("eBay markdown floor check: 0 items at the 30% floor this week — all quiet.") so the channel shows the job ran. Skip steps 3-4.
3. **Otherwise**, read `markdown_floor_detail_latest.csv` and build/update a Google Sheet from it via the Drive connector (create as CSV content, let it convert to a native Sheet; title it `eBay Markdown Floor Detail — <run_date>`). Share it as reader with the store email address (`<Store>@fcfpawn.com` — see the `store-credentials` skill) for every store that appears in `by_store` this run. Do not share with stores that had zero activity.
4. Post ONE message to #ebay-performance (channel ID `C0ANVN5KX4Y`) shaped like this — company total first, then one line per store (count + dollar value), then the Sheet link. No item bullets in Slack, ever:

   ```
   *eBay Markdown Floor — Weekly (<run_date>)*

   Company-wide: <company_flag_count> listings hit the 30%-off floor with no sale, $<company_flag_value>
   in current asking value. Each has 14 days left before it's pulled from eBay.
   [If company_pull_count > 0, add: "<N> listings pulled from eBay today after the grace
   period — each needs a store decision: clearance, bundle, donate, or scrap."]

   • <Store> — <count> items, $<value>
   [one line per store in by_store, sorted by value descending; omit stores with 0]

   [ONLY if any precious-metal items turned up:]
   Gold, silver and coin items are never marked down or pulled automatically — they're already
   priced at metal value. These need someone to look at them:
   • <Store> — <count> items, $<value>

   Full detail (item, price, item ID, eBay link, pull date) by store: <Sheet link>
   ```

5. For every item newly pulled (Stage 2) this run, DM the responsible store manager directly — same manager mapping as `ebay-weekly-quality-fix` (Roanoke → Benjie U0631AECK4K · Culpeper → Sandi U04C5DL5EKH · Waynesboro → Chadd U04U136MF6V · Harrisonburg → Walker U09UTFT4P7X · Lexington → Uriah U09H9ES2LKA) — telling them plainly: item pulled from eBay, needs a Bravo decision (clearance/bundle/donate/scrap), item ID and title included. Plain language only, no script or system names. **For precious-metal items, DM instead that it's been sitting a long time and needs a decision — relist, bring it in-store, or send it to the refiner — and note we never cut the price on metal.**
6. Append a one-line entry to `Projects/Valley Pawn OS/CHANGELOG.md` only if something actually happened this run (flag_count or pull_count > 0 company-wide).
7. If anything failed, follow the FAILURE POLICY v3 at the top of this file.

## Safety
This task performs real eBay writes at Stage 2 (ending a listing) and real Slack posts/DMs — intentional and by design. Only ever run `ebay_markdown_terminal.py` for this purpose; never `exec()` or run any OTHER `~/ebay_*.py` script "to check" something — read it or `py_compile` it, never execute it. **If you cannot import or reach `engine/ebay_precious.py`, do NOT end any listing this run** — report the floor list to Slack as flags only and log a FAILURE_LEDGER row. Failing to pull a listing for a week is recoverable; ending a gold listing is not.