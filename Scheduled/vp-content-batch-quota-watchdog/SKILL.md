---
name: vp-content-batch-quota-watchdog
description: Tuesday 10 AM ET — reads the last 2 weeks' vp-content-batch-weekly manifests, compares actual content items shipped against the 26-item Brand+store-local target, and DMs Joshua only if fill rate has been materially short 2 weeks running. Makes the "not firing at full volume" pattern visible automatically instead of requiring manual Slack/Publer digging.
model: claude-sonnet-5
---

> **LOCAL ACCESS GATE — DO THIS FIRST.** This task runs on Joshua's Mac Studio and has local access via `mcp__Control_your_Mac__osascript`, which may be deferred rather than pre-loaded. If needed, `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`, probe with `do shell script "echo READY"`, retry every ~20s for up to 12 minutes before concluding it's unavailable. All reads under `/Users/joshuadavis/Documents/Claude/...` go through this tool, never the Write tool.

⚠️ **FAILURE ALERT POLICY:** If this run fails, send Joshua ONE plain-language Slack DM (channel D03BHQH5VGT): `⚠️ Scheduled task "vp-content-batch-quota-watchdog" did not complete — <date>.` Nothing technical in it. Never post to any team channel.

This is an automated, unattended run. End with `<run-summary>...</run-summary>`.

## Why this exists

Created 2026-08-04 after Joshua asked why the weekly social batch wasn't hitting full volume for all stores every cycle. Investigation (same session) found the root cause was never "stores being skipped" — every store does get covered — it's that `vp-content-batch-weekly` has repeatedly shipped BELOW its target item count over the past several weeks (2026-07-20: 13/20 target due to an MJ session glitch; 2026-07-27: 10/20 due to stale Bravo data + missing manager submissions; 2026-08-03: 8/20 due to an approval-pause bug requiring manual recovery). Each of these self-healed and every item that DID ship was verified live in Publer — but nobody had a standing way to notice the volume pattern without manually reading Slack history and cross-checking Publer, which is exactly what this task automates. The Brand+store-local target was also doubled 2026-08-04 (3+10=13 → 6+20=26) per Joshua's direct instruction, making fill-rate tracking more important, not less.

## Job

1. Find the most recent manifest under `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/output/{YYYY-MM-DD}/batch_manifest_{YYYY-MM-DD}.json` and the one before it (most recent 2 dated folders under that `output/` directory).
2. For each, read `routing_summary.total_content_items` (or count the `items` array if that field is absent) — this is the Brand+store-local count actually shipped that week. If the manifest has a `target_content_items` field, use it as the target for that week; otherwise use 26 for manifests dated 2026-08-04 or later, and 13 for manifests dated before that (the pre-doubling target).
3. Compute fill rate = actual / target for each of the 2 most recent weeks.
4. **If fill rate is below 60% for BOTH of the last 2 weeks** (a sustained pattern, not a one-off dip): DM Joshua (channel D03BHQH5VGT) a short, plain-language note — no jargon, no file paths:
   ```
   📊 Social content volume has been running low 2 weeks running — {week1 date} shipped {a}/{target}, {week2 date} shipped {b}/{target}. Worth a look when you have a minute.
   ```
5. **If only 1 of the last 2 weeks is below 60%, or both are at/above 60%:** stay completely silent. A single off week is normal (MJ hiccup, a store manager missed a submission deadline) and does not need Joshua's attention — that's noise, not signal.
6. If fewer than 2 manifests exist yet (early days of this task), stay silent and note that in the run-summary only.
7. Do not touch, re-run, or attempt to fix `vp-content-batch-weekly` itself — this task is read-only observation. If you want to flag a likely cause (MJ, Bravo staleness, an approval-pause recurrence), you may add one short clause naming it in the DM, but do not self-heal or retry anything here — that's `vp-content-batch-postflight`'s job, not this one.

## Cron

Tuesday 10 AM ET (`0 10 * * 2`) — after Monday's batch (2:02 AM) and postflight (3:30 AM) have both had a full day to complete/self-heal, and after `weekly-social-media-recap` (Monday 9 AM) has already given Joshua the raw "what published" numbers in #social-media. This task adds the trend/pattern view on top, DM-only, low-noise.

## Hard rule

Silent unless there's a genuine 2-week pattern. Never posts to any team channel — DM only, and rarely at that.