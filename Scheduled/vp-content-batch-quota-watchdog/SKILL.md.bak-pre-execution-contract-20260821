---
name: vp-content-batch-quota-watchdog
description: Tuesday 10 AM ET — verifies the daily-cadence targets directly against live Publer data (not just the manifest): Brand FB/IG/X each 7/week, each store's FB+GBP each 7/week. DMs Joshua only on a sustained (2-week) per-account shortfall. Redesigned 2026-08-04 alongside vp-content-batch-weekly's routing redesign.
model: claude-sonnet-5
---

> **LOCAL ACCESS GATE.** Runs on Joshua's Mac Studio, has local access via `mcp__Control_your_Mac__osascript` (may be deferred — `ToolSearch` query `select:mcp__Control_your_Mac__osascript` if needed, probe with `do shell script "echo READY"`, retry ~20s up to 12 min before concluding unavailable). All reads under `/Users/joshuadavis/Documents/Claude/...` go through this tool.

⚠️ **FAILURE ALERT POLICY:** On failure, DM Joshua once (channel D03BHQH5VGT): `⚠️ Scheduled task "vp-content-batch-quota-watchdog" did not complete — <date>.` Nothing technical. Never post to any team channel.

Automated, unattended run. End with `<run-summary>...</run-summary>`.

## Why this exists / what changed 2026-08-04

Originally built to track an aggregate weekly item-count target. Redesigned same day, alongside `vp-content-batch-weekly`'s full routing overhaul, after Joshua gave exact per-platform targets: *"we want at least one post a day on store pages... GBP pages consistently... X needs to be 7, instagram brand needs to be 7, facebook needs to be 7 for branded page but 1 a day for store pages."* An aggregate item count can hit its target while still being wildly uneven per-account (this is exactly what was happening — Brand IG/Twitter were overshooting while individual store FB/GBP pages were under-served). This task now checks live Publer counts **per account**, not a single aggregate number, because that's the only way to actually verify the thing Joshua is asking for.

## Job

1. Load `PublerClient` from `Refine Social Media/publer_client.py`.
2. Compute the trailing-7-days date window (today minus 7 to today), format `YYYY-MM-DD`.
3. For BOTH `state=scheduled` and `state=published`, call `GET /posts` with explicit `from`/`to` params set to that window and `limit=100` (per-call — **never omit from/to, the endpoint silently caps at ~15 results without it and that WILL produce false "missing" conclusions at this volume**, confirmed 2026-08-04). Combine results, dedupe by post id.
4. Group counts by account using `publer_accounts.json`'s store-key mapping. Build a table against these targets:
   - Brand (Facebook): target 7/week
   - BrandIG: target 7/week
   - BrandTwitter: target 7/week
   - Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke (Facebook): target 7/week each
   - GBP_Culpeper, GBP_Waynesboro, GBP_Harrisonburg, GBP_Lexington, GBP_Roanoke: target 7/week each
5. Flag any account at **under 4/week this week** (roughly half of target — a real gap, not rounding noise from schedule-vs-published timing).
6. Compare against last week's same check (read `output/{date}/quota_watchdog_result.json` if a prior run wrote one — see step 8). **Only DM Joshua for an account that was ALSO flagged last week** — i.e. two consecutive weeks under 4/week for that specific account. A single off week is normal (mid-week check timing, a manager missed a submission) and is noise, not signal — stay silent on those.
7. If 2+ consecutive weeks confirmed for one or more accounts, DM Joshua (channel D03BHQH5VGT), short and plain:
   ```
   📊 A few social accounts have been running light 2 weeks running: {account name} {this week}/7, {last week}/7. Worth a look when you have a minute.
   ```
   List every account that qualifies in one DM, not one DM per account.
8. Write this week's full per-account counts to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/output/{YYYY-MM-DD}/quota_watchdog_result.json` (today's date) so next week's run can do the 2-week comparison in step 6. Include every account's count, not just flagged ones.
9. If fewer than 2 weeks of history exist yet, stay silent this run — note in run-summary only.
10. Read-only. Do not touch, re-run, or attempt to fix `vp-content-batch-weekly`. Naming a likely cause in the DM (e.g. "Bravo data looked stale for X that week" if you happen to know it) is fine as one short clause, but don't self-heal or retry here — that's `vp-content-batch-postflight`'s job.

## Cron

Tuesday 10 AM ET (`0 10 * * 2`) — after Monday's batch (2:02 AM) and postflight (3:30 AM), and after `weekly-social-media-recap` (Monday 9 AM, gives Joshua the raw #social-media numbers). This task is the trend/per-account view on top, DM-only, low-noise.

## Hard rule

Silent unless a specific account has a genuine 2-week-running shortfall. Never posts to any team channel — DM only, and rarely at that.

<!-- 2026-08-04: rewritten from an aggregate-item-count check to a per-account (per-platform, per-store) check against live Publer data, matching the same-day routing redesign of vp-content-batch-weekly. The old aggregate version could not have caught the actual problem Joshua reported (uneven distribution across accounts while the total looked fine). -->
