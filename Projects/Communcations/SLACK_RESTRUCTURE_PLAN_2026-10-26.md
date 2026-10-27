# Slack Restructure Plan — "Landing pages, not scrolling channels"
**Date:** 2026-10-26 · **Domain:** 1 — Valley Pawn · **Project:** Communcations · **Status:** PLAN — awaiting Joshua's go (nothing changed in Slack)
**Supersedes/absorbs:** Internal_Comms_Restructure_Plan (8/24, ON HOLD — "too little info"), COMMS_DEPT_PLAN 9/5 Phases 1–3 (mostly built: ops bot identity, comms_engine, canvases) and Phase 5 (channel cleanup, never run).
**Method:** every one of the 95 channels was read live for Oct 12–26 (Rule 12). Counts below are from what was read, not from run records.

## 1. What the 14-day read shows
- 95 channels. 984 posts (~70/day). 521 automated (53%), 463 human.
- Human conversation lives in ~15 channels: #general, #product-availability, #returns, #end-of-day, #2pm-update, #deal-questions, #mobile-approvals, #facilities, #supply-request, #weeklygoals, #training, #deal-of-the-week, the 5 store funds channels, 3 of 5 roc-* channels, #preston-claude.
- ~30 channels are bot-to-nobody: automated posts only, 0 reactions, 0 replies in 14 days (store-performance, layaway-review, first-payment-default, employee-performance, ebay-performance, website, email-campiagns, ai-marketing, blog-posts, chekkit-*, sold-review, discount-review, pawn-walks, jewlery-counts, items-to-price, items-to-markdown, timekeeping-summary, weekly-returns-summary, registered-agent, voicemails-calls-missed, social-media, ffl-transfer-performance, daily-funds-reconcilation, vp-studio-queue, airbnb, basics).
- 39 channels had zero posts.
- Biggest scroll generators: #voicemails-calls-missed 125 (per-call pings + a 17:45 digest that repeats them all), #employee-prospects 56 (full interview grid re-posted on every booking; 19 posts on 10/13), #website 34 (28 "Shop refreshed" ticker posts), #google-reviews 41, daily walls of 1,800–3,800 chars in #pawn-walks / #sold-review / #discount-review / #jewlery-counts (49 posts, 1 reaction).
- Same subject, several reports: eBay = 4 weekly reports from 2 bots; layaway = 2 weekly reports from 2 senders; AI marketing = 3 weekly audits repeating the same 2 open decisions; #basics = 3 separate morning posts.
- "All clear" noise: 17 of 24 Chekkit posts, 11 of 11 registered-agent posts, Sat/Sun funds posts.
- Identity drift: the same report posts some weeks from Joshua's account ("Sent using Claude", sometimes doubled) and other weeks from the ops bot (Goldilocks).
- Side finding (not comms): PC-enrollment instructions were posted verbatim into all 5 funds channels 10/21–24 including a plaintext password; funds verification then misread them as cash sends and flagged all 5 stores on 10/21–22.

## 2. The answer to "is there a better plan?"
Yes. Chat is the wrong landing space for data that people want to *look at*; it is the right space for things that *happen*. So:
1. **Every report gets a landing page that is updated in place** — a Slack canvas pinned in the channel's bookmark bar (the 5 Monday canvases already work this way, bot-owned since 10/14) plus the existing password-gated dashboard site (vp-dashboard.pages.dev). The canvas never scrolls away; it always shows the current table with an "as of" stamp. History goes to Drive (already happens for most reports).
2. **The channel post shrinks to a headline** — ≤5 lines: the one number/takeaway, per-store lines only where something is off, and "Full table → canvas". No tables in the stream, no footers, one identity (ops bot).
3. **Channels consolidate by audience and department**, not by report. 40 report channels → 6.
4. **Monitors go silent when clean.** A channel post means something needs attention.
Nothing is lost: the full data density Joshua wants (8/24 verdict) moves to canvases + Drive instead of being cut.

## 3. Channel map (95 → ~45)

### A. Unchanged — human workflow channels (35)
#general (humans only, done 10/23) · #basics · #product-availability · #returns · #end-of-day · #2pm-update · #deal-questions · #mobile-approvals · #facilities · #supply-request · #weeklygoals · #training · #monday-meetings · #deal-of-the-week · #policy-announcements · #ask-goldilocks · #preston-claude · #monthly-gun-audit · #law-enforcement · #multiplesale · #records-of-warning · #airbnb (Domain 2) · the 5 funds channels · the 5 roc-* channels · compliance record channels left alone on purpose (#atf-traces, #gun-transfers, #ffl-copy, #business-license, #compliance — zero volume is not noise there).
Format-only fixes inside this group: #basics → one combined "Morning checks" post instead of three; #deal-of-the-week → 5 bot posts/week → 2 (open + features), reminders in-thread.

### B. Six report channels, each with a pinned canvas
| New/kept channel | Audience | Absorbs | Cadence in channel |
|---|---|---|---|
| **#store-performance** (keep) | all staff | #employee-performance, #ffl-transfer-performance | Mon: one 5-line scoreboard headline (rank, biggest mover, one focus item per store) + "Scoreboard" canvas. One recognition line per week. |
| **#loans-layaways** (rename #layaway-review) | managers + leadership | #first-payment-default, #loan-review (already retired) | Mon: one headline + "Loans & Layaways" canvas. Store-level detail keeps going by manager DM (exists). |
| **#aged-inventory-review** (keep) | managers | #items-to-markdown | Mon: one headline + canvas; managers' "Markdowns complete" replies stay. |
| **#marketing** (rename #social-media) | leadership | #website, #email-campiagns, #ai-marketing, #blog-posts, #ebay-performance, #ebay-rating, #vp-studio-queue, #chekkit-updates, #facebook-posts, #you-tube-tik-tok-content, #new-customers | ONE Monday digest (web, social, email, eBay, AI, reviews) + "Marketing" canvas; Fri email KPIs fold into Monday. Shop-refresh ticker → canvas only. eBay 4 reports → 1; AI 3 audits → 1. |
| **#leadership-reports** (rename #company-performance) | Joshua, Preston, Lainie | #scrap-rankings, #mobilepawn-participation, #timekeeping-summary, #weekly-returns-summary, #eom-task-rankings, #ceo-briefs, #call-insights, #sold-review, #discount-review, #pawn-walks | Daily walls (pawn walk / sold / discount) → "Daily Ops" canvas + one exception line in the existing 09:40 daily audit digest. Weekly/monthly reports → headline + canvas. |
| **#daily-checks** (rename #daily-funds-reconcilation) | Joshua, Preston | #jewlery-counts, #chekkit-messages-missed, #voicemails-calls-missed, #emails-missed, #registered-agent | Exceptions only. Funds mismatch, jewelry variance ≠ 0, unanswered texts, "still no callback" (one EOD line per store), new registered-agent documents. "All clear" is silent (ledger/canvas). |

### C. Kept as single-purpose, format fixed (4)
#items-to-price (daily, team; no weekend re-post) · #ebay-listings (daily store leaderboard, team; name the bot) · #google-reviews (celebration feed; keep) · #employee-prospects (one morning schedule post per day, booking changes EDIT that post instead of re-posting the grid).

### D. Archive with a pinned pointer (dead, no live publisher) (~19)
#schedule · #bravo-software · #ebay · #in-store-inventory · #in-store-checklists · #low-cost-high-risk · #valley-pawn-plus · #vp-ops-shadow · #amazon-returns · #supply-order-summary · #new-inventory · #employee-purchases · #emails-missed · #ebay-rating · #call-insights · #eom-task-rankings · #ffl-transfer-notifications · plus the channels emptied by section B after one clean parallel week.
Left for Joshua to say: #hr-documentation and #controllio-review (created 10/7, nothing posted — purpose unknown); #ask-handbook vs #ask-goldilocks (two Q&A bots — merge if Goldilocks covers the handbook); #bonus-goals (dead only because field posting is off by design — keep).

## 4. The concision standard (added to FIELD_COMMUNICATION_STANDARD as v4)
1. Headline ≤5 lines; the number first; per-store lines only for exceptions; last line "Full table → <canvas>".
2. One publication per subject per cadence. Duplicate reports merge or retire.
3. Monitors post only on exceptions; clean runs write the canvas/ledger.
4. Churny posts (interview grid, shop refresh) edit one message in place.
5. One sender for every automated post: the ops bot. Joshua's account posts only what Joshua writes.
6. Canvas carries the full table + "as of"; Drive carries history; the channel carries today.
All six rules are enforced in `bin/comms_engine.py` templates (one place), not re-stated in 60 task prompts.

## 5. Execution (on "go"; additive; each step has a backup + CHANGELOG line)
**Phase 0 — same-day fixes, no structural change:** merge eBay 4→1, AI 3→1, layaway 2→1; #basics 3→1; shop-refresh ticker off (canvas only); interview grid edit-in-place; Chekkit / funds / registered-agent / voicemail digest silent-when-clean; weekend dedupe for items-to-price; single identity (repoint the remaining Cowork posters to the bot or retire them). ~45% of automated volume gone with no channel moved.
**Phase 1 — canvases + headline templates (week 1):** 6 department canvases (bot-owned, pinned via channel bookmarks), comms_engine headline templates for every publication, dashboard-refresh repointed to the canvases.
**Phase 2 — channel merges (week 2):** rename/repoint publishers (scripts, SKILL.md, `fleet/expected_outputs.json` ~136 entries, guardian markers, dashboard feeds), invite the bot where it is not a member, run ONE Monday with old + new in parallel, verify, then archive the old channel with a pinned "moved to …" message.
**Phase 3 — archive dead channels (week 2).**
**Phase 4 — measure (30 days):** posts/day, automated share, reactions and human posts per report channel, before/after. Target: ~70 → ~25 posts/day, every report findable in ≤2 clicks without scrolling.

## 6. Dependencies touched
`fleet/expected_outputs.json` (136 entries, channel ids + markers), `bin/comms_engine.py`, `bin/monday_compile.py`, `bin/weekly_canvases.py` + `fleet/canvas_state/canvas_ids.json`, `bin/monthly_eom_recap.py` (channel list), the native agents and Cowork tasks that post to each merged channel, fleet-guardian / field_scorecard markers, `Business Dashboard Website/REFRESH_RUNBOOK.md` feed table, PUBLICATION_CALENDAR.md, BUSINESS_OS.md. Bot membership: needs `/invite @vp_ops_engine` in any renamed/new private channel (one-time, Joshua).

## 7. Decisions that are Joshua's
1. Go on the channel map in §3 (B, C, D).
2. Missed-call pings: EOD "still no callback" line per store (recommended) vs. keep every per-call ping.
3. #hr-documentation / #controllio-review — keep, repurpose, or archive.
4. #ask-handbook → merge into #ask-goldilocks?
5. Delete the plaintext password messages in the funds channels (Claude does not delete messages).
