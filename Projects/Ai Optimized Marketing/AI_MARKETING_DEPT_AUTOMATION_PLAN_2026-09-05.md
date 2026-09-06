# AI Marketing Department — Full Review + Umbrella Automation Plan
**Date:** 2026-09-05 · **Status:** PLAN ONLY — nothing built, changed, or sent · **Domain:** 1 (Valley Pawn)
**Goal:** one marketing system that is deterministic where it can be, judgment-only where it must be, watched everywhere, and never blocked on a human for anything a script can do.

### How this plan relates to the five lane plans written today
Five lane-level plans already exist as of today, all PLAN ONLY, all awaiting your go:

| Lane | Plan | Owns |
|---|---|---|
| Social | `Refine Social Media/SOCIAL_DEPT_REVIEW_AND_PLAN_2026-09-05.md` | `vp_social/` engine: ledger + planner + single publisher + single Publer reader; 17 tasks → 4 + 4 native |
| Email | `Email Refinement/19_EMAIL_DEPT_AUTOMATION_PLAN_2026-09-05.md` | Brevo: calendar runway, customer attributes, triggered flows, reach, measurement |
| Website analytics | `Website/WEBSITE_ANALYTICS_AUTOMATION_PLAN_2026-09-05.md` | GA4 Data API + Search Console data layer, shop refresh, website reports, WP client |
| eBay | `eBay/EBAY_DEPARTMENT_PLAN_2026-09-05.md` | listing quality, markdown engine, promoted listings, feedback, ratings |
| Comms | `Communcations/COMMS_DEPT_PLAN_2026-09-05.md` | bot identity, rendering engine, audience tiers, Slack surface |

**This plan is the umbrella.** It does not re-plan those lanes. It owns (1) the three lanes that have **no** plan — reputation/reviews, AI-search/GEO/presence/directories, blog — (2) the **cross-cutting layer** every lane plan assumes but none owns: shared clients, one data directory, one formatter contract, one open-items register, guardian coverage, Chrome isolation, the Monday master schedule; and (3) the **sequencing and the single consolidated decision list** so five plans don't hit you with 20 overlapping asks.

---

## 1. What the department is today (verified against channel output, not run records)

**Scale:** 56 enabled marketing scheduled tasks (of 148 fleet-wide) + 5 disabled legacy. ~28 marketing firings every Monday. 6 opus / 43 sonnet / 5 haiku / 2 unpinned. Zero of the 56 touch Parallels/Bravo screen; **26 of 56 depend on a live, logged-in Chrome session.**

| Lane | Tasks | Cadence | Verified health (8/31–9/5) | Plan |
|---|---|---|---|---|
| **Social / content** | 17 | Mon chain 8 AM–4:40 PM; Wed video; Fri analytics | Recap 7–16 posts/wk vs 55+ target (undercounted 5–6× per the social plan). Community + deal reels + comedy healthy. Engagement lane died silently 8/31. Staff/casual video 0 output 61 days. Followers 6.3K, +3 in August. | Social plan |
| **Email** | 12 | Mon chain → Thu 10 AM; daily 7 AM preflight; Fri analytics | **Healthy.** W13 11.6/1k, W14 28.25/1k calls+texts (target ≥8). Gold&Silver 9/1: 11,000 delivered. Weekly audience is 177 of 13,966 contacts. | Email plan |
| **Reputation** (Chekkit / Google) | 5 | hourly / nightly / Tue / Mon | Posting. 1,561 reviews, 4.88 avg, ~21/wk. All 4 heavy tasks drive the Chekkit **browser UI**; no API client exists. Roanoke 454 behind The PawnShop, carried unverified 2 weeks. | **This plan** |
| **AI-search / GEO / presence** | 6 | Mon / Fri / Sun | On cadence. **Visibility Index 83%** (63% late July) — target hit. Schema, llms.txt, NAP clean every week. **Every on-site number is flat; the only moving number is `open_needs_joshua`: 8 → 9 → 10.** | **This plan** |
| **Blog** | 3 | Mon/Thu 1:30 AM | On cadence (7 in Aug). Zero social engagement on 24 shares. 5th near-duplicate emergency-fund post; CTA template ships wrong hours. | **This plan** |
| **Website** | 8 | daily/weekly | See website plan. | Website plan |
| **eBay-adjacent** | 8 | Sun/Mon/Thu/1st | See eBay plan. | eBay plan |
| **Roll-ups** | 3 — CEO briefing (Mon 11:30), EOM recap (1st), publer-analytics-friday | | Briefing reads 8 lane posts, 2 of which haven't fired at 11:30. Recap re-reads Slack prose. 18-item action register, 11 owned by Joshua, most 2+ weeks old. | **This plan** |

**Human inputs the machine depends on:** managers' Deal-of-the-Week photo+price by **Mon 12 PM** (10/10 last 4 weeks — healthiest thing in the department; feeds email, Lane A, deal reels, website deals); staff video by **Wed 2 PM**; Joshua: ~10 one-time logins/decisions (§4).

---

## 2. What's actually wrong across the department (verified)

**A. Chrome is the single point of failure — 26 of 56 tasks.** Chekkit UI ×4 (~2 hrs/night clicking; a cell returned 0 rows silently for ~2 months once); GA4 UI ×3; Publer UI fallbacks ×6 (pixel coordinates in prompts) while `publer_client.py` does it headlessly; WordPress via Chrome nonce ×5 while an App Password already exists and 3 tasks use it; eBay public pages ×2 while `GetFeedback` is already in use. Legitimately browser-only: AI-engine prompt tests and Facebook comment reading (Page tokens dead 8/21). Nothing isolates these from each other or from the Bravo pipeline except `shop-in-store-sync`.

**B. Same data pulled 3–15× with no shared client.** Brevo: 12 tasks, one uses `_shared/brevo_helper.py`. Publer: 15 tasks, analytics pulled by 6, each re-learning the 15-result cap. Chekkit leaderboard scraped twice on Monday 7½ hrs apart. `#deal-of-the-week` parsed by **10** tasks with ≥3 definitions of "qualifying." Canonical NAP copied into 5 task files (one with wrong hours). eBay listings pulled by 4 tasks in the same window.

**C. 17 of 56 have no safety net; several are silent-on-failure.** casual-video-daily (empty folder 47+ days undetected), publer-analytics-friday (feeds Monday), the 4 creative lanes, 4 Brevo maintenance tasks, both roll-ups, creative-refresh-quarterly (a miss degrades 13 weeks), `ebay-feedback-reply-weekly` (permanent public replies, **no model pinned**).

**D. Model-rendered posts used as machine interfaces.** 3 of 56 post deterministic bytes. `vp-ai-search-autofix` / `vp-ai-visibility-autofix` **parse the previous task's free-text Slack bullets** to decide what to change on live listings. CEO briefing's inputs are 8 model-written posts. Same root cause as the 8/31 aged-inventory failure, already fixed there with `format_aged_inventory.py` (exact bytes on stdout; exit 2 = withhold).

**E. Marketing open items live in five unreconciled places.** Presence scorecard `needs_joshua` (10), CEO briefing `actions.json` (17), `Website/AUDIT_2026-08-22/weekly-history.json`, `engagement_lane/RUN_LOG.md`, `Life OS/OPEN_ITEMS_REGISTER.md`. They contradict each other: `SPF-MERGE` open in actions.json but fixed 8/24 per `EFFICIENCY_LOG.md`; presence audit says the noindex regression "self-corrected" — the website audit fixed it. Nobody can tell which of the 10 logins are still real. Now five new lane plans add their own decision lists on top.

**F. Stale facts baked into prompts and reference docs.** Blog CTA "Mon–Sat 10–6"; "~11,159 subscribers" hard-coded; follower baselines frozen 8/6; "154 items hit final cut on 2026-09-01"; a 2026-08-10 catch-up list baked into content-batch; `#email-campiagns` misspelling propagated into the CEO briefing lane table; repo `llms.txt`/`faq-page.md` say "$25,000" while live says "$100,000" (unconfirmed either way — regenerating from source would silently revert the site); `README-publish-checklist.md` unchecked for things live since 6/19; `STATUS-what-went-live.md` carries a ✅ line it retracts 44 lines later; `VP_30_DAY_CONTENT_CALENDAR.md` / `REFINE_SOCIAL_MEDIA_INDEX.md` describe a Sunday 8 PM batch and a Joshua approval step that no longer exist. The 8/3 GEO plan wrote the rule these files break: *"contradiction beats omission — old blocks get deleted, not layered."*

**G. Two auditors crawl the same site** from different sitemaps (103 vs 111 URLs), one report-only and one auto-fixing, each drawing its own conclusion about the other's work.

**H. Reputation lane is thin where it matters.** Review replies only to 4–5★; the two unanswered Culpeper 1-stars (Aug 9, Aug 21, "gold lowballing") sit while the calendar amplifies gold content on that page. Roanoke review gap routed to "existing Chekkit flow" every week with no measurable lift. No `aggregateRating` schema despite 1,561 reviews.

**I. GEO/presence upside is 100% behind logins.** Everything the machine can do autonomously is done and flat. Apple Business Connect (no Valley Pawn listing; Apple Maps may show Dixie Pawn), Bing Places (Dixie storefront lead photo), MapQuest "Dixie Pawn Inc." (owner-verified, cited in Google organic, 8+ weeks), Yext feed at source, GBP "Ste 22", BBB Waynesboro wrong phone, YellowPages rename. Oldest cross the 30-day line **2026-09-21**.

**J. Blog produces cannibalization, not reach.** 2×/wk on a 5-pillar rotation with no topic ledger → 27 duplicate pages, growing 1–2/wk. 24 social shares, 0 engagement. Location pages ~198 words vs competitors 800–1,500; Harrisonburg gold page gap open 5+ weeks. The blog is the one content lane with no measurement loop at all.

---

## 3. Expert Review Board

🧑‍⚖️ **EXPERT BOARD — how to make the marketing department robust without five plans building five copies of the same plumbing**

**PANEL:** martech platform engineer · SRE / reliability lead · deliverability + brand-risk reviewer · local-SEO/GEO strategist

**OPTIONS WEIGHED**
- **Option 1 — Let each lane plan build its own clients/registers/formatters.** For: each plan ships independently. Against: five Brevo helpers become five new Brevo helpers; five decision lists; the 8/3 drift protocol violated at scale.
- **Option 2 — One monolithic marketing orchestrator.** For: one place to look. Against: non-additive (Rule 4), single point of failure at 2 AM, unprovable in a week.
- **Option 3 — Umbrella owns the shared layer; lane plans own lane logic on top (recommended).** For: the pattern that fixed monthly analytics and aged-inventory on 9/5; each client fixed once; every numeric post verifiable; one register; lanes stay independently deployable. Against: the shared layer must ship first (week 1), so lane plans' Phase 1s wait ~5 days.
- **Chekkit API vs keep browser.** Chekkit publishes an API. Build `chekkit_client.py`, prove read paths against current browser numbers, then campaigns. If the plan tier lacks API access → a $ decision for Joshua, not a reason to keep clicking.
- **Two site auditors.** Keep `weekly-website-health-audit` as sole crawler/fixer (best-built task in the function). Presence-audit becomes off-site-only and reads on-site numbers from the health audit's history JSON.
- **Blog.** Keep the cadence, add a topic ledger + cannibalization gate (no publish if a live page already ranks for the target query) and a Search-Console feedback loop via the website plan's GSC pull. Board rejected pausing the blog — cadence is an asset; duplication is a gate problem.

**DECISION**
Option 3. Week 1 ships the shared layer (clients, `data/`, formatter contract, one register, guardian entries, Chrome lock). Lane plans then execute their phases on top. Everything cloned (`-v2`), proven one full cycle on live output, then the old path is disabled — never deleted.

**REJECTED**
- Per-lane plumbing (Option 1) — reproduces the duplication that causes the drift.
- Monolith (Option 2) — non-additive, single point of failure.
- Rebuilding a Meta Graph path — Publer is the publishing layer (Rule 11). Facebook comment reading tries Publer's comments endpoint first; Chrome only as an isolated fallback.
- Pausing the blog — gate it, don't stop it.

**FOR JOSHUA** — consolidated decisions + one login list (§4). Everything else proceeds additively on your go.

---

## 4. The ONE consolidated list — every decision and login across all six marketing plans

Five lane plans plus this one produced ~24 asks. Deduplicated, they are **8 decisions and 7 logins**. Nothing in Phase 1–3 of any plan waits on them.

**Decisions (business, not technical):**
1. **Go / no-go on the umbrella sequencing** (this plan §6). On go, week 1 starts the shared layer; lane plans follow.
2. **Chekkit API access** — approve a tier change if the current plan doesn't expose it (I'll price it first). Retires 4 browser tasks.
3. **Max loan amount** — $100,000 / $25,000 / $10,000? Live since 8/23, unconfirmed. Blocks llms.txt, FAQ, schema, and the website plan.
4. **$100/month giveaway** — draw July + August now and automate (recommended), or end it and take the pages down. *(Social plan §7.1)*
5. **X (@valleypawnva)** — drop from brand routing tier (recommended) or keep. *(Social plan §7.2)*
6. **eBay Promoted Listings** — 2% ad rate at 4 stores on ≥$100 listings, ~$100–150/mo. *(eBay plan §7.1)* — plus Top Rated Plus ops policy, Culpeper $50 intake floor, pull destination. *(eBay plan §7.2–7.4)*
7. **Paid social** — yes / no / not now. If yes: Meta Pixel + $/day cap + first real vp-ad-engine run on the proven winners (hiring-style posts, Store Spotlight). If not now, the never-run ad skill stops appearing as a gap.
8. **Comms identity** — bot sender name; managers get a Monday own-store brief yes/no. *(Comms plan §6)*

**One-time logins (~30 min total; every one has been open 6–12 weeks):**
- **Google** service account grant (GA4 Viewer + Search Console user) — *unlocks the entire website data layer* (website plan Phase 0)
- **Bing Places** — Harrisonburg lead photo is the Dixie storefront sign; watcher self-disables once you're in
- **Apple Business Connect** — claim Harrisonburg; Apple Maps may still show Dixie Pawn
- **MapQuest** business console — remove "Dixie Pawn Inc." (ID 410128854) + cancel the Yext feed at source
- **Google Business Profile** console (different Google account) — drop Harrisonburg "Ste 22"
- **Meta Business Suite** — Business Verification, delete the 2021 "Need Money?" boosted ad, unpublish legacy Harrisonburg shell *(social plan §7.3)*
- **eBay** — re-consent 5 store tokens with `sell.analytics.readonly` (ratings sweep for all 5 stores)
- Plus one click: **register `monthly-publication-audit`** (classifier-blocked 3×)

Each arrives as a 3-line click path when you want it. The login list will be tracked as rows in the single register (§5) with an age counter, so it stops being re-asked in five different posts.

---

## 5. Target architecture — the shared layer (additive; nothing hardened is modified)

```
                SOURCES (all headless)                            SHARED CLIENTS  (Scheduled/_shared/)
  Brevo API ──────────────────────────────┐                        brevo_helper.py    exists → adopted by all 12 (email plan)
  Publer API ─────────────────────────────┤                        publer_client.py   exists → single reader (social plan)
  Chekkit API ────────────────────────────┤ ──► NEW chekkit_client.py                 (this plan)
  eBay Trading + REST ────────────────────┤                        ebay_client.py     listing snapshot, 1 pull/4 consumers (eBay plan)
  WordPress REST (App Password) ──────────┤                        wp_client.py       replaces every Chrome nonce path (website plan)
  GA4 / GSC ──────────────────────────────┤                        ga4_pull / gsc_pull (website plan)
  Slack #deal-of-the-week ────────────────┘ ──► deal_submissions.py  ONE parser, ONE "qualifying" rule (social plan's reader; all 10 consumers)
                                                        │
                                                        ▼
    Projects/Ai Optimized Marketing/data/{social,email,reputation,presence,deals,blog}/YYYY-MM-DD.json
                     single source of truth · native pulls on launchd · idempotent · resumable
                                                        │
    ┌──────────────┬──────────────┬──────────────┬──────┴───────┬────────────────────┬──────────────────┐
 format_reviews_ format_presence_ format_visib_  format_blog_   MARKETING_OPEN_      CEO briefing + EOM
 weekly.py       audit.py         scorecard.py   weekly.py      ITEMS.json + open_   recap read DATA +
 (exact bytes)   (exact bytes)    (exact bytes)  (exact bytes)  items.py (ONE reg.)  register, not Slack
                                                        │
        Cowork task = launcher + verifier + poster (sonnet/haiku).  Rule 18: formatter exit 2 → post nothing.
        Judgment stays on Claude: reply wording, community facts, AI-engine tests, autofix decisions, blog copy.
        Rendering plugs into the Comms engine when it ships; until then formatters post directly.
```

**Contracts every lane plan builds against:**
1. **One pull per source per cadence**, cached under `data/`; consumers read cache, never re-pull.
2. **Formatter contract** = `format_aged_inventory.py`: exact Slack body on stdout, exit 0; on any validation failure print nothing, exit 2. Numeric posts come from formatters; narrative posts stay model-written but read `data/`, not Slack.
3. **One register** — `MARKETING_OPEN_ITEMS.json` with `open_items.py add|resolve|age|dedupe`. The presence scorecard `needs_joshua`, `actions.json`, `weekly-history.json`, and every lane plan's decision list become views of it. One summary row/week to `Life OS/OPEN_ITEMS_REGISTER.md`.
4. **Store facts from one file** (`canonical_nap.json`); no task carries its own copy.
5. **Every producer in `fleet/expected_outputs.json`**; every silent-on-failure task gets a marker or a watchdog. Failure detail → status file + one plain DM (Rule 16).
6. **Chrome lock** — `_run_locks/chrome.lock` shared with the Bravo pipeline; the two legitimately-browser tasks (AI-engine tests, FB comments) take it, everything else must be headless to pass review.
7. **Every task pinned**; opus only where the file justifies it.

---

## 6. Sequencing (the umbrella's job) — each phase proven one full cycle before anything is disabled

### Week 1 — Shared layer + safety net (this plan) — *removes the silent-death class fleet-wide*
- `chekkit_client.py` (reviews, leaderboard, contacts, campaigns), proven read-only against current browser numbers.
- `data/` directory + `open_items.py` + `MARKETING_OPEN_ITEMS.json`; one-time migration of the 5 lists; contradictions resolved (SPF, noindex, Roanoke suite, Ste 22); every §4 login as a row with an age counter.
- `fleet/expected_outputs.json` +17 entries (all §2C tasks). `vp-casual-video-daily` stops running silently against an empty inbox (weekly one-line DM instead).
- Pins: `ebay-feedback-reply-weekly` → sonnet; `monthly-eom-recap` → sonnet; `nightly-chekkit-review-responses` opus → sonnet.
- Stale-fact sweep (§2F) via `-v2` clones; repo `llms.txt`/FAQ regenerated from live + `canonical_nap.json`; `README-publish-checklist.md` and `STATUS-what-went-live.md` collapsed into one current `GEO_STATUS.md` (old files archived, not layered).
- Chrome lock scaffolded; `shop-in-store-sync`'s contention rule generalized.
- **Gate:** every new client reproduces the current channel numbers for one cycle; guardian shows 0 uncovered marketing producers.

### Weeks 1–2 in parallel — lane plans' Phase 0/1 (their docs)
Social Phase 0 (stop the bleeding) + Phase 1 (ledger + readers, incl. `deal_submissions.py`); Email Phase 0 (hygiene) + Phase 1 (calendar runway — drafts run out W15 = Sep 10); Website Phase 0/1 once the Google grant lands; eBay Phase 1; Comms Phase 1 (identity + rendering). The umbrella only checks each builds on the shared clients, not its own.

### Week 2 — Deterministic formatters + roll-ups (this plan)
- `format_reviews_weekly.py`, `format_presence_audit.py`, `format_visibility_scorecard.py`, `format_blog_weekly.py`.
- `vp-ai-search-autofix` / `vp-ai-visibility-autofix` read the health check's **JSON**, not its Slack post.
- CEO briefing and EOM recap read `data/` + the register; briefing verifies all 8 lanes exist before composing and moves to **Mon 1:15 PM** (after the pick and draft guard).
- **Gate:** replay last 4 weeks through each formatter; matches or improves on live posts; zero malformed posts.

### Week 3 — Chrome retirement + Monday master schedule (this plan, with lane plans' Phase 2/3)
- Reputation: 4 Chekkit tasks → `-v2` on the API client; post-watchdog becomes a marker check; **1–2★ reviews get a drafted reply to Joshua's DM within 24 h** (customer-facing → his send). Browser path disabled after one clean Tue + Mon.
- Presence audit → off-site only; on-site metrics from the health-audit history JSON; one sitemap.
- `directory-listing-monitor` becomes a real weekly task on the shared client (Google/Bing/Apple/FB/Yelp NAP vs `canonical_nap.json`) writing per-listing rows to the register — the "9 legacy listings" count gets owners and ages.
- Monday rebuilt: native pulls 1–4 AM; the two browser-only jobs in one locked window; everything after 8 AM reads cache; Chekkit 2 scrapes → 0; GA4 4 → 1 (website plan).
- **Gate:** a Monday with zero Chrome contention and every marker present by its time.

### Week 4 — Blog loop + reputation growth (this plan)
- Blog: topic ledger + cannibalization gate (query the GSC pull for an existing ranking page before publishing; if one exists, update it instead — additive to the existing post); CTA block from `canonical_nap.json`; weekly `format_blog_weekly.py` post (published / clicks / impressions per post from GSC) so the lane finally has a measurement loop. Duplicate-cluster 301 map presented for your approval (the one irreversible step).
- Reputation: `aggregateRating` schema from the live review count (verified weekly); Roanoke review-gap program with a measurable weekly lift target instead of "routed to existing flow"; Harrisonburg gold landing page brief handed to the website content lane.
- Wikidata enrichment (spec from 6/19) once someone logs in.
- **Gate:** 2 weeks with no new duplicate-topic post; reviews/wk trend visible per store.

### Month 2 — Growth (lane plans' Phases 4–5, on your go)
Email reach (177 → per-store segments on the proven Store Spotlight format), triggered flows, giveaway draw automation, win-back, eBay promoted listings, paid social pilot if decision 7 = yes.

---

## 7. What this does NOT touch
Bravo pipeline and Monday combined Bravo run; any existing saved report; any hardened task file (clones only; originals disabled after proving, never deleted); Publer as the publishing layer; Brevo Templates 11 and 72; the Thursday 10 AM send; the FIELD_COMMUNICATION_STANDARD; Rules 16/18. No customer-facing send changes without your word.

## 8. Expected result (department-wide, after week 4)
- Chrome-dependent marketing tasks: **26 → 2**, both locked and isolated.
- Pulls per source per week: Brevo 12 → 1 client, Publer analytics 6 → 1, Chekkit scrapes 2 → 0 browser, eBay listing pulls 4 → 1, deal-of-week parsers 10 → 1, GA4 4 → 1.
- Tasks with no safety net: **17 → 0.** Silent-on-failure: 0.
- Numeric channel posts from formatters: 3 → all (~14 marketing publications).
- Open-items lists: 5 (+5 plan decision lists) → **1**, with owner and age; "needs Joshua" shrinks to what is actually his.
- Reputation: 1–2★ reviews answered within 24 h (your send); reviews/wk per store measured, Roanoke gap on a trend line.
- Blog: duplicate cluster stops growing; every post gets a GSC number.
- Cost: opus nightly loop retired; 2 unpinned tasks pinned; Publer unchanged; Chekkit API tier TBD.

---
*Inputs: 56 SKILL.md files (raw audit: `_task_audit_raw_2026-09-05.md`, this folder), `PUBLICATION_CALENDAR.md`, `presence_scorecard_latest.json`, `PRESENCE_HISTORY.csv`, `ceo-briefing/actions.json`, `CREATIVE_LEDGER.md`, `EFFICIENCY_LOG.md`, `Valley Pawn Studios/STATUS.md`, the five lane plans dated 2026-09-05, and live reads of #ai-marketing, #social-media, #email-campiagns, #blog-posts on 2026-09-05.*
