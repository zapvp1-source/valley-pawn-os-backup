# monday-bravo-postcheck — 2026-07-27 — STOPPED (guard rail: pipeline data missing)

## What this run found

Checked all four ops channels for a post since local midnight ET (2026-07-27):

| Channel | Phrase | Posted today? |
|---|---|---|
| #aged-inventory-review (C04NGH4FF35) | "Aged Inventory Review" | YES — 2026-07-27 09:00:00 EDT (bot: VP OPS ENGINE) |
| #loan-review (C0B08RS2BMK) | "Past-Due Loan Review" | NO — last post 2026-07-26 21:35:54 EDT (Sunday night) |
| #layaway-review (C04N24STDP1) | "Layaway Review" | NO — last post 2026-07-26 21:35:54 EDT (Sunday night) |
| #employee-performance (C0ATTLPQHR8) | "Employee Sales Rankings" | NO — last post 2026-07-26 21:35:50 EDT (Sunday night) |

The three missing reports' most recent posts all landed within ~4 seconds of each other on Sunday evening (7/26, 9:35 PM ET) — consistent with a single manual/ad-hoc run, not this morning's scheduled Monday pipeline. Trigger file evidence: `triggers/processed/vpops-trigger-dropper-manual-2026-07-26T19-41-20.json` (claimed same evening).

## Guard rail check (per SKILL.md Step 4)

Looked for `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/monday-bravo-combined-2026-07-27.result.json` via osascript (folder is outside the sandbox mount). **Not present.** The most recent `monday-bravo-combined-*.result.json` on disk is dated 2026-07-20 (last Monday) — today's combined pipeline run did not produce a result file.

This matches `/Users/joshuadavis/Documents/Claude/Scheduled/STATUS-monday-bravo-combined-run-2026-07-27.md`, which documents that this morning's `monday-bravo-combined-run` failed outright: it executed in a Cowork sandbox with no access to Parallels/`prlctl`/the Bravo Data Extraction folder, so no pre-flight ran and no trigger was ever dropped for today's combined run.

## What I did NOT do

Per the explicit guard rail in this skill ("if result.json missing... DM Joshua and stop. Do not post to channels."), I did **not** attempt to backfill the three missing reports from the compile skill, and did **not** post anything to any Slack channel. Posting from stale/substitute data would violate the completeness-gate intent of the compile logic, and the source-of-truth combined run never actually captured today's Bravo numbers.

## Live signal worth flagging for next session

At the time of this check (2026-07-27 ~09:08 AM ET), a new trigger file `triggers/vpops-trigger-dropper-2026-07-27T09-06-58.json` was sitting **unclaimed** in the trigger queue (dropped ~2 minutes before this check ran, not yet picked up by the AHK watcher). It's unclear what mechanism dropped it or whether it will produce a valid `monday-bravo-combined-2026-07-27` result. Worth checking on the next pass — if it completes and posts the three missing reports, no further action is needed. If it doesn't within a reasonable window, the same core issue as the combined-run failure applies: this recovery path also needs a real Mac-shell execution context (native Claude Code / local agent), not a Cowork sandbox, to reach Parallels and the Bravo Data Extraction folder.

## Action sent to Joshua

One Slack DM (per the platform failure-alert policy) — no technical detail, no channel posts.
