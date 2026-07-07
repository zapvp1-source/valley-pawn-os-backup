---
name: brightlocal-weekly-sync-alerts-check
description: Weekly Valley Pawn listings audit — checks GBP, Bing, Apple, Facebook, Yelp for all 5 stores and posts drift report to #claude-updates (Tuesdays 9am)
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

Use the `directory-listing-monitor` skill to run the weekly Valley Pawn listings audit.

Workflow:
1. Load canonical NAP from `valley-pawn-context` skill (including Harrisonburg Ste 22).
2. Check each of the 5 directories (Google Business Profile, Bing Places, Apple Business Connect, Facebook, Yelp) for each of the 5 stores via Chrome MCP. Start with Google, then Bing, Apple, Facebook, Yelp.
3. Classify each listing: match / drift / unknown / critical.
4. Diff against prior week snapshot in `/sessions/funny-practical-hopper/mnt/outputs/listings-snapshots/` to highlight what moved.
5. Save today's snapshot JSON to `listings-snapshots/<YYYY-MM-DD>.json`.
6. Post structured drift summary to Slack channel #claude-updates (do not DM anyone).
7. If critical drift is found (wrong address, wrong phone, wrong brand name), tag it clearly so Joshua can decide whether to trigger `directory-listing-push`.

Do not make any edits during this run — this skill is monitor-only. Corrections happen through `directory-listing-push`.