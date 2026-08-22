---
name: vp-content-batch-weekly
description: Daily-cadence Valley Pawn content batch, generated/scheduled once a week (Mon 2 AM) across all 7 days: 7 Brand items/week (1/day → Brand FB + Brand IG + Brand X, ONLY brand tier touches these 3 shared accounts) + 35 store-local items/week (5 stores × 1/day → that store's FB + that store's GBP, mandatory both legs every time, no longer conditional on a deal submission). 42 items/week total. Redesigned 2026-08-04 per Joshua: "at least one post a day on store pages... GBP consistently... X needs to be 7, IG brand 7, FB brand 7, FB store pages 1/day." Community+Humor pillars, AUTHENTICITY STANDARD (real photos/facts only) unchanged. Auto-publishes; #vp-studio-queue is a log.
model: claude-opus-4-8
---

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard, added 2026-08-02).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed with the task.
> 3. If it errors (no such tool available, not connected, tool-not-found): wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **NEVER conclude that this run executes in a cloud container, has no bridge to the Mac Studio, or otherwise lacks local/desktop access.** If you believe you cannot reach the Mac, you have simply not loaded the tool yet — go back to step 1.
>
> **Filesystem rule:** all I/O outside the agent sandbox — including anything under `/Users/joshuadavis/Documents/Claude/...` — goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s inside one call; poll in short increments across separate calls. Guard any command that may exit nonzero with a trailing || true.
> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (v2, Joshua 2026-07-22).** If this run fails or can't complete, send Joshua ONE plain-language Slack DM (channel D03BHQH5VGT): ⚠️ Scheduled task "<task-name>" did not complete — <date>. Nothing technical in it. Never send failure notices to any team channel, store manager, or employee, ever, in any medium. Technical detail goes in the manifest/run log only.

This is an automated, unattended run. Execute autonomously; make reasonable choices and note them. End with `<run-summary>...</run-summary>`.

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails or can't complete its work, post nothing to Slack. Only post once the work is genuinely done.

> ⛔ **NO-PAUSE CANARY (2026-08-04).** Never pause mid-batch to ask Joshua a question or wait for a reaction. Standing instruction, reinforced 2026-08-04: **"i dont need to approve anything here, we need them just to fire, ill correct if need be."** Reliability beats hitting an exact item count — if a real shortfall means shipping less than target, ship what's real and log it; never fabricate and never stall.

## ⭐ IMAGE PIPELINE — FIXED 2026-08-11, READ THIS BEFORE ANYTHING ELSE

**The 2026-08-10 run shipped only 2/26 items because of a real infrastructure gap: there was no way to get a real local/Slack-sourced photo into a Publer post without either Chrome's file_upload (which can't reach files outside this session's own sandbox folders) or a public image host (which didn't exist).** That gap is now closed. `Refine Social Media/publer_client.py` has a new method:

```python
p = PublerClient()
media = p.upload_media("/absolute/path/to/local/photo.jpg", in_library=True, direct_upload=True)
# media["id"] is now a Publer media ID, usable immediately in schedule_post:
p.schedule_post(text=caption, store_keys=["Culpeper", "GBP_Culpeper"], media_ids=[media["id"]], scheduled_at="2026-08-12T10:00:00-04:00")
```

**`upload_media()` uploads DIRECTLY to Publer's own media library via `POST /media` (multipart/form-data) — Publer itself is the public host. No WordPress, no Google Drive, no third-party image host, no interactive confirmation gate, no dependency on Chrome's file picker at all.** Verified live 2026-08-11 (real upload, real media ID returned, `validity` confirmed compatible with Facebook post/story and Instagram post/story).

**This is now the PRIMARY, REQUIRED path for every item with a real photo (Bravo item photo, eBay-pipeline photo, or a photo downloaded from Slack).** Workflow per item:
1. Get the real photo onto local disk. For Slack-sourced photos: download via Chrome (`save_to_disk`, not fetch/base64 — base64 is blocked for Slack file URLs) into a local folder under `Refine Social Media/` (e.g. `deal_of_week_uploads/`), OR read the file path directly if it's already local (Bravo/asset-library images).
2. Call `p.upload_media(local_path, in_library=True, direct_upload=True)` — get back `media["id"]`.
3. Call `p.schedule_post(text=caption, store_keys=[...], media_ids=[media["id"]], scheduled_at=...)` — do NOT use `image_urls` unless the photo is already genuinely hosted somewhere public (rare); `media_ids` is now the default.
4. Verify via `list_posts(state="scheduled", ...)` with explicit `from`/`to` params (see the cap warning below) that the item actually landed before moving to the next one.

**Only fall back to Chrome-UI manual posting if `upload_media()` itself errors** (e.g. file too large, unsupported format) — diagnose the specific error first, same discipline as the MJ-retry protocol. Do not silently revert to "no image, text-only" or to Chrome UI as a first resort now that this path exists — that was the whole problem with the 2026-08-10 run.

**Immediate catch-up:** the 2026-08-10 manifest logged 3 real, fully-sourced, photo-ready items that were held back purely by this now-fixed gap — Culpeper (Coach CCC87 Hadley Convertible Crossbody, $249.99), Waynesboro (Case 1905 75th Anniversary 7-Knife Set, $1,199.99), Roanoke (Maytronics Dolphin Explorer E25 Pool Cleaner, $499.99), sourced from `#deal-of-the-week` 2026-08-03 submissions (Sandi, Chadd, Benjie). By the time this task next fires, check whether those 3 already shipped (search `#vp-studio-queue` and Publer for them dated after 2026-08-11); if not, and the items are still real/in-stock, ship them this run using the new `upload_media()` path with freshly-written non-Deal-branded captions (the Deal-of-the-Week branding/text stays exclusive to `vp-deals-social-wednesday`) — don't let them go stale indefinitely.

## STEP 0 — RUN PREREQUISITES

Before anything else, confirm access: `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/vp_fb_content_strategy.md` must be readable. If not, call `mcp__cowork__request_cowork_directory` on `/Users/joshuadavis/Documents/Claude/Projects`, recheck. If still unreachable, ABORT SILENTLY (no Slack post), run-summary only.

## STEP 0.5 — PILLAR OVERLAY + ADJUST LOOP

Read, in order:
1. `/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/PILLAR_OVERLAY.md` — authoritative Community + Humor rules. Overlay wins over any conflicting skill cache.
2. `/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/weekly-adjustments.json` — Friday digest nudge, ±5% max, never violating Community floor 15% / Humor cap 10%/1-week. Skip if missing or >10 days old.

- **Community: 15-20% of the 42-item pool (6-8 items/week).** Hooks from `hook-library/community.json`, 45-day rotation. NO CTA. Region hooks → that store's slot (FB+GBP only, per routing below); valley-wide hooks → a Brand slot (FB+IG+X).
- **Humor: MAX 1/week, hard cap, not scaled by footprint.** `hook-library/humor.json`, 60-day cooldown, STYLE-D, Brand tier only, skip GBP.

## MAIN WORK — DAILY-CADENCE FOOTPRINT (target: 42 items/week, unchanged from 2026-08-04 redesign)

**Brand tier — 7 items/week (1/day). EVERY Brand item routes to Brand FB + Brand IG + Brand X, all three, every time. Store-local items NO LONGER touch Brand IG or Brand X at all.**

**Store-local tier — 35 items/week = 7 items/store/week (1/day/store), all 5 stores every week. EVERY store-local item routes to that store's FB page + that store's GBP page, both legs, mandatory, every time — GBP is never optional.**

**Total: 42 content items/week, 91 platform posts/week.** Daily pattern: 1 Brand item + 5 store-local items (one per store, same day, staggered times) every day of the week.

**Content sourcing for 7 real items/store/week:**
- Slot 1/week per store: real `#deal-of-the-week` (`C0AVCANK7E3`) submission if one exists (note: keep captions non-Deal-branded — Deal-of-the-Week's own branded posts are `vp-deals-social-wednesday`'s job, not this task's; using the same real item with a fresh caption is fine, reposting the Deal caption verbatim is not).
- Slots 2-7/week per store: real items from that store's freshest Bravo export (`{date}_{STORE}_items-to-price.csv`, `..._aged-inventory-summary.csv`) — "The Find" pillar, real brand/model/condition/price.
- If a store's Bravo export is stale (>24h) AND no fresh deal submission, ship what's real (even fewer than 7 for that store that week), log `actual_items_this_store`, `target_items_this_store: 7`, `shortfall_reason` in the manifest, DM Joshua only if it becomes a pattern (2+ weeks same store).
- **The image-pipeline fix above removes what was, as of 2026-08-10, the single largest cause of shortfall — use it.**

**Manifest:** `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/output/{YYYY-MM-DD}/batch_manifest_{YYYY-MM-DD}.json`. Log per item: tier, store, pillar, routing (`["Brand FB","BrandIG","BrandTwitter"]` or `["FB {store}","GBP {store}"]` only), authenticity_check, photo_gap, and now `image_method: "upload_media"` or `"chrome_ui_fallback"` per item so future sessions can see the fix is actually being used. Log `target_content_items: 42`, `target_per_store: 7`, `actual_content_items`, `store_counts: {CUL,WAY,HAR,LEX,ROA}`.

**The target never licenses fabrication.** Real photos, real sourced facts, always. Ship what's real; log the honest shortfall.

- Deals-of-the-Week source: `#deal-of-the-week` (`C0AVCANK7E3`), last 7 days, one per store max. Skip a store's deal slot if nothing submitted by Wednesday EOD (their other 6 slots still run off Bravo).
- Bravo inventory: `Bravo Data Extraction/output/` — most recent dated files; if >24h stale, log per-store staleness and DM Joshua if it becomes a pattern.
- `#vp-studio-queue` (`C0BHTEUPADB`, private): post the full item card stack as an informational log, not an approval gate.

## AUTHENTICITY STANDARD (2026-07-22, unchanged, applies to all 42 items)

### Caption voice rules
1. Write like a real employee of a small-town VA pawn shop — the read-aloud-behind-the-counter test.
2. Every caption needs at least one concrete, verifiable fact (Bravo data, real Slack event, real hours/services). Zero invented details.
3. Informative before decorative — lead with what it is, condition, price or "ask for it by name," which store, why buying here makes sense.
4. Banned AI-tells: "nestled", "hidden gem", "earns the slow walk", "steeped in history", "look no further", "elevate your", "whether you're X or Y", rhetorical-question openers, em-dash-heavy lyric prose, "We're lucky to call this valley home." Vary sentence length; contractions always.
5. Vary structure across the batch — more chances to repeat at 42 items/week; actively check for it, especially within one store's 7 items.

### Image accuracy rules
1. Real photos first — Bravo/eBay/Slack photos, uploaded via `upload_media()` now. MJ is the fallback for a specific item, never the default.
2. NEVER an AI render of a real named place. Real photo or a different angle — never fake it.
3. MJ renders must match the real item's brand/category/color/scale. Wrong render → regenerate or skip, never ship.
4. Log photo gaps (`photo_gap: true`).

### Pre-publish QA gate (per item, logged as `authenticity_check`)
`caption_human`, `image_accurate`, `facts_sourced` — all three must pass. Failing items get rewritten (max 2 attempts) then skipped + logged.

## NO-APPROVAL POLICY (2026-07-21, reinforced 2026-08-04)

No approval gate, ever. Post the log card to `#vp-studio-queue`, then immediately publish/schedule every item in the same run. The only reasons to skip an item are the existing hard guardrails — never "waiting for Joshua," and never "no image host" anymore (see the fix above).

## MIDJOURNEY CHECK — MANDATORY RETRY PROTOCOL

Real-photos-first (via `upload_media()`) sits above both MJ and Canva. At 42 items/week, MJ throughput needs matter more for the items that genuinely have no real photo. Every run: (1) retry the imagine page up to 3x with 30s waits before calling MJ unreachable, (2) if all 3 fail, diagnose and log the EXACT failure mode under `mj_status`, (3) a Chrome/access-permission gap → DM Joshua that a one-time interactive "Run now" fixes it, (4) genuine MJ-side issue → fall back to Canva WITH the specific reason, (5) MJ preferred whenever working; Canva is fallback only.

## PUBLISHING — PUBLER ONLY

All Meta Graph API paths disabled. Route ALL Meta traffic through Publer. **Primary path: `publer_client.py`'s `schedule_post(media_ids=[...])` after `upload_media()` — see the fix above.** Chrome UI (composer, search-token + JS-query account-picker, GBP Photo tab, green-banner verification) is now the FALLBACK, used only when `upload_media()` itself errors on a specific file.

**Publer verification cap warning:** `list_posts` / `GET /posts` silently caps at ~15 results without `from`/`to` date params, regardless of `limit`. At 42 items/week this WILL be hit constantly — always pass explicit `from`/`to` (`YYYY-MM-DD`).

**Brand IG selection (Chrome-UI fallback only):** Brand FB and Brand IG show as the identical name "Valley Pawn" in Publer's picker — never text-search; use the JS provider-badge query:
```js
[...document.querySelectorAll('.ACLI')].find(el =>
  el.querySelector('.ACLI__name')?.textContent.trim() === 'Valley Pawn' &&
  el.querySelector('.ACLI__provider')?.src.includes('instagram-circle'))?.click();
```
(Not needed on the `upload_media()`/`schedule_post()` API path — `store_keys=["BrandIG"]` resolves unambiguously via `publer_accounts.json`.)

**ONE-MINUTE-GAP RULE:** never fire two posts to the same shared account (Brand IG, Brand Twitter) less than 2 minutes apart. At 1 Brand item/day this is trivial.

**TWITTER/X ROUTING:** Brand tier ONLY (7/week). Store-local items do NOT route to Twitter/X. Trim captions over ~260 chars.

## HARD GUARDRAILS

- NEVER open instagram.com/*, facebook.com/*, x.com/*\twitter.com/* in Chrome against Valley Pawn accounts. All Meta/Twitter goes through Publer.
- MJ fast hours exhausted → pause that item + DM Joshua.
- Bravo export missing/stale >24h for a store → log per-store staleness, DM Joshua if it becomes a pattern.
- Empty caption after 2 retries → skip + DM Joshua.
- "Dixie Pawn" in generated copy → HARD STOP, skip item + DM Joshua.
- No firearms/guns/weapons language on any channel (especially Roanoke).
- Pillar cap breach → re-balance before generating heroes.
- Community: no CTA, ever. Humor: never exceed 1/week.
- Never fire two posts to the same shared account (Brand IG, Brand Twitter) less than 2 minutes apart.
- NEVER an AI render of a real named place. NEVER state an unsourced specific fact.
- NEVER pause mid-batch for approval or input.
- NEVER route a store-local item to Brand IG/Twitter, or a Brand item to a store FB/GBP page.
- NEVER skip the GBP leg of a store-local item.
- **NEVER give up on a real, photo-ready item just because Chrome's file_upload can't reach it — use `upload_media()` first.**

## Timing

Fires Monday 2:02 AM ET via cron `0 2 * * 1`. Generates and SCHEDULES all 42 items across the coming 7 days in this one run. `vp-content-batch-postflight` verifies 90 min later; `vp-content-batch-quota-watchdog` checks per-store/per-platform fill-rate the following Tuesday.

<!-- 2026-08-11: IMAGE PIPELINE FIX. The 2026-08-10 run shipped only 2/26 items (0 store-local) because Chrome's file_upload can't reach files outside its own session sandbox and no public image host existed for the Publer API path. Added `PublerClient.upload_media()` (POST /media, multipart, direct-to-Publer's-own-library, verified live) and `media_ids` support in `schedule_post()`. This is now the PRIMARY image path, Chrome UI demoted to fallback-on-error only. Flagged the 3 real items held back 2026-08-10 (Culpeper Coach bag, Waynesboro Case knife set, Roanoke Dolphin pool cleaner) for catch-up. -->
<!-- 2026-08-04 (2nd pass): FULL ROUTING REDESIGN — Brand tier (7/wk) exclusively on Brand FB+IG+X; store-local (35/wk, 7/store) exclusively on that store's FB+GBP, GBP mandatory. Verified against 3 weeks of live Publer data before redesigning. -->
<!-- 2026-08-04 (1st pass): DOUBLED footprint 13→26 (superseded by the routing redesign above). Added NO-PAUSE CANARY after the 2026-08-03 approval-pause bug. -->
<!-- 2026-07-22: AUTHENTICITY STANDARD. -->
<!-- 2026-07-21 (3rd pass): TWITTER/X ROUTING (narrowed to Brand-only 2026-08-04). -->
<!-- 2026-07-21 (2nd pass, same day): ONE-MINUTE-GAP RULE. -->
<!-- 2026-07-21 (2nd pass): mandatory 3-retry MJ protocol. -->
<!-- 2026-07-21: removed approval gate. -->
<!-- 2026-07-16 (evening): fixed Brand IG account-picker ambiguity. -->
<!-- 2026-07-06: STEP 0/0.5 additions. -->
<!-- migrated to Publer-only publisher 2026-07-04. -->
