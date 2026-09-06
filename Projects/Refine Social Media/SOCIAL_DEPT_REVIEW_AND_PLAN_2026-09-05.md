# Social Media Department — Full Review & Automation Plan
**Date:** 2026-09-05 · **Status:** PLAN — nothing built yet, awaiting Joshua's go
**Scope:** every social lane, script, scheduled task, skill, doc, Slack channel and Publer account for Valley Pawn
**Method:** enterprise-map load → 4 parallel deep audits (registry + all 25 task prompts; all code/docs/state in `Refine Social Media/` + `Valley Pawn Studios/`; all 12 social skills; live verification against Publer API + 6 Slack channels + Joshua's DM) → expert board → this plan.
**Rule 12 note:** every "broken/working" claim below was checked against Publer's live post list or the Slack channel itself, not run timestamps.

---

## 1. What the department is today (one page)

**Publishing layer:** Publer Business ($63/mo), workspace `6a358d48fe216c70f7e65d4e`, 15 connected accounts — 6 FB Pages (Brand + 5 stores), @valley_pawn IG, @thevalleypawn TikTok, @valleypawnva X, WordPress blog, 5 Google Business Profiles. All 15 connected, 0 failed posts, 0 drafts. Meta Graph API is dead (all Page tokens invalidated 8/21). Publer is the only working publish path.

**Human inputs (only two):** store managers post the Deal of the Week photo+price in `#deal-of-the-week` every Monday by noon (10/10 the last 4 weeks — this is the healthiest thing in the department), and managers are asked for a phone video Tue→Wed (4/5 submitted week of 9/1; zero the week before).

**Automation:** 25 Cowork scheduled tasks touch social (17 core lanes + 6 deal-of-week/Brevo + 2 adjacent). No native launchd agents for social. Monday alone has 16 fires between 8:10 AM and 7:35 PM.

**The weekly machine as it actually runs (verified in Publer 8/22–9/5):**

| Lane | Task | When | Output last 2 weeks | Verdict |
|---|---|---|---|---|
| Deal-of-week intake | prompt / reminder / pick / website-deals / Thu email watchdog | Mon 8:10–1:05, Thu 10:30 | 5/5 deals each week; Brevo W14 sent 9/3 | ✅ keep as the spine |
| A — Product batch | `vp-content-batch-weekly` (+preflight, postflight, quota watchdog) | Mon 1:40 PM | 7 items / 16 placements 8/31, all live | ⚠️ works, but hand-written Python every week |
| B1 — Deal reels | `vp-deal-reels-weekly` | Mon 2:30 PM | 13/13 videos live (5 store + IG + TikTok compilation) | ✅ healthy 3 weeks |
| B2 — Staff video | prompt / chase / `vp-casual-video-daily` | Tue 9 / Wed 11:15 / nightly 7:35 | inbox empty 61 days; processor never processed a real clip | ❌ dead lane |
| B3 — Comedy reels | `vp-comedy-reel-weekly` | Wed 6:30 PM | 10/10 targets live 9/3–9/5 | ✅ healthy |
| C — Community | `vp-community-weekly` | Mon 3:10 PM | 40/40 scheduled for 9/6–12 | ✅ healthy; nearly ran dry 8/31 (format cooldowns) |
| D — Engagement + reply sweep | `vp-engagement-weekly` | Mon 3:45 PM | 6/6 posts live, but the task "silently died" and the 9/1 "Guess the Price" reveal was never posted | ⚠️ broken promise to the audience |
| Deals-social Wednesday | `vp-deals-social-wednesday` | Wed 6 PM → Thu | found Lane A had already posted the same 5 deals; filled gaps; 2 byte-identical captions | ❌ duplicate of Lane A |
| Analytics | `vp-publer-analytics-friday`, `weekly-social-media-recap`, follower check | Fri 4 / Mon 9:40 / Mon 9:50 | Recap said 15 posts; Publer shows 88. Digest said 57; Publer 89. Every week = "hold current mix." Followers flat at 6,300 | ❌ numbers wrong by 5–6× |
| Creative drift / quarterly refresh | `creative_drift.py`, `vp-creative-refresh-quarterly` | select/record per lane; Oct 1 | 44 formats, product lane never wired | ⚠️ good engine, partly wired |
| Giveaway ($100/mo) | none | — | public "WIN $100 EVERY MONTH" pages live since June; **no drawing has ever happened** | ❌ liability |
| Reel comment alert | `reel-comment-alert` skill | 30 min after publish | Graph-API based → dead | ❌ dead |
| YouTube / store IGs | none | — | 0 videos, 13 subs; 3 store IG accounts exist but unconnected | — dormant |

**Volume:** ~75–90 placements/week across 15 accounts. Aug reach +65%, engagements +38%, video views up 34×, net followers **+3**.

---

## 2. Root causes (why it isn't frictionless)

1. **The core lanes are re-authored by hand every week.** Lane A, C and D have no reusable script — each Monday an LLM run writes a new `publish_batch_YYYY-MM-DD.py` / `_lane_c/build_manifest_<week>.py` / `engagement_lane/build_<date>.py` with hard-coded captions. 30+ one-off `_run_*.sh` / `_fix_*.py` / `_verify_*.py` files litter the folder. Every week is a fresh chance for a new bug.
2. **Seven different code paths write to Publer.** `PILLAR_OVERLAY.md` says everything must go through `vp_social_publisher.py` (the one with caption/duplicate gates). Lane A, deal reels, comedy, casual video and deals-social all bypass it and call `schedule_post()` directly. Result: blank captions still ship, byte-identical FB↔GBP captions (14 pairs in 2 weeks), and on 8/22 a `DELETE /posts` call wiped all 63 queued posts.
3. **No shared ledger of what was planned/posted.** Three lanes (batch, deal reels, deals-social) independently pick the same Deal-of-the-Week item, so Culpeper got the Mantis tiller 3 times in 3 days and Waynesboro the Gibson amp 3 times in 2 days. Tasks can't see each other's output except by re-querying Publer ad hoc.
4. **Every reader of Publer has its own (buggy) query.** `weekly_social_recap.py` calls `list_posts` with no date range (Publer silently returns a default window → 15 instead of 88). The digest undercounts the same way. `publish_batch_*.py` checks job status for `"completed"` while Publer returns `"complete"` → every batch logs 5 false timeouts. Fleet guardian then DMs Joshua "engagement posts haven't gone out" (they had) and "comedy task hasn't produced a single video, maybe ever" (it had).
5. **Failure noise reaches Joshua** despite Rule 16: 12+ "did not complete" / guardian DMs in 3 weeks, several of them false.
6. **Documentation is five generations deep and contradictory.** Index (7/7), fb-content-strategy (7/6), PILLAR_OVERLAY (7/13), BUSINESS_OS addenda (6/19), 8/22 rebuild plan, and the task prompts each describe a different system (20 vs 42 items/week; store-local to IG vs not; Harrisonburg page ID inverted in 3 skills vs the live routing). Task prompts still say "fires Mon 2:02 AM" (moved 8/22), postflight still expects the pre-8/4 routing.
7. **Installed skills point at dead infrastructure.** `facebook-post`, `reel-comment-alert`, `vp-asset-compose`, `vp-ad-engine` and `valley-pawn-context` all still instruct Graph API / `facebook-post` / Canva template IDs that are placeholders / a `vp-hero-video` skill that doesn't exist. A fresh session that trusts them will repeat the 7/4 mistake that got the Meta app disabled.
8. **Two lanes depend on things that don't exist:** `#casual-video` channel (asked of Preston 8/22, never created), Publer session file for preflight (never created; preflight hasn't produced a file since 8/24).

---

## 3. Expert board

🧑‍⚖️ **EXPERT BOARD — How to make Valley Pawn social publishing deterministic and hands-off**

**PANEL:** martech/automation engineer · SRE (reliability, idempotency) · brand-risk & platform-policy reviewer · pawn-shop operator (permanent seat)

**OPTIONS WEIGHED**
- **Option 1 — Patch in place** (fix the 6 known bugs, leave 25 tasks + 7 publish paths). For: fastest. Against: keeps the weekly hand-written-script pattern that generates the bugs; Rule 4 says we shouldn't edit hardened tasks anyway; no ledger means dupes continue.
- **Option 2 — Rebuild the whole department as one native Python app, retire all LLM tasks.** For: maximally deterministic. Against: throws away the creative work (captions, comedy scripts, community writing) that the LLM does well; big-bang cutover = highest risk; violates prove-before-deploy.
- **Option 3 — "One engine, one publisher, one ledger" (recommended).** Deterministic Python core owns *state, routing, de-duplication, publishing and every metric*; LLM tasks are narrowed to *creative only* and hand the engine JSON candidates. Built additively alongside, proven in parallel for 2 weeks, then the old tasks are disabled (kept as rollback per Rule 15).

**DECISION**
Option 3. The failures are all in the *plumbing* (state, dedupe, Publer I/O, counting), not in the *creative*. Move plumbing into code that runs the same way every week; leave the writing with the model but behind a validator. Native launchd owns anything that needs no judgment (ledger sync, metrics, formatters).

**REJECTED**
- Reviving Meta Graph API / `facebook-post` — dead tokens, app disabled 7/4, and re-attempting is what flagged the IG account. Publer stays the sole path.
- Canva-based composition (`vp-asset-compose`) — template IDs were never configured; the Pillow/ffmpeg renderers already in production are working. Mark the skill dormant.
- A Slack approval queue — Joshua decided 7/6 and again 8/4: no approval gate. Log cards only.
- Adding new channels (YouTube Shorts, store IGs) before the core is stable.

**FOR JOSHUA** — four decisions only (section 7). Everything else proceeds additively on your go.

---

## 4. Target architecture

```
                 ┌──────────────── HUMAN INPUT (unchanged) ────────────────┐
                 │ #deal-of-the-week (Mon ≤ noon)  ·  staff phone videos   │
                 └───────────────────────────┬─────────────────────────────┘
                                             ▼
  ┌──────────────────────── vp_social/  (ONE Python package, deterministic) ────────────────────────┐
  │ ledger.py   SQLite: every planned/scheduled/published post — item, lane, account, caption hash, │
  │             publer_post_id, status. Synced from Publer nightly (native launchd).                 │
  │ plan.py     Builds the week: brand slots, store slots, deal posts, reels, community, engagement │
  │             using deal_store.json + CITY_COMMUNITY_KB + creative_drift.  Enforces:               │
  │             • one deal item ≤ 1 photo post + 1 video per page per week                          │
  │             • no byte-identical caption across accounts   • no image reuse across stores        │
  │             • humor ≤ 1/wk fleet-wide   • community 15–20%  • firearms / Dixie / hours gates    │
  │ creative/   Narrow LLM contracts: captions(item, channel) → JSON; comedy_script() → JSON;        │
  │             community_post(store, format) → JSON.  Validated by qa_check_caption() before use.  │
  │ publish.py  THE ONLY writer to Publer (hardened vp_social_publisher + upload_media +             │
  │             correct job-status + retry + DELETE hard-blocked + idempotent by ledger key).        │
  │ reader.py   THE ONLY reader of Publer (always from/to; paginated). Feeds every report.           │
  │ report/     Deterministic formatters (Rule 18 pattern): weekly recap, Friday digest, quota,     │
  │             postflight, month-in-review, follower log. Empty stdout + exit 2 on any gap.         │
  └───────────────────────────────────────────────────────────────────────────────────────────────┘
                                             │
              ┌──────────────────────────────┼──────────────────────────────┐
              ▼                              ▼                              ▼
   Cowork tasks (creative + orchestration)   native launchd (no judgment)   Publer → 15 accounts
   vp-social-monday   (Sonnet)  Mon 1:30 PM  ledger-sync nightly 11 PM
   vp-social-midweek  (Opus)    Wed 6:00 PM  metrics + recap Mon 9:40 AM
   vp-social-friday   (Sonnet)  Fri 4:00 PM  quota / postflight Tue 10 AM
   vp-social-reply-sweep (Sonnet) Mon+Thu    giveaway draw last day 11:59 PM
```

**Scheduled-task count:** 17 core social tasks → **4** (plus 4 native agents). Deal-of-week/Brevo tasks untouched.

**What each Cowork task does after the rebuild**
- `vp-social-monday` — one run, staged with checkpoints (so a crash resumes, not restarts): preflight → plan week → captions via creative contract → deal reels render → community + engagement picks → `publish.py` → postflight from ledger → one log card to `#vp-studio-queue`. Replaces preflight, batch, deal-reels, community, engagement, postflight, deals-social-Wednesday (its Thursday deal posts become slots in the plan).
- `vp-social-midweek` — comedy reels (Opus for the writing) + staff-video processing if the inbox has files + the Guess-the-Price / poll reveal that was promised Monday.
- `vp-social-friday` — analytics narrative on top of the deterministic digest; writes `weekly-adjustments.json`; **records to creative_drift** (the loop is currently open — drift never reads adjustments).
- `vp-social-reply-sweep` — comment replies as the Page via Chrome Business Suite, twice weekly (replaces the dead Graph-API `reel-comment-alert`). Only lane that needs a browser.

---

## 5. Build plan (phased, additive, each phase proves before the next)

### Phase 0 — Stop the bleeding (Day 1–2, no architecture change)
- New `reader.py` with correct date-range queries; point a **new** recap/digest script at it (old scripts left in place, tasks repointed). Fixes the 5–6× undercount.
- Fix `"complete"` vs `"completed"` in a new publish helper; hard-block `DELETE /posts` in `publer_client.py` (additive guard, backup kept).
- Post the overdue **Guess-the-Price reveal** (audience was promised it 9/1). Public send → listed for Joshua in §7 only if he wants to see it first; otherwise goes with the plan.
- `vp-deals-social-wednesday`: add a ledger/Publer-queue check so it never re-posts an item Lane A already scheduled (until the planner replaces it).
- Rule 16 sweep: remove the stale "DM Joshua on failure" blocks from the 6 social task prompts that still carry them; guardian expected_outputs rows for the 8 uncovered social tasks so it stops raising false alarms.
- Correct the Harrisonburg page-ID contradiction (live routing `474248069342834` is right; 3 skills + strategy doc + open-items row are inverted).

### Phase 1 — Ledger + readers (Week 1)
- `vp_social/ledger.py` (SQLite, `Refine Social Media/state/social_ledger.sqlite`), backfilled from Publer for the last 90 days.
- Native launchd `com.valleypawn.social-ledger-sync` nightly.
- All six reports rebuilt as deterministic formatters reading the ledger (same pattern as `format_aged_inventory.py`): recap, digest, quota, postflight, follower log, month-in-review. Rule 18: withhold on any gap.
- `PUBLICATION_CALENDAR.md` + `fleet/expected_outputs.json` rows updated.

### Phase 2 — Planner + single publisher (Week 2)
- `plan.py` with the conflict rules above; `publish.py` as the only Publer writer; `creative/` contracts.
- Prove on the island: dry-run a full week's plan against last week's inputs; diff against what actually shipped; confirm 0 dupes, 0 blank captions, 0 identical captions, humor ≤1.
- Retire the weekly hand-written scripts (moved to `_archive/`).

### Phase 3 — Consolidated tasks (Week 3) — parallel run
- Register `vp-social-monday`, `-midweek`, `-friday`, `-reply-sweep` as NEW tasks in **dry-run mode** for one week (plans, logs, publishes nothing) while the old 17 keep running. Compare ledgers.
- Week 4: flip new tasks live, **disable** (not delete) the old 17 — they stay as rollback for 30 days per Rule 15.

### Phase 4 — Dead lanes (Week 3–4, in parallel)
- **Staff video:** stop depending on `#casual-video`; the Tuesday ask goes into a thread in `#deal-of-the-week` (already where managers respond), chase pulls attachments via the API path that deal photos already use, processor gets a real end-to-end proof on one of the 4 videos submitted 9/1.
- **Giveaway:** register `giveaway-monthly-draw` against the Brevo "Giveaway Entries" list (the script is a stub) — pending Joshua's call in §7.
- **Preflight:** folded into `vp-social-monday` stage 0 with only the checks that matter (Publer reachable, deal photos present, disk, ffmpeg); the Publer-session-file check that never worked is dropped.
- **Creative drift:** wire the product lane, add the file lock, enforce cross-store fan-out, and top up community/humor format depth so the lane doesn't run dry mid-November (it will at current cooldowns).

### Phase 5 — Docs & skills (Week 4)
- One canonical `SOCIAL_SYSTEM_SPEC.md` replaces the five drifted specs; `REFINE_SOCIAL_MEDIA_INDEX.md` rewritten; dead docs/scripts moved to `_archive/` (nothing deleted).
- Skill updates via `save_skill`: `valley-pawn-context` (Publer not `facebook-post`, correct Harrisonburg ID, remove "Later"), `vp-content-batch` → thin pointer to the spec, `facebook-post` + `reel-comment-alert` marked DEPRECATED at the top, `vp-asset-compose` marked dormant, `scheduled-task-models` policy rows for the 4 new tasks.
- BUSINESS_OS Domain-4 section + CHANGELOG + Open Items Register updated.

**Estimated calendar:** 4 weeks to fully cut over; Phase 0 wins land in the first 48 hours.

---

## 6. What this changes for Joshua and the team

- **Managers:** nothing changes — same Monday deal post, same video ask (now in one thread).
- **Joshua:** no weekly touch. One Monday log card and one Friday digest in Slack, both from the ledger, both correct. No failure DMs. Everything technical goes to `Valley Pawn Studios/STATUS.md`.
- **Cost:** Publer stays $63/mo. Scheduled-task model spend drops (17 tasks incl. 3 Opus → 4 tasks incl. 1 Opus).
- **Reliability:** every publish is idempotent by ledger key (a re-run can never double-post); every report is a deterministic script (a bad number can't be hand-rendered).

---

## 7. Decisions that are genuinely yours (everything else proceeds on your go)

1. **The $100/month giveaway.** Public pages have promised it since June and nobody has been drawn for July or August. Options: (a) draw July + August now from the Brevo entries list and automate going forward, or (b) end it and take the pages/rules down. Recommend (a) — the promise is already public.
2. **X (@valleypawnva).** 29 posts, ~1 reach each, 0 followers, connected under your personal name. Recommend dropping X from the brand routing tier and keeping the account parked. Say the word and it stays.
3. **Meta housekeeping that needs your login (one-time, ~20 min):** Business Verification for portfolio `221863965111592`, merge/unpublish the legacy Harrisonburg shell page, delete the 2021 "Need Money?" boosted post with hostile comments. None of it blocks the rebuild; it does affect page distribution.
4. **Go / no-go on the plan above.** On "go" I start Phase 0 immediately and run continuously; you'll hear from me only at each phase gate or if something needs a genuine business call.

---

## 8. Not touching (by design)
Deal-of-the-Week intake tasks and Brevo W-series · `vp_deal_reel.py` / `vp_deal_compilation.py` / `vp_comedy_reel.py` renderers · `creative_drift.py` + `CITY_COMMUNITY_KB.md` + `CALENDAR_AUG_DEC_2026.md` · `valley-pawn-blog-publisher` · the 8/22 audit findings and Q4 creative direction · brand identity in `vp-brand-studio` (palette, type, 6 styles, forbidden tropes, pillars).

---

## Appendix A — Evidence index (where each finding was verified)
- Publer: `GET /accounts`, `GET /posts?state=…&from=2026-08-08&to=2026-09-19` (267 posts, 0 failed)
- Slack: `#social-media` C0BMRC2LN3D, `#deal-of-the-week` C0AVCANK7E3, `#vp-studio-queue` C0BHTEUPADB, `#ai-marketing` C0BCEESUANM, `#blog-posts` C0APY6TE604, DM D03BHQH5VGT
- Files: `batch_2026-08-31.log`, `manifests/*_results.json`, `friday_digests/friday_digest_2026-09-04.md`, `follower_growth_log.csv`, `engagement_lane/RUN_LOG.md`, `Valley Pawn Studios/STATUS.md`, `casual-video-inbox/`, `creative_state.json`
- Registry: all 164 scheduled tasks + 25 social SKILL.md prompts; `launchctl list`
- Skills: 12 social-relevant skills read in full; contradictions quoted in the audit working notes

## Appendix B — Task disposition after cutover
| Today (17) | After |
|---|---|
| vp-content-batch-preflight / -weekly / -postflight / -quota-watchdog | → `vp-social-monday` + native quota/postflight |
| vp-deal-reels-weekly, vp-community-weekly, vp-engagement-weekly, vp-deals-social-wednesday | → `vp-social-monday` |
| vp-comedy-reel-weekly, vp-casual-video-daily, vp-staff-video-chase | → `vp-social-midweek` |
| vp-staff-video-prompt | kept (Haiku, one message) |
| vp-publer-analytics-friday, weekly-social-media-recap, vp-follower-growth-monthly-check | → `vp-social-friday` + native formatters |
| vp-creative-refresh-quarterly | kept, reads the ledger |
| weekly-social-media-content (disabled since April) | archived |
| (none) | + `vp-social-reply-sweep`, + `giveaway-monthly-draw`, + `com.valleypawn.social-ledger-sync` |
