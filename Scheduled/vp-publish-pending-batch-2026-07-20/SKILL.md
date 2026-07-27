---
name: vp-publish-pending-batch-2026-07-20
description: One-time: publish the 13-item 2026-07-20 batch that's been sitting unapproved in #vp-studio-queue since yesterday — Joshua no longer wants an approval step, so push it live now and check Midjourney reachability per his request.
---

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


This is a one-time cleanup/catch-up run. Context: the 2026-07-20 vp-content-batch-weekly catch-up run staged 13 items (3 Brand + 10 store-local) in Slack #vp-studio-queue (channel ID C0BHTEUPADB) as an approval-card thread (parent message ts 1784557802.893929, posted 2026-07-20 10:30 AM ET), with the full manifest at `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/output/2026-07-20/batch_manifest_2026-07-20.json`. Nobody approved these — Joshua said today (2026-07-21) "I don't want to approve anything, I will give feedback after postings," meaning the approval-gate workflow is retired (the recurring `vp-content-batch-weekly` task has already been updated to stop gating on approval going forward).

Your job now:

1. Read the full manifest at the path above to get every item's routing tier, caption, target channels, and scheduled_for time.
2. Before publishing, actually test whether Midjourney is reachable this session (Joshua asked "check midjourney again, we want full push this week" — the 07-20 run used Canva for all 13 heroes because MJ was unreachable that session). If MJ is reachable now, you do NOT need to regenerate the existing 13 Canva heroes (they're already made and fine to use as-is) — but note MJ's current availability in your report since Joshua wants to know, and if there's an obvious quick way to add this week's still-missing Deals-of-the-Week (5, requires fresh #deal-of-the-week submissions — check if any exist now) or Reels (2, requires a working MJ Video/ffmpeg path) items to bring this week closer to the full 20-item footprint, do so. If those inputs still aren't available, don't force it — just report clearly what's missing and why.
3. Publish all 13 already-staged items to Publer per their manifest routing/schedule. Route through Publer only (Chrome MCP), one composer per channel per item. Use the Brand IG disambiguation fix for any Brand-tier item targeting Instagram: on the open composer, run
```js
[...document.querySelectorAll('.ACLI')].find(el =>
  el.querySelector('.ACLI__name')?.textContent.trim() === 'Valley Pawn' &&
  el.querySelector('.ACLI__provider')?.src.includes('instagram-circle')
)?.click();
```
instead of typing a name into the account search box — the Brand FB page and Brand IG account share the identical display name "Valley Pawn" in Publer and are only distinguishable by the provider badge icon. For store-local items, use the store name (FB) and the GBP search tokens: Lexington=`Walker`, Culpeper=`James Madison`, Waynesboro=`Broad`, Harrisonburg=`E Market`, Roanoke=`Peters Creek`. Verify each post's scheduled confirmation before moving to the next.
4. Update the manifest (or write a companion `_published` results file next to it) logging each item's outcome (published / failed + reason) and any Publer post ID captured.
5. Post ONE update to the #vp-studio-queue thread (as a reply under the original parent message ts 1784557802.893929) summarizing: "Per your note, publishing this batch directly — no approval needed going forward. X/13 items published, Y skipped (reason). MJ status: reachable/unreachable this session." Keep it short.
6. DM Joshua a one-line summary on Slack: how many of the 13 published, MJ status, and whether Deals/Reels could be added this run or are still blocked and why.

Do not wait for any approval reactions — this run's entire point is that the approval step no longer exists. If something in the manifest is genuinely broken (e.g. a hero image file is missing, a caption is empty), skip just that item, log why, and continue with the rest — don't abort the whole run over one bad item.