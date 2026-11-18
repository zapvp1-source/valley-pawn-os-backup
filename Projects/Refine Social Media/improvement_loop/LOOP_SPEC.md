# Social Improvement Loop — spec (v1, 2026-11-17, Joshua: "we want an improvement loop weekly")

Why: audits and scorecards kept finding problems and stopping at "noted" / "outside scope" / "flagged".
This loop turns every finding into a change, checks the change worked, and keeps going without Joshua.

## When
Weekly, Monday ~10:40 AM ET — after the 8:35 campaign scorecard, BEFORE the 14:30 weekly plan build,
so every change lands in that week's posts. Scheduled task: "Social improvement loop (weekly)".

## Inputs (read, never re-measure what already exists)
CAMPAIGN_SCORECARD.md (newest run), weekly-adjustments.json + adjustments_log.jsonl (Friday digest),
TIMING_CHECK_*.md, FACT_CHECK_LOG.md, engagement_outbound/DAILY_LOG.md + ledger.jsonl + QUEUE.json,
follower_growth_by_store.csv, Valley Pawn OS/CHANGELOG.md (last 7 days), Life OS/HUMAN_QUEUE.md (social rows).

## The one list
improvement_loop/ACTION_LEDGER.json — every finding is a row:
{id, opened, source, finding, action, owner: AUTO|JOSHUA, status: OPEN|DONE|VERIFIED|REVERTED|WAITING,
 metric, baseline, target, recheck_on, done_on, change_note, backup, result_history[], attempts}
A finding in any input with no ledger row = the run is not finished.

## Each run, in order
1. HARVEST: read inputs; add a row for every new problem or opportunity (dedupe by finding).
2. VERIFY: for each DONE row whose recheck_on <= today, measure its metric (Publer post_insights,
   paginated — campaign_scorecard_measure.py) and append to result_history.
   - hit target or clearly better than baseline → VERIFIED.
   - no gain after 2 rechecks → revert from backup (REVERTED) and open the next option as a new row.
3. EXECUTE: every OPEN AUTO row, this run. Rules:
   - backup to Valley Pawn OS/fleet/_backups/<file>.bak-pre-loop-<YYYYMMDD> first;
   - plan.py / community_topics.json / routing / PILLAR_OVERLAY / scorecard tuning rules / outbound RUNBOOK
     are IN scope — "outside scope" is not an allowed outcome;
   - vp_social_publisher.py and publer_client.py: build new alongside, never edit in place;
   - after any planner change: test build (copy of package + plans + ledger on the VM, real planner, next 3 weeks)
     must show 0 collisions and all slots inside posting hours, else revert;
   - one CHANGELOG line per change.
   - a row that can't be done this run gets attempts+1 and a concrete next step; attempts >= 3 → rebuild the approach.
4. ESCALATE: JOSHUA rows only for money, messages to customers/staff not already approved, sign-ins, or
   irreversible changes. One HUMAN_QUEUE row each, with a recommendation and a default.
   Reversible items run the default 7 days after the row is surfaced with no answer.
5. REPORT: write improvement_loop/runs/<YYYY-MM-DD>.md (what was found, executed, verified, reverted, waiting)
   and add one line at the top of CAMPAIGN_SCORECARD.md's newest run:
   "Loop: found N · executed N · verified N · reverted N · waiting on Joshua N".
   No Slack, no DMs. Joshua sees it in the existing reports.

## Hard limits
No paid spend. Giveaway stays paused. Never drop a platform for low reach (keep X, keep Brand FB).
No firearms on social. Facts must be in a source checked that morning. Public Facebook comments/shares/follows
cannot be posted by an unattended run — the loop never tries; it keeps QUEUE.json fresh only.
