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

> ⛔ **NO-PAUSE CANARY (2026-08-04).** Never pause mid-batch to ask Joshua a question or wait for a reaction — not for approval, not for a judgment call. If something is genuinely ambiguous, treat it as scoped to that one item: skip it, log why in the manifest, DM Joshua per the gap rules below, and keep going with the rest. Standing instruction, reinforced 2026-08-04: **"i dont need to approve anything here, we need them just to fire, ill correct if need be."** Reliability (fires every cycle, every store, every platform) beats hitting an exact item count — if a real shortfall means shipping less than target, ship what's real and log it; never fabricate and never stall.

## STEP 0 — RUN PREREQUISITES

Before anything else, confirm access: `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/vp_fb_content_strategy.md` must be readable. If not, call `mcp__cowork__request_cowork_directory` on `/Users/joshuadavis/Documents/Claude/Projects`, recheck. If still unreachable, ABORT SILENTLY (no Slack post), run-summary only.

## STEP 0.5 — PILLAR OVERLAY + ADJUST LOOP

Read, in order:
1. `/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/PILLAR_OVERLAY.md` — authoritative Community + Humor rules. Overlay wins over any conflicting skill cache.
2. `/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/weekly-adjustments.json` — Friday digest nudge, ±5% max, never violating Community floor 15% / Humor cap 10%/1-week. Skip if missing or >10 days old.

- **Community: 15-20% of the 42-item pool (6-8 items/week).** Hooks from `hook-library/community.json`, 45-day rotation. NO CTA. Region hooks → that store's slot (still carries FB+GBP only, per the routing redesign below — community store posts do NOT get a special exemption from the routing rule); valley-wide hooks → a Brand slot (FB+IG+X).
- **Humor: MAX 1/week, hard cap, not scaled by footprint.** `hook-library/humor.json`, 60-day cooldown, STYLE-D, Brand tier only, skip GBP.

## MAIN WORK — DAILY-CADENCE FOOTPRINT (REDESIGNED 2026-08-04)

**Why this changed:** Joshua, 2026-08-04: *"it seems we are not posting on all our store pages, we want at least one post a day on store pages. also seems like we are not posting to all GBP pages consistently, we are only posting 1 a week on X that needs to be 7, instagram brand needs to be 7, facebook needs to be 7 for branded page but 1 a day for store pages."* Live Publer data (3-week window, 7/21-8/11) confirmed the complaint: shared accounts (BrandIG ~11.7/week, BrandTwitter ~5.3/week) were absorbing traffic from EVERY item (brand AND store-local both routed to them), while individual store FB pages got only ~2.3-2.7/week each and GBP legs were conditional on a real deal submission existing that week — meaning a store with no #deal-of-the-week submission got ZERO GBP posts that week. That's the root of "not posting to all GBP pages consistently." Fixed by fully decoupling which tier touches which accounts:

**Brand tier — 7 items/week (1/day). EVERY Brand item routes to Brand FB + Brand IG + Brand X, all three, every time. Store-local items NO LONGER touch Brand IG or Brand X at all.** This is the only way to hit exactly 7/week on each of those 3 shared accounts without either overshooting (old design) or being blocked by store-tier content gaps.

**Store-local tier — 35 items/week = 7 items/store/week (1/day/store), for all 5 stores every week, no exceptions. EVERY store-local item routes to that store's FB page + that store's GBP page, both legs, mandatory, every time — GBP is never optional or conditional on a deal existing.** This directly fixes both "not posting daily on store pages" and "GBP inconsistent."

**Total: 42 content items/week, 7 (Brand) × 3 legs + 35 (store) × 2 legs = 91 platform posts/week.**

**Daily generation/scheduling pattern:** each of the 7 days gets exactly 1 Brand item + 5 store-local items (one per store — Culpeper, Waynesboro, Harrisonburg, Lexington, Roanoke — same day, staggered times). Pick a consistent daily posting time per store (e.g. Culpeper 10am, Waynesboro 11am, Harrisonburg 1pm, Lexington 2pm, Roanoke 3pm) and a daily Brand slot (e.g. 5pm) so the week has a predictable rhythm — this also naturally satisfies the one-minute-gap rule on shared accounts since Brand only posts once/day.

**Content sourcing for 7 real items/store/week (up from the old 1/store/week #deal-of-the-week-only gate):**
- Slot 1/week per store: real `#deal-of-the-week` (channel `C0AVCANK7E3`) submission if one exists that week.
- Slots 2-7/week per store: pull real items from that store's freshest Bravo export (`Bravo Data Extraction/output/{date}_{STORE}_items-to-price.csv` and `..._aged-inventory-summary.csv`) — real brand/model/condition/price, "The Find" pillar. This is now a DAILY-STRENGTH dependency, not a weekly nice-to-have — Bravo freshness directly gates whether a store can hit its 7/week target.
- If a store's Bravo export is stale (>24h) AND that store has no fresh deal submission, do not fabricate a 7th item — ship what's real (even if that's fewer than 7 for that store that week), log `actual_items_this_store: N`, `target_items_this_store: 7`, `shortfall_reason` in the manifest, and DM Joshua per the existing Bravo-staleness gap rule. A store running short some weeks because the real data wasn't there is honest; inventing a post to hit 7 is not.
- Community/Humor pillar items still count toward each tier's total (Community fills some Brand and some store slots per the overlay; Humor is Brand-only, max 1/week total).

**Manifest:** save to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/output/{YYYY-MM-DD}/batch_manifest_{YYYY-MM-DD}.json`. Log per item: tier, store (if store-local), pillar, day-of-week slot, routing (now either `["Brand FB","BrandIG","BrandTwitter"]` or `["FB {store}","GBP {store}"]` — nothing else), authenticity_check, and photo_gap if applicable. Log top-level `target_content_items: 42`, `target_per_store: 7`, `actual_content_items`, and a per-store breakdown `store_counts: {CUL: N, WAY: N, HAR: N, LEX: N, ROA: N}` so gaps are visible without cross-referencing Publer by hand.

**CRITICAL — the target never licenses fabrication.** Same AUTHENTICITY STANDARD as always: real photos, real sourced facts. If real content only supports fewer than 42 items in a given week, ship what's real and log the honest shortfall per-store. A partial-but-honest week beats a full week with invented details, every time.

- Deals-of-the-Week source: `#deal-of-the-week` (`C0AVCANK7E3`), last 7 days, one per store max counted toward that store's 7. Skip a store's deal slot if nothing submitted by Wednesday EOD (their other 6 slots still run off Bravo) — DM Joshua only if it becomes a pattern, not every single week.
- Bravo inventory: `Bravo Data Extraction/output/` — `{date}_{STORE}_items-to-price.csv` / `{date}_{STORE}_aged-inventory-summary.csv`. Use most recent dated files; if >24h stale, log staleness explicitly per-store and DM Joshua — this now directly constrains that store's ability to hit 7/week, so staleness is a bigger deal than it used to be.
- `#vp-studio-queue` (`C0BHTEUPADB`, private): post the full daily/weekly item card stack as an informational log, not an approval gate (see NO-APPROVAL POLICY below).

## AUTHENTICITY STANDARD (2026-07-22, unchanged, applies to all 42 items)

### Caption voice rules
1. Write like a real employee of a small-town VA pawn shop, not a copywriter — the read-aloud-behind-the-counter test.
2. Every caption needs at least one concrete, verifiable fact (Bravo data, real Slack event, real hours/services). Zero invented details.
3. Informative before decorative — lead with what it is, condition, price or "ask for it by name," which store, why buying here makes sense.
4. Banned AI-tells: "nestled", "hidden gem", "earns the slow walk", "steeped in history", "look no further", "elevate your", "whether you're X or Y", rhetorical-question openers, em-dash-heavy lyric prose, "We're lucky to call this valley home." Vary sentence length; contractions always.
5. Vary structure across the batch — **more important than ever at 42 items/week**; a large batch has far more chances to repeat itself. Actively check for repeated openers/rhythm, especially within a single store's 7 items.

### Image accuracy rules
1. Real photos first — Bravo/eBay/Slack photos. MJ is the fallback for a specific item, never the default.
2. NEVER an AI render of a real named place (street, storefront, landmark). Real photo or a different angle — never fake it.
3. MJ renders must match the real item's brand/category/color/scale. Wrong-scale/wrong-model render → regenerate or skip, never ship.
4. Log photo gaps (`photo_gap: true`) so they can drive store photo requests.

### Pre-publish QA gate (per item, logged as `authenticity_check`)
`caption_human`, `image_accurate`, `facts_sourced` — all three must pass. Failing items get rewritten (max 2 attempts) then skipped + logged. Never ship a failing item to hit the count.

## NO-APPROVAL POLICY (2026-07-21, reinforced 2026-08-04 — see NO-PAUSE CANARY above)

No approval gate, ever. Post the log card to `#vp-studio-queue`, then immediately publish/schedule every item in the same run. The only reasons to skip an item are the existing hard guardrails (empty caption after 2 retries, "Dixie Pawn", firearms language, pillar cap breach, missing Bravo/MJ input, failed authenticity_check after 2 retries, genuine per-store data shortfall) — never "waiting for Joshua."

## MIDJOURNEY CHECK — MANDATORY RETRY PROTOCOL

At 42 items/week, MJ throughput needs matter more (more items may lack a real photo). Every run: (1) retry the imagine page up to 3x with 30s waits before calling MJ unreachable, (2) if all 3 fail, diagnose and log the EXACT failure mode (permission gap / login screen / fast-hours banner / blank page / timeout) under `mj_status`, (3) a Chrome/access-permission gap → DM Joshua that a one-time interactive "Run now" fixes it, that's different from an MJ outage, (4) a genuine MJ-side issue → fall back to Canva WITH the specific reason, (5) MJ preferred whenever actually working; Canva is fallback only. Real-photos-first still sits above both.

## PUBLISHING — PUBLER ONLY

All Meta Graph API paths disabled. Route ALL Meta traffic through Publer. Drive via Chrome MCP: one composer per channel per item, search-token + JS-query account-picker (never positional clicks). GBP needs the Photo tab before upload. Verify the green success banner AND re-check the item actually appears in Scheduled/Published before the next composer. **Prefer the Publer API client (`Refine Social Media/publer_client.py`, `schedule_post` with `image_urls`) over Chrome UI whenever a public image URL exists** — faster, avoids the Chrome-UI picker/gap fragility. Chrome UI remains the fallback for real Slack-sourced photos with no public host yet.

**Publer verification cap warning:** `list_posts` / `GET /posts` silently caps at ~15 results without `from`/`to` date params, regardless of `limit`. At 42 items/week this WILL be hit constantly — always pass explicit `from`/`to` (`YYYY-MM-DD`) when checking this week's items. A false "missing post" conclusion happened 2026-08-04 from exactly this — the post existed the whole time.

**Brand IG selection (verified live):** Brand FB and Brand IG show as the identical name "Valley Pawn" in Publer's picker. Never text-search for it. On the open composer, run:
```js
[...document.querySelectorAll('.ACLI')].find(el =>
  el.querySelector('.ACLI__name')?.textContent.trim() === 'Valley Pawn' &&
  el.querySelector('.ACLI__provider')?.src.includes('instagram-circle'))?.click();
```
Confirm the Post Preview shows Instagram-style before continuing. **Since only the 7 Brand items/week touch this account now (was every item before), the one-minute-gap risk on shared accounts is much lower — one Brand item/day gives natural spacing — but still verify presence in Scheduled/Published after each action, never trust the toast alone.**

**ONE-MINUTE-GAP RULE:** Instagram/Twitter reject a 2nd post to the same account within ~1 minute, and Publer can show a false-positive "success" toast while the post silently vanishes (never in Published/Scheduled/Drafts/Failed/Recycling — just gone, with only a hover-tooltip warning icon as any trace). Never fire two posts to the same shared account (Brand IG, Brand Twitter) less than 2 minutes apart; schedule (don't immediate-publish) and stagger. At 1 Brand item/day this is now easy — one clean daily slot per shared account.

**TWITTER/X ROUTING (redesigned 2026-08-04 — Brand tier ONLY, was every item before).** Every Brand item (7/week) routes to the shared Twitter/X account (`Joshua Davis` in Publer) alongside FB+IG. Store-local items do NOT route to Twitter/X anymore — this is what brings X down to exactly 7/week from its prior ~5-12/week (it was absorbing store-tier traffic too). Trim captions over ~260 chars to fit; keep sourced facts, drop flourish. Twitter/X posts still respect the one-minute-gap (now trivial at 1/day).

## HARD GUARDRAILS

- NEVER open instagram.com/*, facebook.com/*, x.com/*\twitter.com/* in Chrome against Valley Pawn accounts. All Meta/Twitter goes through Publer. NEVER hit developers.facebook.com/apps/*.
- Meta-insight-only data need → log gap + DM Joshua. No browser fallback.
- MJ fast hours exhausted → pause that item + DM Joshua, never silently relax-mode.
- Bravo export missing/stale >24h for a store → log per-store staleness, DM Joshua if it becomes a pattern (2+ weeks for the same store).
- Empty caption after 2 retries → skip + DM Joshua.
- "Dixie Pawn" in generated copy → HARD STOP, skip item + DM Joshua.
- No firearms/guns/weapons language on any channel (especially Roanoke).
- Pillar cap breach → re-balance before generating heroes.
- Community: no CTA, ever. Humor: never exceed 1/week.
- Never fire two posts to the same shared account (Brand IG, Brand Twitter) less than 2 minutes apart.
- NEVER an AI render of a real named place.
- NEVER state an unsourced specific fact.
- NEVER pause mid-batch for approval or input — see NO-PAUSE CANARY.
- **NEVER route a store-local item to Brand IG or Brand Twitter, and NEVER route a Brand item to a store FB or GBP page** — the whole point of this redesign is exact per-account weekly counts; cross-routing breaks that.
- **NEVER skip the GBP leg of a store-local item** — it is mandatory, not conditional on a deal existing.

## Timing

Fires Monday 2:02 AM ET via cron `0 2 * * 1`. Generates and SCHEDULES (not immediate-publishes) all 42 items across the coming 7 days in this one run — Publer holds and fires each at its scheduled time, so "1/day" happens automatically once scheduling is correct, without needing 7 separate daily runs. `vp-content-batch-postflight` verifies 90 min later; `vp-content-batch-quota-watchdog` checks per-store/per-platform fill-rate the following Tuesday (updated 2026-08-04 to check the new per-store-per-platform targets, not just an aggregate total).

<!-- 2026-08-04 (2nd pass, same day): FULL ROUTING REDESIGN per Joshua's explicit per-platform targets ("at least one post a day on store pages... GBP consistently... X needs to be 7, IG brand 7, FB brand 7, FB store 1/day"). Decoupled shared accounts (Brand IG, Brand Twitter) so ONLY the 7 Brand items/week touch them (was every item, all 26+ of them, causing massive overshoot on IG/Twitter while individual store FB pages and GBP legs were under-served and conditional). Store-local now 35 items/week (7/store, was 4/store from the earlier same-day doubling), FB+GBP mandatory both legs every time. Verified the complaint against 3 weeks of live Publer data before redesigning (BrandIG ~11.7/wk, BrandTwitter ~5.3/wk, individual store FB ~2.3-2.7/wk, GBP conditional on deal submissions) — this supersedes the earlier 2026-08-04 "double to 26 items" edit, which only doubled volume without fixing the routing/distribution problem Joshua was actually describing. -->
<!-- 2026-08-04 (1st pass): DOUBLED the Brand+store-local footprint from 3+10=13 to 6+20=26 (superseded same day by the routing redesign above). Added NO-PAUSE CANARY after the 2026-08-03 approval-pause bug (unresolved root cause, mitigation only). -->
<!-- 2026-07-22: added AUTHENTICITY STANDARD — employee-voice captions, sourced facts, real-photos-first, no AI renders of real places, pre-publish authenticity_check gate. Overrides conflicting style guidance elsewhere. -->
<!-- 2026-07-21 (3rd pass): added TWITTER/X ROUTING (originally all items — narrowed to Brand-only in the 2026-08-04 redesign above). -->
<!-- 2026-07-21 (2nd pass, same day): added ONE-MINUTE-GAP RULE after 2 of 4 backfilled IG posts silently failed despite clean success toasts. -->
<!-- 2026-07-21 (2nd pass): mandatory 3-retry MJ protocol with diagnosis. -->
<!-- 2026-07-21: removed approval gate per Joshua's direct instruction. -->
<!-- 2026-07-16 (evening): fixed Brand IG account-picker ambiguity; confirmed #vp-studio-queue + Canva auth cleared the two blockers holding this batch dark since 2026-06-29. -->
<!-- 2026-07-06 (evening): added STEP 0.5 pillar overlay + adjust loop. -->
<!-- 2026-07-06: added STEP 0 folder-access prerequisite. Pointed Deals source to #deal-of-the-week. Corrected inventory filenames. -->
<!-- migrated to Publer-only publisher 2026-07-04. -->
