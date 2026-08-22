---
name: vp-content-batch-postflight
description: Monday 3:30 AM ET post-flight verification for vp-content-batch-weekly (which fired at 2:02 AM). Verifies manifest saved + Slack log cards + Publer publish confirmations, self-heals silent drops. Silent on clean success (the weekly "what published" recap now lives in #social-media via weekly-social-media-recap, not a Joshua DM) — still DMs Joshua on any partial/failure.
model: claude-sonnet-5
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua's DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.

> **REPORTING POLICY (updated 2026-08-04):** Joshua no longer gets a routine "here's what published" DM from this task — that content is now covered every Monday 9 AM ET by the `weekly-social-media-recap` task, which posts a real, Publer-verified recap directly to `#social-media` (channel C0BMRC2LN3D). This task stays completely SILENT on a clean success (all platforms verified, no self-heal needed). It only DMs Joshua when something actually needs his attention: a partial failure, a silent platform drop that couldn't self-heal, or a backfill that needs his go-ahead. Claude (this session) still gets the completion notification either way and can self-heal.

Post-flight verification of Monday 2:02 AM's `vp-content-batch-weekly` run.

**There is no approval step.** Joshua said "I don't want to approve anything, I will give feedback after postings" — `vp-content-batch-weekly` publishes every item immediately after staging the Slack log card in `#vp-studio-queue`; it does not wait for reactions. This task's job is to verify that actually happened (manifest saved, log card posted, AND Publer actually shows the posts scheduled/published) — not to check whether items are "ready to approve."

**PER-PLATFORM VERIFICATION IS MANDATORY, not just a headline count.** Root cause found 2026-07-21: a "13/13 published" DM was wrong in a way that mattered — items 1-4 published fine to Facebook + GBP, but their Instagram leg was silently dropped (never scheduled, never published, never in Publer's Failed bucket — just missing entirely). A count like "13/13 published" is NOT sufficient evidence on its own — it can be true for the FB/GBP legs while Instagram silently fails per-item with zero trace. Twitter/X is NOT part of this pipeline's routing at all (by design — manifests never list it), so don't flag its absence as a bug.

Step 3 verification must be PER-PLATFORM, not just a total-item-count check:
1. Read the manifest's routing_summary for this week — for each item, note which platforms it's supposed to hit (Facebook, Instagram, GBP — per-item, since Brand items are FB+IG only while store items are FB+IG+GBP).
2. In Publer (`app.publer.com/#/calendar/posts`), filter the account sidebar to ONLY the shared Instagram account (`Valley Pawn`, account id `6a35979ebbd130d6e889c0bb`) and check BOTH the "Scheduled" and "Published" tabs for this week's items — confirm every item that should route to Instagram actually appears in one of those two buckets. Do the same spot-check for at least 2 store Facebook accounts and 1 GBP account.
3. If any item is routed to Instagram in the manifest but is absent from both Publer's IG-Scheduled and IG-Published views (and not in Failed either) — that is a silent-drop, treat it as a Step 4 failure requiring self-heal, even if Facebook/GBP for that same item succeeded. Do not let a healthy FB/GBP leg mask a dead IG leg.
4. Track per-platform pass/fail counts internally (e.g. "Facebook 13/13, GBP 10/10, Instagram 9/13 — 4 items missing IG") — this only surfaces in a DM if Step 4 self-heal can't fully recover it (see Step 5).

Then check Publer's calendar for this week — confirm the items from the manifest actually appear as scheduled/published posts, not just staged captions.
- If Slack card exists but Publer shows nothing scheduled for a given platform leg → publishing failed after staging for that leg → Step 4 (retry the publish step specifically for that platform, not the whole batch, if the manifest/captions are already good).
- If Slack card and Publer posts confirm across every routed platform for every item → success path (Step 5, silent).

## Step 4 — Self-heal (no Joshua DM unless it stays broken)

The batch failed silently, staged but didn't publish, or dropped one platform leg. Try to recover:
1. Re-invoke `vp-content-batch-weekly`'s current instructions in-session for the current week (staging + immediate publish, no approval wait) — or for a partial per-platform drop, retry just the missing platform leg for the affected items using the current (fixed) Instagram DOM-query selection method.
2. Watch for errors. Common failure modes:
   - Slack MCP auth-blocked in cron context → invoke skill will succeed because THIS session has Slack access → items get staged now.
   - MJ fast-hours ran out → downgrade to reuse-only mode, produce whatever can be generated from existing library.
   - Bravo export missing → fall back to Slack `#new-inventory` scan for the last 7 days.
   - Publer login expired mid-run → if staging succeeded but publish didn't, this is the likely cause. Retry publish only.
   - Instagram account-picker silently selects nothing (pre-2026-07-21 bug pattern) → this is a PUBLISHING ACTION and requires Joshua's explicit one-time go-ahead in chat before creating/scheduling any new public post — do not auto-create replacement IG posts without asking. Surface the exact missing items and ask.
3. After self-heal, re-run Steps 2 and 3 verification, per platform.

If self-heal SUCCEEDS → jump to Step 5 (silent, nothing to report).
If self-heal FAILS, or requires publishing a new post that needs Joshua's go-ahead → write full diagnostic to `output/{YYYY-MM-DD}/postflight_FAILED.json`. DM Joshua a short note that this week's batch needs a manual look, naming exactly which items/platforms are missing and asking for a go-ahead to backfill — do not stay silent on a real failure now that there's no approval step to catch it downstream.

## Step 5 — Report (silent on success; DM only when something needs Joshua)

**Clean success (all platforms verified for every item, no self-heal needed):** do nothing. Do not DM Joshua. The weekly `weekly-social-media-recap` post to #social-media already covers "what published this week" — a duplicate DM here is exactly the redundancy Joshua asked to remove 2026-08-04.

**Partial failure, silent drop that couldn't self-heal, or a backfill needing a go-ahead:** DM Joshua (channel D03BHQH5VGT), format:
```
⚠️ Week of {YYYY-MM-DD} — content batch needs a look
Per-platform: Facebook {a}/{total}, GBP {b}/{total}, Instagram {c}/{total}
{Name the specific items/platforms missing, and whether a backfill needs your go-ahead}
Publer calendar: https://app.publer.com/#/calendar/week
```

Write the internal verification result (per-platform counts, self-heal actions taken) to `output/{YYYY-MM-DD}/postflight_result.json` either way, so it's available for `weekly-social-media-recap` or any future session to cross-check — but that file is not itself a Slack post.

## Cron

Monday 3:30 AM ET via `0 30 3 * * 1`. Runs 90 min after `vp-content-batch-weekly`. Long enough for the batch to complete, short enough to catch same-day failure.

## Hard rule

Joshua is DM'd ONLY when something needs his attention — a partial/failure, a silent platform drop that couldn't self-heal, or a backfill decision. He is never DM'd a routine "here's what published, no action needed" summary anymore — that's `weekly-social-media-recap`'s job, posted to #social-media, verified independently against Publer. Publishing a brand-new replacement post to backfill a dropped item ALWAYS requires Joshua's explicit go-ahead in that DM/thread before it happens — this is a hard platform rule, not a preference, and standing "don't ask me things" instructions do not override it.

<!-- 2026-08-04: Consolidated with weekly-social-media-recap per Joshua's explicit request ("only post to social media channel, delete the redundant scheduled post to me"). Removed the routine success-case DM (previous Step 5: "✅ Week of ... — N posts published, no action needed") since it duplicated the new Monday 9 AM #social-media recap. Failure/partial/backfill DMs are unaffected — those are alerts, not recaps, and stay on Joshua's DM per the hard failure-alert policy. Backup of prior version: SKILL.md.bak-pre-social-recap-consolidation-2026-08-04. -->
<!-- 2026-07-21: Rewrote for the no-approval-gate world. Was previously "DM only when ready to approve, silent otherwise" — now verifies actual Publer publish (not just Slack staging). -->
<!-- 2026-07-21 #2: Added mandatory per-platform (esp. Instagram) verification after discovering a real silent-drop: items 1-4 published fine to FB/GBP but never reached Instagram, and the prior postflight logic's aggregate "13 published" count was blind to it. -->