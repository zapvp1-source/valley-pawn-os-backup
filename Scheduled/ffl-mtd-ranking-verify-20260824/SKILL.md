---
name: ffl-mtd-ranking-verify-20260824
description: One-shot 10:30 AM check that today's nics-weekly-mtd-ranking posted to #ffl-transfer-performance; backfill if missing.
---

You are verifying a Valley Pawn scheduled report. Follow the vp-operating-rules skill (Rules 12/15/16 — verify against output, fix forward, NEVER post failure notices or technical jargon to any Slack channel).

1. Read Slack channel #ffl-transfer-performance (C0BPH5T1NFL) via the Slack connector. If a message dated today (2026-08-24) with the MTD FFL transfer ranking already exists, you are done — end silently.
2. If NOT posted: the weekly task `nics-weekly-mtd-ranking` (fires Mondays 9:30 AM, SKILL at /Users/joshuadavis/Documents/Claude/Scheduled/nics-weekly-mtd-ranking/SKILL.md) did not complete. Read that SKILL.md and execute it now end-to-end: pull month-to-date (Aug 1–23) FFL transfers for all 5 stores from Bravo per its instructions, rank stores by transfers + revenue, and post the ranking to #ffl-transfer-performance in its exact historical format (see the 2026-08-17 post in the channel for reference).
3. Before touching Bravo, run the mandatory contention check from the bravo-context skill.
4. If you cannot complete the pull, do NOT post anything to the channel. Log details to a status file in /Users/joshuadavis/Documents/Claude/Scheduled/ and send ONE plain-language DM to Joshua (Slack user D03BHQH5VGT) only if the report will not go out today.