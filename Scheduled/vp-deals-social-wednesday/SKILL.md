---
name: vp-deals-social-wednesday
description: Wednesday 6 PM ET — pull the week's #deal-of-the-week submissions, use the manager's REAL item photo (MJ only as verified fallback), draft employee-voice captions from submission facts only, stage in Publer for Thursday 10 AM-4 PM.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

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


> ⚠️ **FAILURE HANDLING (Rule 16, supersedes the 2026-07-22 v2 DM policy — updated 2026-09-06).** Failure notices NEVER go to Slack — not to a team channel, not to a store manager, and not to Joshua's DM. If this run fails or cannot complete its core work, append one dated plain-language line plus the technical detail to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/STATUS.md` under a `## Run holds` heading and stop. The next session picks it up from there. Anything that does go to the field stays in plain everyday language — no error codes, no tool or file names. This replaces every 'DM Joshua that it did not complete' and every 'stay silent on Slack' instruction elsewhere in this file.


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
Run the Valley Pawn Deals-of-the-Week SOCIAL layer for this week. This is the social-media companion to the existing Brevo email flow (`vp-deal-of-week-monday-prompt` + `vp-deal-of-week-monday-pick`).

## Step 0 — MANDATORY duplicate check before anything else

The Monday batch (`vp-content-batch-weekly`) and the deal reels lane already publish this week's
Deal of the Week items. On 2026-09-02 this task re-posted all five deals a second time; Culpeper's
tiller landed on the same page three times in three days.

1. `do shell script "cd '/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media' && python3 -m vp_social sync --back 7 --forward 14"`
2. For each store, check the ledger before staging anything:
   `sqlite3 '/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/state/social_ledger.sqlite' "select account_key, scheduled_date, substr(text,1,60) from posts where account_key in ('<Store>','GBP_<Store>') and scheduled_date >= date('now','-2 day') and state in ('scheduled','published')"`
3. If that store's page already has a post for the same product this week, **skip that store entirely**.
   Only fill genuine gaps. Never publish the same deal photo twice to one page.

**Routing (2026-08-04 redesign):** store deal items go to that store's Facebook Page + that store's
Google Business Profile ONLY. Brand IG is not a store-local target — do not add it.

**Submission cutoff is Monday 12:00 PM ET** (not end-of-day Tuesday).

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
