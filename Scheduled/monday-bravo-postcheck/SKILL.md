---
name: monday-bravo-postcheck
description: Mon 8:30 AM post-check/self-heal: verify the 4 combined-Bravo ops reports posted (compile now fires at a fixed 8:00 AM ET after the Sunday pull); backfill any missing.
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


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