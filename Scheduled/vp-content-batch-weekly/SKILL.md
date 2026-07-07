---
name: vp-content-batch-weekly
description: Weekly Valley Pawn content batch — 3 Brand + 10 store-local + 5 Deals + 2 Reels (20 total), now with Community pillar (15-20%) + Humor pillar (≤10%) + Friday-digest adjust loop. Brand posts hit FB + IG + Twitter. Publer-only publisher. Self-healing.
model: claude-sonnet-5
---

This is an automated run of a scheduled task. The user is not present to answer questions. Execute autonomously; make reasonable choices and note them in your output. Only take "write" actions (send/post/create/update/delete) that this task file explicitly asks for. When in doubt, produce a report. End your response with <run-summary>one or two sentences on what you found and whether anything changed since last run</run-summary>.

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do.

## STEP 0 — RUN PREREQUISITES (added 2026-07-06; the 2026-07-06 run failed because the Projects folder was not mounted)

Before doing anything else, confirm access to the Valley Pawn project files. The batch depends on `/Users/joshuadavis/Documents/Claude/Projects/` (Bravo exports, Valley Pawn Studios asset library + output, the strategy doc).

1. Check whether `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/vp_fb_content_strategy.md` is readable.
2. If it is NOT readable, call `mcp__cowork__request_cowork_directory` with path `/Users/joshuadavis/Documents/Claude/Projects` to mount it, then re-check.
3. If the folder still cannot be accessed after that, **ABORT SILENTLY** — post nothing to Slack (per the failure policy), and end with a run-summary explaining the folder was unreachable. Do not proceed with missing files.
4. Read the authoritative strategy doc at the exact path in step 1 as your Step-1 context source. It supersedes the copy referenced as `outputs/vp_fb_content_strategy.md` in the skill. If the skill and this doc conflict, this doc wins.

## STEP 0.5 — PILLAR OVERLAY + ADJUST LOOP (added 2026-07-06 strategic build)

Also read, in this order:
1. `/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/PILLAR_OVERLAY.md` — **authoritative** Community + Humor pillar rules. If it conflicts with the vp-content-batch skill cache, the OVERLAY WINS.
2. `/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/weekly-adjustments.json` — written by last Friday's vp-publer-analytics-friday digest. Apply its `action` as a pillar nudge (±5% max, never violating any cap/floor: Community floor 15%, Humor cap 10% / 1 per week, and all vp_fb_content_strategy caps). If the file is missing or >10 days old, skip the nudge.

Pillar additions this build enforces every week:
- **Community pillar: 3–4 of the 20 items (15–20%).** Hooks from `Refine Social Media/hook-library/community.json` — rotate regions, skip hooks used <45 days ago, write `last_used_at` back after picking. NO Valley Pawn CTA, no product mention; address footer at bottom only. Region hooks → that store's GBP+FB (store-local tier); valley-wide hooks → Brand tier. STYLE-B; real local photos preferred over MJ when available.
- **Humor pillar: MAX 1 item this week (10% rolling cap).** Hooks from `hook-library/humor.json` — 60-day cooldown, STYLE-D Polaroid Playful only, Brand tier, skip GBP. Hard boundaries in the JSON `_meta.rules.boundaries` — read and obey them. Any image text goes through `~/.vp-studio/scripts/compose_text_on_hero.py` (MJ TEXT RULE).

## MAIN WORK

Run the weekly Valley Pawn content batch. **Invoke the `vp-content-batch` skill** — it is the authoritative source for routing, caption, time-window, pillar rules, and Deals-of-the-Week Step 3c-bis. Do NOT duplicate the skill's logic from this prompt; trigger it. Feed it the strategy doc read in STEP 0 AND the pillar overlay from STEP 0.5.

Default footprint: **3 Brand + 10 store-local statics + 5 Deals-of-the-Week + 2 Reels = 20 items** (Community items fill 3–4 of these slots per the overlay; Humor at most 1), each routed correctly, captioned (mandatory), scheduled across the 30/30/30/10 windows, staged in Slack `#vp-studio-queue` as an approval card stack, with a manifest saved to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/output/{YYYY-MM-DD}/batch_manifest_{YYYY-MM-DD}.json`. Log each item's pillar (including `community` and `humor`) in the manifest so the Friday digest can close the loop.

- Deals-of-the-Week source channel is Slack **`#deal-of-the-week`** (channel ID `C0AVCANK7E3`) — read the last 7 days, one deal per store, skip any store that didn't submit by Wednesday EOD and DM Joshua.
- Bravo inventory lives in `Bravo Data Extraction/output/` as `{date}_{STORE}_items-to-price.csv` and `{date}_{STORE}_aged-inventory-summary.csv` (NOT `inventory_export_*.csv`). Use the most recent dated files; if >24h stale, log + DM Joshua.
- **`#vp-studio-queue` staging channel:** if it does not exist in the workspace, do NOT invent a substitute channel silently — create the staging card content, save the manifest, and DM Joshua that the channel needs to be created, then hold staging. (As of 2026-07-06 this channel did not yet exist.)

## PUBLISHING — PUBLER ONLY (as of 2026-07-04)

All Meta Graph API paths are disabled (Meta app blocked; brand IG flagged 2026-07-04). Route ALL Meta traffic through Publer. The prior `facebook-post` Graph-API flow is retired. After Joshua approves items in `#vp-studio-queue`, drive Publer via Chrome MCP: one composer per channel per item, using the search-token account-picker pattern (JS-query-by-tooltip, never positional icon clicks). GBP posts require the Photo tab before upload. Verify the green "Successfully posted" banner before opening the next composer. Full Publer runbook (account search tokens, droparea[5] upload, Reel tab, cross-contamination recovery) is in the `vp-content-batch` skill and the studio notes — follow it exactly. (The Publer API client at `Refine Social Media/publer_client.py` may be used instead of the UI for image posts — schedule_post with image_urls — when public image URLs are available.)

## HARD GUARDRAILS
- NEVER open instagram.com/* or facebook.com/* in Chrome against Valley Pawn accounts (triggered the 2026-07-04 IG flag). All Meta interaction goes through Publer. NEVER hit developers.facebook.com/apps/*.
- If a run needs Meta insight data only Graph API can provide, log the gap in the manifest and DM Joshua. Do NOT attempt browser fallback.
- MJ fast hours exhausted → pause + DM Joshua (never silently fall to relax mode).
- Bravo export missing/stale >24h → log staleness, DM Joshua.
- Empty caption after 2 regenerate retries → skip + DM Joshua.
- "Dixie Pawn" in generated copy → HARD STOP, skip the item + DM Joshua.
- No firearms/guns/weapons language on any social/GMP channel (especially Roanoke).
- Pillar cap breach at Step 2 → re-balance before generating heroes.
- Community posts: NO CTA, ever. Humor: never exceed 1/week; obey the boundaries block in humor.json.

## Timing
Fires Monday 2:02 AM ET via cron `0 2 * * 1`. Batch stages Slack cards; Joshua approves Monday morning from phone; Publer publishes on the assigned schedule across the week.

<!-- 2026-07-06 (evening, strategic build): added STEP 0.5 — PILLAR_OVERLAY.md (Community 15-20% + Humor ≤10% pillars) + weekly-adjustments.json adjust loop fed by vp-publer-analytics-friday. Community/Humor hook libraries live in Refine Social Media/hook-library/. -->
<!-- 2026-07-06: added STEP 0 folder-access prerequisite + persistent strategy-doc path after the 2026-07-06 run failed with no Projects mount. Pointed Deals source to #deal-of-the-week (C0AVCANK7E3). Flagged missing #vp-studio-queue. Corrected inventory filenames to items-to-price / aged-inventory-summary. -->
<!-- migrated to Publer-only publisher 2026-07-04 after Meta app disabled + brand IG flagged. Prior facebook-post Graph API flow retired. Deals-of-the-Week Step 3c-bis added 2026-07-04. -->
