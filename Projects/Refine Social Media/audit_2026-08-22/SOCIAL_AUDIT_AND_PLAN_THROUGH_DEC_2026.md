# Valley Pawn — Social Media Audit & Content Plan Through December
**Date:** 2026-08-22 · **Domain:** 1 (Full Circle Finance Inc DBA Valley Pawn)
**Status:** CONTEXT LOADED — audit complete, plan proposed, NOTHING BUILT YET (per Joshua's "report back before touching anything")

---

## 📍 CONTEXT BRIEF

**RECENT CHANGES THAT MATTER**
- 2026-08-21: store-local social gap "recovered" — 10 posts manually published via a one-off script; quota watchdog rewritten to osascript-only; a proven store-photo retrieval path added to `vp-content-batch-weekly`. **Unproven until Monday 8/24.**
- 2026-08-21: `vp-deal-of-week-monday-pick` found to have died silently 3 straight Mondays (8/3, 8/10, 8/17); 107 of 129 tasks patched with resume-discipline blocks.
- 2026-08-21: **Facebook Page tokens are dead** — every store Page token invalidated when the FB password changed. Direct Graph API path (the `facebook-post` skill, page scans, comment tooling) is down. Publer publishing still works.
- 2026-08-21: AEO/GEO audit delivered separately (Visibility Index 71%); owns directories/schema/NAP — **do not touch**.

**WHAT EXISTS NOW**
- 10 social/content scheduled tasks + 4 deal-of-week + 4 email + 6 review + 9 website + 4 AI-search + 4 eBay = **44 marketing tasks, 41 enabled**.
- `PILLAR_OVERLAY.md` is already the authoritative content strategy (pillars, quotas, 4 authenticity gates, adjust loop). **The strategy is not missing. It has never once executed at spec.**
- Publer is the publishing route for 15 connected accounts. Layer: Cowork scheduled tasks (not launchd).

**VERIFIED AGAINST OUTPUT (Rule 12)**
- Live Publer API pull of all **554 published posts, 2026-05-24 → 2026-08-22**. Raw JSON + summary saved to `audit_2026-08-22/`.
- Slack: 14 days of `#social-media`, `#vp-studio-queue`, `#deal-of-the-week`, `#ai-marketing`, `#website`, `#email-campiagns`, `#google-reviews`, `#chekkit-updates`, `#in-store-inventory`.
- Filesystem: casual-video-inbox, deal photo uploads, fonts, brand assets, ffmpeg availability.

**RISK / WHAT A NARROW FIX WOULD MISS**
- Fixing "post more video" without fixing the monolith just moves which pillar gets dropped.
- The Friday→Monday auto-adjust loop will overwrite any new mix rule that doesn't route through `weekly-adjustments.json`.

---

# PART 1 — THE AUDIT

## The headline numbers (90 days, live Publer data)

| Metric | Claimed / Target | **Actual** |
|---|---|---|
| Platform posts per week | 91 | **42.6** (and only **17.1** actually published *by* the automation) |
| Store-local items per week | 35 | **0** for 3 straight weeks (8/3, 8/10, 8/17) |
| Reels / video per week | 4 (~52 in 90 days) | **2 pipeline videos in 90 days. Zero in the last 49 days.** |
| Posts that are static images | — | **77.6%** (430 of 554) |
| Posts with NO caption at all | 0 ("Ever. No exceptions.") | **252 of 554 — 45%** |
| Captions reused verbatim | 0 | **229 of 302 captioned posts — 76%** |
| Median engagement, per account | — | **0.0 on 8 of 9 measurable accounts** |
| Best post in 90 days | — | **9 total interactions** |
| Total comments across 485 measured posts | — | **18** (3.7% of posts) — and **0 replies from us, ever** |
| TikTok posts | — | **0.** Connected, never used. |

**Joshua's read was correct on all three counts:** no community content shipping, no video, nothing interesting.

## What's actually broken — five root causes

### 1. Everything is one Monday-2 AM monolith, and the good pillars are always first to be dropped
`vp-content-batch-weekly` produces brand posts, 35 store-local posts, community, humor, and reels in a **single run**. When any dependency degrades, the run sheds load from the tail — which is exactly where Community, Humor, and Reels sit. Verbatim from `#vp-studio-queue`, 2026-08-10:

> "Community + Humor pillars — not attempted this run given the image-pipeline gap."

And 2026-08-17:

> "**Store-local (35-item target): 0 this run.**"

The pillars Joshua asked for on 7/6 are structurally the first casualties every single week.

### 2. Video depends on a human dropping a file into a folder that has been empty since July 6
`vp-casual-video-daily` fires every night at 7:44 PM and processes `Valley Pawn Studios/casual-video-inbox/`. That folder contains a README, an end-card PNG, and a failed.log — **and has received zero video files since 2026-07-06**. There is no prompt, no deadline, no chase, no owner.

Contrast: `#deal-of-the-week` has a Monday 8 AM prompt, an 11 AM reminder that names non-submitters, and a 12:30 PM pick. Result — **10 of 10 submissions two weeks running, and week two needed no chase at all.** The mechanic that works is sitting right next to the one that doesn't.

### 3. No machine-generated video path exists — despite every ingredient being on the Mac already
`ffmpeg 8.1.2` is installed. Brand fonts (Inter, Playfair Display), logo assets, and a 1080×1920 end card all exist. Five real, high-quality product photos with real prices arrive from managers **every single Monday, reliably**. Nothing turns any of that into video.

### 4. Community content — the top organic performer — is coupled to a product image pipeline it doesn't need
The best-performing posts in 90 days, in order: hiring posts, the $100 giveaway, **Skyline Drive (community)**, **Walker Street / VMI (community)**, **named employees ("Sandi Cole and Bree run the counter…")**, then real product at a real price. Community posts need no product photo — yet they're generated inside the run that dies when product photos fail.

### 5. Nothing ever asks anyone anything
18 comments in 90 days, and Publer's stored-reply array is empty across all 554 posts — **nobody has ever replied to a customer comment.** Not one post in the sample asks a question, runs a poll, or invites a response. There is no community because nothing is built to create one.

## Secondary findings worth fixing

- **The Monday batch runs a week stale.** It fires at 2:02 AM Monday; manager deal submissions land 9:30–11:00 AM Monday. The 8/17 batch was working from the *Aug 10* deals, and the 8/10 batch claimed "Uriah didn't submit" — Uriah submitted at 11:17 AM that same day, nine hours after the batch had already run.
- **Preflight is blind to the exact thing that keeps failing.** `vp-content-batch-preflight` v3 runs 7 fix-first checks — Bravo freshness, Publer session, MJ hours, skill integrity, Slack, disk, text compositor. **None of them checks whether a product photo can actually reach Publer.** That is the failure that zeroed store-local content three weeks in a row.
- **Store coverage is wildly uneven:** Culpeper 111 posts / Roanoke 81 / Waynesboro 80 / Lexington 34 / **Harrisonburg 13**. Harrisonburg is publishing 1 post a week while Culpeper publishes 8.5.
- **Cross-platform posts are byte-identical** — the same text to Brand FB, IG, and X on the same minute; the same text to each store's FB and GBP. This violates `PILLAR_OVERLAY` §6 rule 5 and reads as spam to both algorithms and humans.
- **Same caption re-posted to the same page 3–4 times** ("A Martin D-28 doesn't just sit on a wall" ran 4× on Brand FB alone).
- **The Friday→Monday auto-adjust loop is optimizing on noise.** Its 8/21 output: "top content: warranty (36 reach), bottom: warranty (0 reach), adjustment: +5% warranty." It is tuning the mix on n=8 posts with single-digit engagement.
- **Two unanswered 1-star Culpeper reviews** in two weeks, both alleging gold lowballing — while the brand runs gold-buy content. Culpeper also got **0** new Google reviews the week the other four stores got 21 between them.
- **Organic social drives 7 sessions/week to the website — 2% of traffic, down 61% WoW.**
- **The email channel has been dark for 3 weeks** — and the proven winner was a *Store Spotlight* (250 calls+texts per 1,000 recipients) vs *Education* (0, twice).

---

# PART 2 — 🧑‍⚖️ EXPERT BOARD

**PANEL:** martech/automation engineer · short-form video producer (local retail) · brand-risk & community manager · SRE/reliability lead

### Options weighed

**Option 1 — Patch the monolith.** Fix the photo path, raise the video quota inside `vp-content-batch-weekly`, tell it to stop skipping Community.
*For:* smallest change, no new tasks. *Against:* the board rejected this unanimously. It has been patched every week since July and the same pillars die every week. A shared run means a shared failure mode; raising a quota inside a run that ships 0 changes nothing.

**Option 2 — Rebuild the content stack from scratch.** One new unified engine.
*For:* clean architecture. *Against:* violates additive-only (Rule #4); throws away a working Publer client, a working preflight ladder, a working deal-of-week intake, and a working analytics digest. Months of rebuild for infrastructure that mostly works.

**Option 3 — Decompose into independent lanes, each with its own inputs, failure mode, and watchdog. Add a machine-video engine that requires zero human input.** *(RECOMMENDED)*
*For:* Community and Video stop competing with product photos for survival — a photo-pipeline failure can no longer zero out video or community. Video becomes deterministic (ffmpeg over photos that provably arrive weekly) instead of hopeful. Every lane degrades to "ship less," never to "ship nothing." Fully additive: `vp-content-batch-weekly` keeps its product job, everything else moves out alongside it.
*Against:* more scheduled tasks to maintain — mitigated by registering every lane in Fleet Guardian's `expected_outputs.json` so silent failures auto-rerun rather than needing human maintenance.

### DECISION

**Split the content engine into five independent lanes and build a machine-video engine that runs on the deal photos we already receive every Monday.**

In plain English: right now one program has to do everything on Monday morning, and when any piece of it breaks, the interesting stuff — video, community, humor — is what gets thrown overboard. We split it into five small programs that can't sink each other, and we stop waiting for someone to hand us a video: we make videos automatically out of the product photos the managers already send in every week, on time, without fail.

### REJECTED
- **Patching the monolith** — tried weekly since July, same failure every week.
- **Full rebuild** — violates additive-only and discards working infrastructure.
- **Relying on staff-shot video alone** — the inbox has been empty for 47 days; hope is not a pipeline. Staff video stays, but as an *addition* to a machine floor, and with the proven deal-of-week prompt/chase mechanic attached.
- **Re-deriving content pillars** — `PILLAR_OVERLAY.md` already defines them correctly. The problem is execution, not strategy.
- **Using the Meta Graph API for anything** — all Page tokens are dead as of 8/21. Everything routes through Publer.

### FOR JOSHUA — the only genuine decisions that are yours
1. **Christmas Layaway launch date.** Recommend opening the campaign **September 15** (90-day drumbeat into December). This is a pricing/promotion call, not a technical one.
2. **Resume the weekly email cadence?** It's been dark 3 weeks. Data says Store Spotlight drives 250 calls+texts per 1,000; Education drives 0. Recommend resuming weekly with Store Spotlight, but the send cadence is your call.
3. **Do we want staff on camera?** The machine-video lane needs no one. The staff lane needs 2–3 short phone clips a week from managers. Your call whether to put that on them.

Everything else below proceeds additively without you.

---

# PART 3 — THE PLAN (Aug 22 → Dec 31)

## The five lanes

### LANE A — PRODUCT (existing, keep, 3 fixes)
`vp-content-batch-weekly` keeps exactly one job: brand posts + store-local product posts to FB/IG/X/GBP.
- **A1** Move the store-local leg from Mon 2:02 AM to **Mon 2:00 PM**, after manager deal submissions land. Kills the one-week-stale bug permanently.
- **A2** Add an **image-pipeline check** to `vp-content-batch-preflight` v3 — the blind spot that zeroed 3 weeks of store content. Fix-first ladder like the other 7 checks.
- **A3** Enforce per-platform caption variants (no byte-identical FB/IG/X or FB/GBP twins) and a hard no-empty-caption gate at publish time, not batch time.

### LANE B — VIDEO ENGINE (new — the big build)
Two independent sources. Neither can block the other.

**B1 · Deal Reels — machine-made, zero human input.** Every Monday afternoon, take the 5 manager deal photos (which arrive 10/10, reliably) and generate a 12–18 second vertical 1080×1920 Reel each: Ken Burns pan/zoom on the real product photo → price-reveal card (`$849.99 / retail $1,399`) → store + address card → brand end card, burned-in captions, royalty-free music bed. Built on ffmpeg 8.1.2 + Inter/Playfair + existing brand assets — all already on the Mac.
→ **5 store Reels + 1 brand compilation Reel per week.** Publishes to store FB Reels, Brand IG Reels, and **TikTok** (currently dark).
→ **This takes video from 0/week to 6/week using assets that provably already exist.**

**B2 · Staff phone video — the proven mechanic, cloned.** Clone the deal-of-week trio onto video:
- Tue 9:00 AM — prompt to `#casual-video` naming all 5 stores
- Wed 11:00 AM — reminder that names only the stores that haven't submitted
- Wed 3:00 PM — pick, process, schedule
Processor already exists (`casual_video_processor.py`). Add `faster-whisper` for auto-captions (not currently installed). Prompts are one-line and concrete: *"30 seconds — the weirdest thing that walked in this week."* / *"Show us the best deal on your counter right now."*
→ Target **2–3/week**, chased rather than hoped for.

**Combined target: 8–9 videos per week, of which 6 require nobody to do anything.**

### LANE C — COMMUNITY (new, fully independent)
3–4 posts/week, completely decoupled from product photos. Never a CTA, never a product mention — per the `PILLAR_OVERLAY` voice test: *"if a stranger would read it as 'a local business that loves its town,' it's right."*
Sources: Shenandoah NP + Skyline Drive seasons, JMU / VMI / W&L calendars, Friday night high-school football, farmers markets, county fairs, fall foliage, Blue Ridge Parkway, local festivals, Veterans Day. Routed store-local so each town sees its own town.
**This lane is the top organic performer and must never again be dropped as overflow.**

### LANE D — ENGAGEMENT (new)
The lane that actually creates community. 2 posts/week on rotation, text/image only — **zero image-pipeline dependency**:
- *Guess the Price* (real item, reveal in comments next day)
- *What Is This Thing?* (odd item that walked in)
- *This or That* (two items, pick one)
- *Best find you ever made* (open question)
- Poll: what should we stock more of
Plus a **comment-reply watcher** — pull comments and reply inside the hour. First-hour replies are the single biggest reach signal on Meta. (Routes via Publer/Chrome — Graph API tokens are dead.)
**Baseline to beat: 18 comments and 0 replies in 90 days.**

### LANE E — SEASONAL CALENDAR (new, locked Aug→Dec)

| Window | Campaign spine | Notes |
|---|---|---|
| **Aug 22 – Sep 1** | Back-to-school (laptops, tablets, monitors, dorm gear) + **Labor Day sale** | Cash-price angle; proven Memorial Day format |
| **Sep 1 – 14** | Fall projects & tools · generators & storm prep · hunting **pre-season** gear | No firearms on Meta/GBP — accessories, optics, safes, gear only |
| **Sep 15** | ⭐ **CHRISTMAS LAYAWAY OPENS** — 90-day drumbeat begins | *Free layaway* is the single strongest Q4 lever a pawn shop has. Weekly beat Sep→Dec. |
| **Oct** | Halloween · storm/generator season · fall foliage community · **year-end gold selling** (price + tax angle) | Culpeper gold-service repair required first — 2 open 1-star lowball reviews |
| **Nov 1 – 10** | **Veterans Day** (huge in Lexington/VMI + Shenandoah) — community-first, not a sale | Zero-CTA community post + a genuine thank-you |
| **Nov 24 – 30** | **BLACK FRIDAY + SMALL BUSINESS SATURDAY** — the biggest week of the year | Doorbusters per store, layaway payoff push, Reels-heavy |
| **Dec 1 – 20** | Last-minute gifts · jewelry & watches · **layaway pickup deadline** countdown · gift ideas under $50/$100/$250 | Daily Reels cadence through Dec 20 |
| **Dec 21 – 31** | Holiday hours · thank-you community post · **New Year gold-buy setup** (Jan is peak pawn season) | Sets up January |

## Hardening — the standing directive applied to every lane

Every new lane ships with all five, per `HARDENING_STANDARD.md` and Rule 15 (fix-forward):
1. **Fix-first ladder** — detect → remediate → re-verify → degrade → escalate. A DM without a preceding remediation attempt is a task failure.
2. **Registered in `fleet/expected_outputs.json` + `rerun_manifest.json`** — Fleet Guardian auto-detects and re-runs a silent failure. No new bespoke watchdogs.
3. **No human dependency without a prompt + a chase.** Any lane that needs a human gets the deal-of-week trio (prompt → named reminder → pick).
4. **Degraded mode ships less, never zero.** A lane that can't get a photo publishes text. A lane that can't get a video publishes a still.
5. **Model pinned** in frontmatter; staggered cron (Monday is already carrying 17 marketing tasks).

Plus two fleet-level fixes:
- **Add the image-pipeline check to preflight** (the blind spot).
- **Gate the Friday auto-adjust loop at n≥30 posts/account.** It is currently tuning the content mix on 8 posts and single-digit reach — that's noise, and it will fight any new mix rule.

## What success looks like by December 31

| Metric | Today | Target |
|---|---|---|
| Pipeline posts/week | 17 | 55+ |
| Videos/week | 0 | 8–9 |
| Community posts/week | 0 | 3–4 |
| Posts with no caption | 45% | 0% |
| Verbatim caption reuse | 76% | <10% |
| Comments received / replied | 18 / 0 per 90 days | 150+ / 100% replied |
| TikTok posts | 0 | 4+/week |
| Harrisonburg posts/week | 1.0 | 7 (parity) |
| Organic social → website sessions/week | 7 | 50+ |

---

## Sequencing (if approved)

**Week 1 (Aug 22–29)** — Lane B1 Deal Reel engine built and proven on the 5 photos already in hand · preflight image check · Lane A1 timing fix · Lane E calendar locked and dated.
**Week 2 (Aug 30–Sep 5)** — Lane C Community + Lane D Engagement lanes live · TikTok activated · Harrisonburg routing fixed.
**Week 3 (Sep 6–12)** — Lane B2 staff-video prompt/chase trio live · comment-reply watcher live · whisper captions installed.
**Sep 15** — Christmas Layaway campaign opens across all lanes.
**Ongoing** — every lane in Fleet Guardian; weekly proof against live Publer output, never against run records.

---

## Open decision handed back to Joshua
The three items in "FOR JOSHUA" above (layaway launch date, email cadence resumption, staff-on-camera). Everything else proceeds without you.
