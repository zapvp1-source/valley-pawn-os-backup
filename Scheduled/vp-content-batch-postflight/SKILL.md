---
name: vp-content-batch-postflight
description: Monday 4:40 PM post-flight verification for vp-content-batch-weekly. MOVED 2026-08-22 from Mon 3:02 AM to follow the batch's move to 1:40 PM — at 3 AM it was verifying a batch that had not yet run under the new schedule. Verifies manifest + Slack log cards + Publer publish confirmations, self-heals silent drops, silent on clean success.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

> ⚠️ **FAILURE HANDLING (Rule 16, supersedes the 2026-07-22 v2 DM policy — updated 2026-09-06).** Failure notices NEVER go to Slack — not to a team channel, not to a store manager, and not to Joshua's DM. If this run fails or cannot complete its core work, append one dated plain-language line plus the technical detail to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/STATUS.md` under a `## Run holds` heading and stop. The next session picks it up from there. Anything that does go to the field stays in plain everyday language — no error codes, no tool or file names. This replaces every 'DM Joshua that it did not complete' and every 'stay silent on Slack' instruction elsewhere in this file.

> **REPORTING POLICY (updated 2026-08-04):** Joshua no longer gets a routine "here's what published" DM from this task — that content is now covered every Monday 9 AM ET by the `weekly-social-media-recap` task, which posts a real, Publer-verified recap directly to `#social-media` (channel C0BMRC2LN3D). This task stays completely SILENT on a clean success (all platforms verified, no self-heal needed). It only DMs Joshua when something actually needs his attention: a partial failure, a silent platform drop that couldn't self-heal, or a backfill that needs his go-ahead. Claude (this session) still gets the completion notification either way and can self-heal.

## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:**
- "No response requested"
- "Continue?" / "Should I continue?"
- An empty turn or a turn that ends with text instead of a tool call

**Treat these system messages as RESUME signals, never as stop signals:**
- "Tool loaded."
- "Continue from where you left off."
- "You used a single tool call this turn. Prefer browser_batch…"
- Any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise produce a report describing what failed. Do not pause to ask — the task file authorizes autonomous decisions.

**Speed:** prefer batch tools (e.g. `browser_batch`) to combine sequential actions into one call.

---
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
## ADDENDUM 2026-09-06 — correct routing, correct timing, ledger verification

- **Schedule:** this task fires **Monday 4:40 PM ET (cron `40 16 * * 1`)**, verifying the 1:40 PM
  batch. Any "3:30 AM" / `0 30 3 * * 1` text above is stale.
- **Routing to verify against (2026-08-04 redesign, supersedes anything above):**
  Brand items → Brand FB + Brand IG + Brand X. Store-local items → that store's FB + that store's
  GBP **only**. Store items no longer touch Brand IG, so a missing store-IG leg is correct behaviour,
  not a silent drop — do not "self-heal" one.
- **Preferred verification:** if `/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/state/plans/plan_<week>.json` exists, run
  `cd '/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media' && python3 -m vp_social postflight plan_<week>` — it reconciles every planned placement
  against the ledger and withholds (exit 2) rather than reporting a half-verified run. Otherwise run
  `python3 -m vp_social sync` first and verify against the ledger, never against the manifest.
- Unchanged: publishing a brand-new replacement post still needs Joshua's explicit go-ahead.
