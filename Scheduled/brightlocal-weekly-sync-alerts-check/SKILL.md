---
name: brightlocal-weekly-sync-alerts-check
description: Weekly Valley Pawn listings audit — checks GBP, Bing, Apple, Facebook, Yelp for all 5 stores and posts drift report to #ai-marketing (Tuesdays 9am)
---

> 🔧 REPAIRED 2026-07-10: this task's Slack target (#claude-updates) no longer exists, so every run since it was created has posted into the void. Re-pointed at #ai-marketing (C0BCEESUANM, private) so this feed reaches Joshua alongside the other AI-search/GEO signals (vp-ai-search-health-check, vp-ai-visibility-metrics). This task covers Apple Business Connect, Facebook, and Yelp — directories the AI-search checks don't touch — so it stays as a distinct, non-redundant Tuesday check rather than being folded into those.

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

Use the `directory-listing-monitor` skill to run the weekly Valley Pawn listings audit.

Workflow:
1. Load canonical NAP from `valley-pawn-context` skill (including Harrisonburg Ste 22).
2. Check each of the 5 directories (Google Business Profile, Bing Places, Apple Business Connect, Facebook, Yelp) for each of the 5 stores via Chrome MCP. Start with Google, then Bing, Apple, Facebook, Yelp.
3. Classify each listing: match / drift / unknown / critical.
4. Diff against prior week snapshot in `/sessions/funny-practical-hopper/mnt/outputs/listings-snapshots/` to highlight what moved.
5. Save today's snapshot JSON to `listings-snapshots/<YYYY-MM-DD>.json`.
6. Post structured drift summary to Slack channel #ai-marketing (ID C0BCEESUANM; do not DM anyone).
7. If critical drift is found (wrong address, wrong phone, wrong brand name), tag it clearly so Joshua can decide whether to trigger `directory-listing-push`.

Do not make any edits during this run — this skill is monitor-only. Corrections happen through `directory-listing-push`.