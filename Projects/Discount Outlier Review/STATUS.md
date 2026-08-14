# Discount Outlier Review — STATUS

Last updated: 2026-08-13 (evening)

## 2026-08-13 (evening) — WIRED TO #discount-review + ANNUAL RUNNING TOTALS ADDED

Joshua created the private Slack channel **#discount-review (`C0BQ6JA27MX`)** and asked for the
report to be team-visible with a running annual discount total, by store and company.

### Changes

- **Destination switched to the team channel.** `SLACK_CHANNEL` default in
  `run_daily_discount_review.py` changed `D03BHQH5VGT` (Joshua's DM) → `C0BQ6JA27MX`. The
  task SKILL.md STEP 6 posts there too. **Failure notices still go to Joshua's DM ONLY** —
  never to the team channel, per the standing failure-alert policy. Since the team now reads
  this, the daily post must stay plain per the Field Communication Standard.
- **Year-to-date totals added** (`compute_ytd()`). Every daily post now shows, per store AND
  for the company: today's discount dollars *and* the running calendar-year total, on the
  same line. The Top-10-by-discount-% list is unchanged (Joshua explicitly wanted it kept).
- **Every store appears every day.** The per-store board now unions "stores with sales today"
  with "stores that have traded at all this year," so a store that's closed (Wednesday) or
  simply had no sales still shows `no sales today | YTD $X`. Previously a quiet store vanished
  from the board and its cumulative number with it.
- **YTD is derived, not accumulated.** `compute_ytd()` re-reads the per-day summary JSONs in
  `daily/` for the current year and sums them, deliberately EXCLUDING the target date (whose
  numbers come from the current run in memory). So re-running a day recomputes instead of
  double-counting, and there's no separate running-total ledger that can drift. A malformed
  day file is skipped rather than breaking the post. New summary fields: `ytd_year`,
  `ytd_days_counted`, `ytd_total_discount_dollars`, `ytd_by_store`.
- Backup: `run_daily_discount_review.py.bak-pre-ytd-2026-08-13`.

### Verified

Dry-run against real 2026-08-12 data (channel unset so nothing posted): compiles clean,
YTD = $1,448.93 company across 2 selling days, per-store YTD CUL $607.88 / HAR $156.43 /
LEX $419.84 / ROA $150.62 / WAY $114.16, all 5 stores rendered, Top 10 intact.

### Also changed outside this project (see `Sold Margin Review`)

`sold-review` was still running on the OLD buggy `jewelry-margin-sold` cell — meaning it was
exposed to the exact store-picker-garbage and silent-missing-CSV failures fixed here, while
posting to a **team** channel (#sold-review). Both `sold-review` and `discount-review` now
read the fixed `sold-discount-detail` cell, and both gained a REUSE-FIRST step: whichever
runs first pulls, the other reuses the CSVs. They were previously dropping byte-identical
triggers ~36 min apart — two full 5-store Bravo cycles for one dataset.
`run_daily_sold_review.py` got the new filename pattern at the front of its
`_FILENAME_CANDIDATES` (backup: `.bak-pre-sold-discount-detail-2026-08-13`); old patterns
retained so historical data still parses.

---

## 2026-08-13 (earlier)

## 2026-08-13 (later) — FIXED AND PROVEN LIVE ✅ — first real report delivered

Both bugs found in the morning run are fixed, and the report Joshua actually wanted has
been produced and posted. **The entry below this one describes the broken state and is
kept for history — it is superseded by this section.**

### What was built (100% additive — Rule #4)

- **NEW** `Bravo Data Extraction/reports/SoldDiscountDetail.ahk` — clone of
  `JewelrySoldMargin.ahk` with both fixes. The shared `jewelry-margin-sold` cell, its
  handler, and the jewelry-scrap project that owns them were **not touched**, so that
  project's behavior is completely unchanged.
- **NEW** cell `sold-discount-detail`, registered in `bravo_watcher.ahk` by appending one
  `#Include` and one `REPORT_HANDLERS` line at the file's own "add new ones here" anchors.
  Verified strictly additive: stripping the two new lines reproduces the backup byte-for-byte
  (`bravo_watcher.ahk.bak-pre-sold-discount-detail-2026-08-13`).
- `run_daily_discount_review.py` — added the new filename pattern to the **front** of the
  existing `_FILENAME_CANDIDATES` list; old patterns retained as fallbacks so previously
  pulled data still parses. Backup: `run_daily_discount_review.py.bak-pre-new-cell-2026-08-13`.

### The two fixes

1. **Header-only CSV on a genuine zero-sale day.** The old empty-grid branch set
   `row_count := 0` and returned "success" without writing anything, so a quiet day was
   indistinguishable on disk from a cell that never ran. Now writes the schema header, making
   "ran, no sales" a positive, checkable fact.
2. **Grid identity validation.** `WriteBuysGridToCsv` searches the *entire* UIA root for
   `DataItem`s, so it can latch onto any grid that happens to be alive — which is exactly how
   WAY's "5 rows" turned out to be the Global Access store picker (`DisplayCode,Store`).
   The new handler classifies the grid before accepting a single row, re-checks identity on
   every scroll pass, and applies a final column check before writing. Anything that doesn't
   look like sold-inventory data is refused rather than written.

### Proven live — trigger `sold-discount-detail-2026-08-13T13-13-41` (2026-08-12 data)

`status: success` on all 5 stores (previous run: `partial`, 1 hard error, 0 usable stores).

| Store | Result | Evidence |
|---|---|---|
| CUL | 20 real rows | header `Number,Status,Category,Description,Cost,Price,Last Sold Price,Date`; valid grid detected in **4s** |
| HAR | 0 sales | 68-byte header-only CSV written |
| LEX | 0 sales | 68-byte header-only CSV written |
| ROA | 0 sales | 68-byte header-only CSV written |
| WAY | 0 sales | 68-byte header-only CSV — **no store-picker garbage**, confirming the old "5 rows" was fabricated |

`missing_stores` is now empty. Compile produced 18 rankable items (2 generic-SKU rows
excluded), avg discount 13%, $308 total off ticket, **4 flags, 0 sold into a loss**, Excel at
`daily/2026-08-12_discount_review.xlsx`. Report posted to Joshua's DM.

Corrupt WAY file moved to `Bravo Data Extraction/output/_quarantine/` with a `.CORRUPT-store-picker-grid`
suffix so the compile script's fallback patterns can never pick it up.

### Honest caveats

- The identity check was **not** exercised against a live store-picker collision this run —
  the picker simply never appeared. The defense is in place and its reject path is coded, but
  it has not yet fired in anger. If it ever does, the log line to look for is
  `[grid] WARN: found a grid that is NOT the sold-details grid`.
- CUL was the only store with sales on 2026-08-12, so the multi-store roll-up math
  (weighted company average across stores) is still only exercised on a single store.
- 4 of 5 stores burn the full 180s render timeout on a zero-sale day, so a quiet day costs
  ~23 min of pipeline time. Works correctly, just slow — a cheap early-exit "no rows" probe
  would be the obvious future optimization, not a correctness issue.
- **The task is still NOT registered with the scheduler** (on disk, never enabled, per
  `BUSINESS_OS.md` LIVE-STATE). It now works when triggered; enabling it on a daily cadence
  is a separate decision for Joshua.

---

## 2026-08-13 (earlier) — SUPERSEDED — first live run, bugs found

First live full-day run (manually triggered; task is still NOT registered with the
recurring scheduler per `BUSINESS_OS.md` LIVE-STATE — it's on disk, never enabled).
Target date: 2026-08-12. Trigger `discount-review-2026-08-13T08-27-03` completed
(`status: partial`) in ~23 min. `run_daily_discount_review.py` ran clean (EXIT:0) and
correctly reported `items: 0` / `slack_skipped: true` given what it could see — so
**nothing was posted to Slack, which was the right call by the script**. But the
underlying pull has a real bug, verified against actual output on disk (Rule #12), not
just the run log:

- **CUL**: cell errored — `UIA click sequence failed: ClickByName: element not found:
  Custom Reports` after a `BackToDashboard hops exhausted` recovery attempt. No CSV
  written (expected, given the error).
- **HAR, LEX, ROA**: result.json marked all three `"status": "success"`, `"row_count": 0`,
  with an `output_path` — but **no CSV file exists on disk at that path for any of the
  three**. The run log shows `[grid] rendered but returned 0 rows — treating as
  legitimate empty result` then straight to `step 8: exit editor` — it appears the
  handler's 0-row path never actually writes a (header-only) CSV, unlike the >0-row path.
  So "success + 0 rows" is currently indistinguishable on disk from "never ran" — the
  compile script correctly refused to treat missing files as confirmed quiet days and
  reported them as `missing_stores` instead. That's the compile script behaving safely;
  the gap is upstream in the handler.
- **WAY**: result.json says `"status": "success"`, `"row_count": 5`, and a CSV *was*
  written — but its contents are **`DisplayCode,Store` / CUL,HAR,LEX,ROA,WAY mapped to
  store names** — i.e. some kind of store-picker/lookup grid, not sold-item rows. None of
  the expected columns (Number, Status, Category, Description, Cost, Price, Last Sold
  Price, Date) are present. The grid-capture step almost certainly grabbed the wrong UI
  element for WAY specifically (5 rows == 5 stores is probably not a coincidence).

Net effect: **0 of 5 stores produced trustworthy sold-item data on this run.** This is
exactly the scenario the "First live run note" below anticipated. Per that note and per
Rule #4 (additive-only): did **not** touch `jewelry-margin-sold`, `JewelrySoldMargin.ahk`,
or `bravo_watcher.ahk`. Did not retry/relaunch — the failure pattern (wrong grid on a
"success", missing file on a "success") looks like deterministic handler logic, not a
transient login/watcher stall, so a relaunch would likely reproduce it rather than fix it.
Sent Joshua the one-line failure DM per the platform failure-alert policy; no technical
detail there — it's all here for the next session.

**For the next session:** before this task is trusted enough to register on a schedule,
someone (or a future session, with Joshua's sign-off, per `expert-review-board` since this
is a handler-behavior question) needs to look at `JewelrySoldMargin.ahk`'s 0-row and
grid-capture logic — specifically whether it's reading the correct grid control after
"Claude Sold Inv Details" renders with few/no rows. Since that AHK handler is shared with
the jewelry-scrap project, any fix should be coordinated, not made unilaterally by this
task's owner. Until fixed, re-running discount-review will likely reproduce the same
result. Old note below (2026-07-29) is superseded by this entry for "not yet proven live."

## What this is

Daily point-of-sale discount outlier report. For every item sold yesterday across all 5
Valley Pawn stores, compares the ticketed/asking `Price` against the actual `Last Sold
Price` (both already recorded in Bravo), ranks discounts by store and company, and flags
heavily-discounted items (>=20% off OR >=$50 off ticket price; anything sold at or below
cost is always flagged as "into a loss" regardless of %/$ threshold). Sales-side
discounting-behavior signal, distinct from Sold Margin Review's realized-margin math.

## Built so far

- `run_daily_discount_review.py` — full compute/rank/flag/Excel/Slack script. Verified via
  `py_compile` and a standalone demo against real 40-row CUL sample data (see
  SCHEMA_NOTES.md for the placeholder-price bug found and fixed before shipping).
- `SCHEMA_NOTES.md` — data source, column schema, both data-quality gotchas.
- Reuses the EXISTING `jewelry-margin-sold` pipeline cell / "Claude Sold Inv Details"
  saved Bravo report as its data source — no new Bravo report, AHK handler, watcher
  restart, or pipeline cell was built or touched.

## Decisions made (Expert Board, 2026-07-28)

- Dual threshold: >=20% off OR >=$50 off (not %-only or $-only — each alone misses a real
  case the other catches). Both tunable after 2-4 weeks of live data.
- Weighted (not simple) average discount % at store/company level, to avoid cheap-item
  skew distorting the headline number.
- Generic/bulk SKUs (bare numeric item numbers) and firearm-paperwork placeholder rows
  ($0.01 ticket price) are excluded from ranking/flagging — footnoted, not silently
  dropped from the data-quality count.
- **Slack destination:** no `#discount-review` team channel exists, and there is no tool
  available (Slack MCP, browser, or otherwise) to create a new Slack channel
  autonomously. Rather than block the feature on Joshua manually creating one, the script
  defaults to posting daily to Joshua's own Slack DM (channel `D03BHQH5VGT`, the same
  channel sold-review already uses for failure alerts) via
  `DISCOUNT_REVIEW_SLACK_CHANNEL`. If Joshua later creates `#discount-review` and wants
  the team to see it, set that env var to the new channel ID in the scheduled task's
  SKILL.md and it switches destinations with no other change.

## Scheduled task

- Name: `discount-review`, SKILL.md at
  `/Users/joshuadavis/Documents/Claude/Scheduled/discount-review/SKILL.md`, modeled on
  `sold-review`'s proven structure (health-gate -> drop trigger -> poll -> compile ->
  post -> DM-only-on-failure).
- Cadence: 8:15 AM ET daily (after pawn-walk 6:30 AM and sold-review 7:45 AM, so Joshua
  reads all 3 back to back without them colliding on the shared Bravo pipeline).
- Registered via `mcp__claude-code-remote__create_trigger` (cron, UTC) — never local
  CronCreate, per platform standard.

## Not yet proven live

- No live full-day CSV pull has been run yet through this script end-to-end (only the
  40-row partial CUL sample used for demo/verification). The first live run will be the
  scheduled task's first firing, which will drop a real single-day trigger for all 5
  stores against the existing `jewelry-margin-sold` cell, exactly like sold-review does
  for `sold-yesterday` — same proven mechanism, different (pre-existing) report name.
- An attempt to drop a one-off trigger manually from this interactive session to test
  early was blocked by the platform's own safety classifier (writing directly into the
  live Bravo `triggers/` queue from an interactive session is treated as a sensitive
  production-pipeline mutation). This is not a bug in the design — sold-review and every
  other scheduled task drop their triggers via `do shell script` from INSIDE a
  scheduled-task session (see its SKILL.md), never via a direct file write from an
  interactive session, so `discount-review`'s SKILL.md follows that exact same
  already-proven pattern and is not expected to hit the same block once it runs on its
  own schedule.
- First-run outcome (success, partial, or failure) should be checked the morning after
  the scheduled task is registered and first fires — either by Joshua's Slack DM, or by
  reading `daily/{date}_discount_review_summary.json` in this folder.

## Explicitly NOT built (out of scope / deferred)

- No new Slack channel (no tool exists to create one; DM-first design above avoids
  needing it).
- No changes to `jewelry-margin-sold`, `JewelrySoldMargin.ahk`, `bravo_watcher.ahk`, or
  any other existing pipeline cell, handler, or scheduled task — this build is 100%
  additive.
