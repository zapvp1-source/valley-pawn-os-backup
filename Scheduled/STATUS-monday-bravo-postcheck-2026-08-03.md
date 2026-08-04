# monday-bravo-postcheck — 2026-08-03 — BACKFILLED (root cause found)

## What this run found

Checked all four ops channels for a post since local midnight ET (2026-08-03, checked ~8:23 AM ET):

| Channel | Phrase | Posted today (before this run)? |
|---|---|---|
| #aged-inventory-review (C04NGH4FF35) | "Aged Inventory Review" | NO — last post 2026-08-01 (unrelated "Aged Markdowns Complete" chat msg); last real report post 2026-07-27 09:00 EDT (VP OPS ENGINE) |
| #loan-review (C0B08RS2BMK) | "Past-Due Loan Review" | NO — last post 2026-07-27 10:54 EDT (VP OPS ENGINE) |
| #layaway-review (C04N24STDP1) | "Layaway Review" | NO — last post 2026-07-27 10:54 EDT (VP OPS ENGINE) |
| #employee-performance (C0ATTLPQHR8) | "Employee Sales Rankings" | NO — last post 2026-07-27 09:15 EDT (VP OPS ENGINE) |

## Guard rail check (per SKILL.md Step 4)

`monday-bravo-combined-2026-08-03.result.json` **exists** (started/finished 2026-08-03T06:17:25, status "partial"). All cells needed for the 4 required reports succeeded cleanly for all 5 stores:
- `aged-inventory-summary` — 5/5 success, 16 rows each
- `loans-75-days-past-due` — 5/5 success (1-row summary each, valid incl. CUL's 0-count)
- `layaways` — 5/5 success (1-row summary each)
- `employee-activity` (2026-08-01, MTD window) — 5/5 success, 7-10 rows each

Only failures in the result.json: `chekkit-invites` HAR + ROA ("EnsureStore failed") and `fpd-cohort` CUL ("EnsureStore failed") — neither is one of the 4 required channels for this task, not backfilled here.

**Guard rail passed** → proceeded to backfill per canonical `monday-bravo-combined-compile/SKILL.md` logic (Steps 1-3 only; Step 4 store-performance and Step 4.5 FPD are out of postcheck's scope, not attempted).

## What I backfilled

Computed and posted all 4, using compile SKILL's exact math/format:
1. **Aged Inventory Review** → #aged-inventory-review. Cleanest: Waynesboro (9.40%). Worst: Roanoke (20.75%). Company total 15.62%.
2. **Past-Due Loan Review** → #loan-review. Loan balance denominator from freshest complete EOM set: **2026-07-29** (5/5 stores' .xlsx present in `output/`, extracted "Ending Loan Base" via openpyxl — no `.csv` EOM files exist on disk currently, only `.xlsx`; compile SKILL's literal `.csv` path reference is stale, adjust that skill or note for next session). Company loan balance $720,406.75. All 5 stores ✅ within 5% (closest ROA 4.28%). EOM data is 5 days old — within the 8-day freshness window, no DM flag needed.
3. **Layaway Review** → #layaway-review. No Locate layaways company-wide.
4. **Employee Sales Rankings** → #employee-performance. Period 8/1–8/3. Top: Walker Tapley $2,393.73. 9 employees ranked (Preston Peters + $0 earners + SYSTEM excluded per rule). Company Total (Total Store column sum, all 5 stores, incl. excluded employees) = $8,654.57.

Also wrote `/Users/joshuadavis/Documents/Claude/loan-layaway-results-latest.json` (the `weekly-loan-layaway-manager-dms` 9 AM downstream dependency) with today's per-store loan/layaway data — this would otherwise have fed stale 7/27 data to that task.

**Not done** (out of postcheck's scope, flagging for awareness): Step 4 store-performance post, Step 4.5 FPD post, Step 5 Word/Excel file saves, chekkit-inactives stash for Tuesday's task. If these are needed, a manual run of `monday-bravo-combined-compile` (or a scope expansion of postcheck) would be required.

## ROOT CAUSE — why this happened (important, needs Joshua's attention)

`monday-bravo-combined-compile` (Part 2 of the Monday pipeline) is registered as a **one-time task, currently `enabled: false`, last fired 2026-07-13**. It has not fired since. Per its own description, Part 1 (`monday-bravo-combined-run`) is supposed to schedule a fresh one-shot instance of Part 2 each Monday ~75 min out — that clearly stopped happening (or stopped succeeding) at some point after 7/13.

Timeline that explains the gap:
- 7/26: VP Ops Engine (native launchd, Jobs A-D) went live and took over posting aged-inventory / loan-layaway / employee-rankings / store-rankings to the same 5 channels — this is why 7/26 and 7/27 posts in these channels are from bot "VP OPS ENGINE", not Claude/Cowork. `monday-bravo-combined-compile` being disabled around this time would make sense (avoid duplicate posts, per the CHANGELOG's 7/27 note about `monday-bravo-combined-run` causing dupes).
- 8/2: VP Ops Engine was **stood down** (all 12 launchd agents unloaded, project tabled) per CHANGELOG.
- 8/3 (today): First Monday since the stand-down. `monday-bravo-combined-run` (Part 1) fired fine at 5:38 AM and pulled all the data successfully (result.json confirms). But `monday-bravo-combined-compile` (Part 2) never fired — it's still sitting disabled from 7/13 — so nothing posted until this postcheck manually compiled and posted from the raw CSVs.

**Net: the Cowork-side Monday reporting pipeline currently has no live Part 2.** Unless `monday-bravo-combined-run`'s "schedule the compile task" step is fixed (or Part 2 is re-enabled/re-created with correct weekly recurrence), this postcheck will have to backfill by hand every Monday going forward. Recommend next session investigate why Part 1 isn't successfully creating/updating the Part 2 one-shot task, and either fix that or convert Part 2 to a proper recurring task on a fixed ~75-min-after-Part-1 offset instead of a one-shot re-scheduled task.

## Action sent to Joshua

One Slack DM: backfill summary + root cause pointer to this file.
