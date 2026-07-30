# Discount Outlier Review — STATUS

Last updated: 2026-07-29

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
