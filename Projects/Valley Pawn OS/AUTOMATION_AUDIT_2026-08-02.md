# Valley Pawn - Automation Audit
Full Circle Finance Inc | 2 August 2026

## The headline

Your automation fleet is in better shape than it looked. 72 of your 78 scheduled automations are running on time. The other 6 simply have not reached their first scheduled date yet - nothing is broken there.

What was actually wrong was narrower and is now fixed: most tasks were not told how to reach your Mac when they start up, so they would quit early and report a false failure. That is repaired across the board today.

Two real gaps remain.

## 1. The Monday review chain has been broken for three weeks - HIGH PRIORITY

Your Monday morning store review runs in two halves. Part 1 kicks off the data pull. Part 2 fires 90 minutes later, collects the results, and posts everything to Slack.

Part 1 has run every Monday. Part 2 has not run since 13 July.

Three Mondays with no aged-inventory review, no store rankings, no employee sales rankings, no loan-and-layaway review, no first-payment-default ranking. The data was pulled. Nobody ever got the report.

Most likely cause is exactly the problem fixed today - Part 1 would start, fail to reach the machine, and never schedule Part 2. Monday 3 Aug 5:30 AM is the live test.

## 2. Payroll journal entries have not posted to QuickBooks since 22 May - HIGH PRIORITY

weekly-payroll-to-qbo pulls each Friday processed payroll from Gusto and builds journal entries by store. Switched off for ten weeks. BUSINESS_OS.md lists it as business-critical, so this looks unintentional. Needs confirming - ten weeks of payroll entries is not a small catch-up.

## 3. Twenty-one finished automations have never been switched on

Complete, ready-to-run files never registered with the scheduler. Never fired once. Several exist to keep OTHER automations working:

- Session keep-alives: Gusto (30 min), Cloud Cover (4 hrs), WordPress token, Facebook token health check (3 AM). Stop logins and tokens going stale. Absence is a plausible cause of intermittent failures elsewhere.
- Daily store reporting: sold review (7:45 AM), discount review (8:15 AM), loan/inventory text, dashboard data collector (hourly).
- Marketing and reputation: social publisher (pushes approved content live), Chekkit review responder, AI-visibility repair, email cleanup.
- Real estate and admin: Jacksonville + St. Augustine retail property searches (Mondays), monthly CPA report, weekly timekeeping analysis, firearms distributor application monitor.

None switched on. Some may have been abandoned on purpose.

## 4. BUSINESS_OS.md is significantly out of date

Describes 58 scheduled tasks. Actual: 119 registered. Every future session reads it first, so the drift compounds.

## 5. Redundancy is real but low risk

Retired social automations (Wednesday FB, Saturday FB, weekly social, weekly YouTube shorts, daily social) superseded by the content batch system. Already off, harmless clutter.

Standalone weekly reviews (aged inventory, store rankings, employee sales, loan/layaway) are correctly off - they run inside the Monday orchestrator. KEEP THEM OFF. Re-enabling would duplicate work and post duplicate reports.

## What was done today

- Fixed the local-access failure: 73 task files patched, all backed up
- Removed completed one-off tasks: 17 stale registrations deleted
- Archived finished task folders: 18 folders moved to _archive
- Verified: 0 corrupted files, 0 tasks left unguarded

Nothing permanently deleted. Originals in Scheduled/_backups and Scheduled/_archive.

## Review board assessment

Fleet overall: 92 percent firing on cadence. Functioning system, not a broken one. Auditing before flipping switches was correct - the two genuine failures would have been buried under the noise of mass-enabling 21 tasks.

Keep-alives: highest-value items in the unregistered group because they are protective - they prevent failures in automations that already run and already matter. Low cost, low risk.

Everything else unregistered: whether a Jacksonville property search or a daily discount review earns its keep is a business judgement, not a technical one.

Sequencing: enable nothing until Monday confirms the local-access fix worked. If Monday posts land clean, the fix is proven. If not, added load only obscures the diagnosis.

## Next steps in order

1. Monday morning - confirm the Monday reviews post to Slack. Validates today fix.
2. Decide on payroll-to-QBO - deliberate or not? If not, turn on and reconcile the May-August gap.
3. Then enable the keep-alives - four session/token maintenance tasks.
4. Then the remaining 17, one group at a time, watching usage after each.
5. Rebuild BUSINESS_OS.md from live state.

Supporting data: Scheduled/_audit-inventory-20260802.json - per-task inventory of all 140 task files with cadence, last-run, skip counts, output destinations.

---

# CORRECTION - added after verifying Slack, 2 Aug

Finding 1 above was WRONG. I inferred a three-week outage from task timestamps. The Slack record shows the reports ARE landing. Correcting on the record:

## What Slack actually shows

- 13 July - all four reviews posted (aged inventory, loan, layaway, store rankings)
- 20 July - PARTIAL. Store rankings and layaway yield posted. Aged inventory and loan review did NOT. One real missed week.
- 26/27 July - everything posted, but MULTIPLE TIMES

## The actual current problem: duplicate reporting

A second system called VP OPS ENGINE joined the ops channels on 26 July and now posts the same reviews. The Cowork scheduled tasks never stopped. Both are running.

Result on 26-27 July:
- Aged inventory posted twice (26th 21:35, 27th 09:00) - identical numbers
- Loan review posted twice (26th 21:35, 27th 10:54)
- Layaway review posted three times
- Store rankings posted three times (26th 21:35, 27th 08:30, 27th 10:44)

VP OPS ENGINE is not referenced in ANY scheduled task file. It is external to Cowork - most likely the standalone management dashboard stack. So there are now two independent reporting engines covering the same ground, neither aware of the other.

## Why this matters more than the original finding

Duplicate reports train the team to ignore the channel. Worse, the two engines can disagree - if one pulls at 21:35 and the other at 09:00 the next day the numbers differ and nobody knows which is right. That is a credibility problem with the reporting, not just noise.

## Also surfaced

On 27 July Preston posted that the report does not show yield, and Walker asked whether Harrisonburg layaway yield was better than last week and said the format was hard to comprehend. The metric is not landing with the people meant to use it - it needs a week-over-week comparison, not a point-in-time number.

## The fix - decision needed

For each of the four Monday reviews, one engine owns it and the other stands down:

Option A - VP OPS ENGINE owns all four. Disable the Cowork Monday chain (monday-bravo-combined-run, monday-bravo-combined-compile, monday-store-rankings). Cleanest if the external dashboard is the direction of travel.

Option B - Cowork owns all four. Stop VP OPS ENGINE posting to these channels. Keeps everything in one place with the pipeline that already works.

Option C - split by report. Most flexible, most fragile - two systems to maintain forever.

Recommendation: pick A or B, not C. Whichever engine Joshua intends to invest in long term should own all four, and the other should be switched off the same day. Running both is the worst of the three.

Separately: fix the 20 July gap cause once ownership is settled, and rework the Layaway Yield post to show week-over-week change.
