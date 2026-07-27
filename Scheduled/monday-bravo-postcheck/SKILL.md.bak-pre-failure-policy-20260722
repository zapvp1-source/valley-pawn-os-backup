---
name: monday-bravo-postcheck
description: Mon 8:15 AM post-check/self-heal: verify the 4 combined-Bravo ops reports posted today; backfill any missing from the pipeline CSVs; silent if all good.
model: claude-sonnet-5
---

Monday post-check / self-heal for the combined Valley Pawn Bravo review. You run ~8:15 AM ET Monday, AFTER `monday-bravo-combined-run` (Part 1, ~5:38 AM) and `monday-bravo-combined-compile` (Part 2, ~75 min later). Your job: confirm today's four ops reports actually posted; backfill any that are missing; stay completely silent if all four are present.

⚠️ FAILURE POLICY — never post error/status/"couldn't finish" noise to ops channels. Only post real report data. If you cannot complete because pipeline data is missing, DM Joshua and stop — never post partial data to a channel.

This is an AUTOMATED run (Joshua not present). Act autonomously; do not ask questions.

STEP 1 — Verify today's posts. Compute today's date in ET. Load the Slack tools via ToolSearch (query: "select:mcp__f92ce7c6-0353-4419-8491-f0843b182ff2__slack_search_public_and_private,mcp__f92ce7c6-0353-4419-8491-f0843b182ff2__slack_send_message"). For each channel, search for a message posted TODAY (since local midnight ET) carrying that report:
- #aged-inventory-review (C04NGH4FF35) — phrase "Aged Inventory Review"
- #loan-review (C0B08RS2BMK) — phrase "Past-Due Loan Review"
- #layaway-review (C04N24STDP1) — phrase "Layaway Review"
- #employee-performance (C0ATTLPQHR8) — phrase "Employee Sales Rankings"
(Do NOT check #store-performance here — store rankings run in a separate flow.)

STEP 2 — If all four posted today → DONE. Stay completely silent: no Slack post, no DM.

STEP 3 — If any are missing → backfill ONLY the missing ones. Follow the canonical compile logic in /Users/joshuadavis/Documents/Claude/Scheduled/monday-bravo-combined-compile/SKILL.md exactly (same formats, the COMPLETENESS GATE, and the loan-balance-from-EOM rule — read the freshest complete `*_end-of-month.csv` `Ending Loan Base` set for the loan denominator and stamp its as-of date; never hard-code or Slack-scrape a balance). Read today's result.json and the report CSVs from `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/` using the Control-your-Mac osascript tool (load via ToolSearch query "computer-use"; the Bravo Data Extraction folder is outside the task sandbox so osascript file reads are required). Post each missing report to its channel. Do NOT repost a report that already posted today.

STEP 4 — Guard rails:
- If `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/monday-bravo-combined-<TODAY>.result.json` is missing or the report CSVs are absent, the pipeline didn't finish — DM Joshua (U03BB52MDSA): "🚦 postcheck <TODAY>: combined pipeline data missing, nothing to backfill" and stop. Do not post to channels.
- After a successful backfill, DM Joshua one line listing which reports were backfilled and to which channels. If a required report (aged-inventory, employee-activity, chekkit-invites) had 0 rows, lead the DM with "🚨 INCOMPLETE RUN" and name the empty report(s).

Stores: CUL, HAR, LEX, ROA, WAY.