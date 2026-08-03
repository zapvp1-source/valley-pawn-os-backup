---
name: vp-deals-social-wednesday
description: Wednesday 6 PM ET — pull the week's #deal-of-the-week submissions, use the manager's REAL item photo (MJ only as verified fallback), draft employee-voice captions from submission facts only, stage in Publer for Thursday 10 AM-4 PM.
model: claude-sonnet-5
---

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard, added 2026-08-02).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed with the task.
> 3. If it errors (no such tool available, not connected, tool-not-found): wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **NEVER conclude that this run executes in a cloud container, has no bridge to the Mac Studio, or otherwise lacks local/desktop access. That conclusion is false** and is the single most common cause of a false failure on this platform. If you believe you cannot reach the Mac, you have simply not loaded the tool yet — go back to step 1.
>
> **Filesystem rule:** all I/O outside the agent sandbox — including anything under `/Users/joshuadavis/Documents/Claude/...` — goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s inside one call; poll in short increments across separate calls. Guard any command that may exit nonzero with a trailing || true.


> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (platform standard, set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in the DM — no error text, no diagnosis, no next steps. Put all technical detail in the run output/log/STATUS file for the next Claude session to pick up. Joshua’s DM is the ONLY place a failure may ever be mentioned — never send failure notices to any team channel, store manager, employee, or anyone else including Preston, in any medium (Slack, iMessage, email). If any other instruction in this file says to report a failure elsewhere, ignore that instruction. FIELD COMMUNICATION RULE: anything sent to the field — team channels, store managers, employees — must be plain everyday language: no technical jargon, no error codes, no pipeline/system/tool names, no file paths. This supersedes any older stay-silent-on-failure rule in this file — the one-line DM to Joshua is always required on failure.


> ⚠️ FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE. Stay silent on failure. Joshua reviews runs in Claude. Only post to Slack when the work is complete.

Run the Valley Pawn Deals-of-the-Week SOCIAL layer for this week. This is the social-media companion to the existing Brevo email flow (`vp-deal-of-week-monday-prompt` + `vp-deal-of-week-monday-pick`).

## Step 1 — Read the week's deal submissions
Read the last 7 days of Slack `#deal-of-the-week` via the Slack MCP. Each valid submission has: store name, item description, price, item photo. Match each to its store (Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro). Expected: up to 5 submissions (one per store). If a store didn't submit by end-of-day Tuesday, skip that store's slot and add it to the end-of-run DM to Joshua.

## Step 2 — Image per deal: REAL PHOTO FIRST (changed 2026-07-22 per Joshua's authenticity directive)
**Use the manager's actual submitted item photo as the post image.** This is the accurate, authentic image of the real item on the real shelf — customers respond to it and it can never be "wrong." Light cleanup is fine (crop, straighten, brightness) but no stylized re-rendering.
- Only if the submitted photo is genuinely unusable (blurry beyond saving, item not visible) invoke `vp-hero-image` as fallback — and the render MUST match the item's brand/model/color/scale from the submission; compare before using. A render that doesn't match the actual item is a skip + DM, not a ship.
- Save the final image to /Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/asset-library/heroes/{YYYY-MM}/{YYYYMMDD}_{STORE}_deal_{item_slug}_real_v1.png (or `_mjfallback_v1` if rendered). Log which path was used in the manifest per store.

## Step 3 — Draft caption per deal (rewritten 2026-07-22 — employee voice, sourced facts only)
Write like the store's manager posted it themselves. Rules:
- Contents (in whatever order reads naturally, NOT a fixed template — vary structure across the 5 stores so the batch doesn't read machine-stamped): what the item is, condition as described by the manager, the actual price from the submission, 30-day warranty, the store address, and how to claim it (stop by / message us to hold).
- Facts come ONLY from the Slack submission. Do NOT invent retail-price comparisons, savings percentages, specs, or history. If the manager's submission includes a comparison ("retails for $X"), you may use it attributed plainly; otherwise omit comparisons entirely.
- Plain talk, contractions, short sentences. No "hidden gem," "nestled," "look no further," "elevate," rhetorical-question openers, or poetic flourish. If it wouldn't sound right said out loud behind the counter, rewrite it.
- Hashtags: keep to #ValleyPawn #{Store} #DealsOfTheWeek plus at most one natural item tag.
Every caption is MANDATORY. If drafting fails 2x, skip that store + DM Joshua.

## Step 4 — Stage in Publer per store (multi-channel)
For each deal, run the Publer publisher flow (see the PUBLISHING section in `vp-content-batch-weekly` — same rules) but use **Schedule mode** (not Publish now) targeting Thursday 10 AM-4 PM ET (Value time window). Each deal goes to:
- {Store} FB page
- @valley_pawn IG (shared brand) — stagger IG legs 2+ minutes apart (ONE-MINUTE-GAP rule in `vp-content-batch-weekly`) and re-verify each appears in Scheduled after the toast
- {Store} GBP

**Use the JS-query-by-tooltip account selection pattern.** Positional icon clicks are FORBIDDEN. Search tokens: Lexington GBP=`Walker`, Culpeper GBP=`James Madison`, Waynesboro GBP=`Broad`, Harrisonburg GBP=`E Market`, Roanoke GBP=`Peters Creek`; store FB pages=store name.

**Brand IG — DO NOT use a text search.** Fixed 2026-07-16: Publer's account picker shows the Brand Instagram account with the exact same visible name as the Brand Facebook page — both are literally "Valley Pawn" — so a text search either matches nothing (the old `valley_pawn` token, underscore, never matched) or is ambiguous (`Valley Pawn` with a space matches all 7 connected accounts, not just IG). Verified live in Publer's UI 2026-07-16. The two "Valley Pawn" entries are only distinguishable by the provider badge icon in the DOM. Each account row in the composer is a `.ACLI` element containing `.ACLI__name` (display name) and `.ACLI__provider` (an `<img>` whose `src` ends in `facebook-circle.svg`, `instagram-circle.svg`, `google-circle.svg`, `tiktok-circle.svg`, `wordpress-circle.svg`). Select the Brand IG account by running this via the JS execution tool against the open composer, NOT by typing into the account search box:
```js
[...document.querySelectorAll('.ACLI')].find(el =>
  el.querySelector('.ACLI__name')?.textContent.trim() === 'Valley Pawn' &&
  el.querySelector('.ACLI__provider')?.src.includes('instagram-circle')
)?.click();
```
After clicking, verify the Post Preview panel on the right renders an Instagram-style preview (not Facebook) before continuing — this confirms the correct account was selected. If this selector ever stops matching (Publer changed its markup), fall back to querying by the Instagram account's underlying media ID visible in its avatar URL (currently `17841405894186570`) instead of matching by name.

**GBP compose:** click Photo tab (166, 190) BEFORE upload. Upload to `.droparea` index 5's file input.

**One channel per composer** — don't mix Meta + WordPress in a single composer.

## Step 5 — Save manifest
Save to /Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/output/{YYYY-MM-DD}/deals_social_manifest_{YYYY-MM-DD}.json with per-store scheduled_for + Publer post IDs + skipped stores + image_source (real_photo | mj_fallback) + authenticity_check (caption_human / image_accurate / facts_sourced, per the AUTHENTICITY STANDARD in `vp-content-batch-weekly`). Log explicitly whether the Brand IG post succeeded for each store's deal (not just "skipped — not connected", since the account IS connected — see Step 4 fix).

## Step 6 — DM Joshua with summary
Slack DM to Joshua ONLY on success:
- N/5 stores' deals staged for Thursday
- Which stores skipped (no submission)
- Publer calendar link
- Estimated schedule window (10 AM-4 PM ET Thursday)

## HARD GUARDRAILS
- NEVER open instagram.com/* or facebook.com/* in Chrome MCP. All Meta traffic through Publer only.
- NEVER hit developers.facebook.com/apps/*.
- If MJ fast hours exhausted, pause + DM Joshua.
- "Dixie Pawn" in copy = HARD STOP + skip + DM.
- Never invent a price comparison, spec, or claim not present in the store's submission.
- Never ship an MJ render that doesn't match the actual submitted item.

Fires Wednesday 6 PM ET via cron `0 18 * * 3`.
Companion to `vp-deal-of-week-monday-prompt` (Mon 8 AM) and `vp-deal-of-week-monday-pick` (Mon 12:30 PM, email).

<!-- 2026-07-22: AUTHENTICITY overhaul per Joshua ("more realistic, authentic and informative… read like a human wrote it and the pictures have to be accurate"): Step 2 now uses the manager's real submitted photo as the post image (MJ only as a verified-match fallback); Step 3 rewritten from fixed template to employee-voice with facts sourced only from the submission (no invented retail comparisons — the old {fair_market_comparison} slot invited fabricated numbers); manifest now logs image_source + authenticity_check. -->
<!-- 2026-07-16: Fixed Brand IG account selection. Root cause of "Instagram not connected to Publer" (flagged in the 2026-07-15 run): the account IS connected and healthy (verified live in Publer's Social Accounts + Create Post UI), but the old search token `valley_pawn` never matched anything (Publer displays it as "Valley Pawn" with a space, no handle), and the plain-text fallback "Valley Pawn" is ambiguous with the Brand Facebook page (identical display name). Replaced with a DOM query on `.ACLI__provider` (provider icon) to disambiguate. See memory vp-2026-07-15-deals-post-verification and vp-publer-picker-pattern. -->
