# Tiered CEO / Supervisor / Manager Summary System — Plan (v1, awaiting Joshua's go)

**Drafted:** 2026-08-24 · **Status:** PLAN ONLY — nothing built yet, per Joshua's instruction to report back first.
**Domain:** 1 — Valley Pawn · **Project:** Communcations

## What Joshua asked for

Every Monday + end of month, three tiers of summary:

| Tier | Audience | Scope |
|---|---|---|
| 1 | Joshua (CEO) | Entire picture: operations + marketing, HR, compliance, eBay, social audits. Concise but meaningful. |
| 2 | Preston (Supervisor) | Operational half only: performance data, the numbers, per-store analysis. |
| 3 | 5 Store Managers | Snapshot of their own store's week, and their month at EOM. |

## Expert Review Board — decisions

Board convened (BI architect, ops exec, comms designer, reliability engineer, cost controller). Recommendation, unanimous:

1. **Synthesis layer, not new data pulls.** Every input already exists by Monday mid-morning: `monday-bravo-combined-compile` (posts to #employee-performance, #layaway-review, #first-payment-default, #aged-inventory-review, #store-performance at 8:00 AM), `weekly-store-kpis` (10:30 AM leaderboard), `weekly-timekeeping-analysis` (9 AM), `weekly-analytics-summary` (GA4, 9 AM), `review-obtained-last-week`, `weekly-social-media-recap`, `email-analytics-weekly` (Fri), eBay weekly rankings (launchd), plus pipeline CSVs in `Bravo Data Extraction/output/` and `Scheduled/_shared-bravo-data/`. The brief tasks READ those outputs and channels — **zero new Bravo touches, zero contention, fully additive (Rule #4).**
2. **Two new scheduled tasks, not six.** `weekly-enterprise-brief` (Mon 11:30 AM ET) and `monthly-enterprise-brief` (1st, 11:30 AM ET). Each produces all three tiers in one run from one shared read. Rationale: the fleet is at 134 enabled tasks with ~5,345 recorded usage-cap skips — every added task is real cap pressure. Model pin: `claude-sonnet-5`.
3. **Delivery = Slack DMs**, matching existing patterns. Joshua → DM D03BHQH5VGT. Preston → DM U03BWMEM9GR. Managers → per-store DM using the same roster as `weekly-loan-layaway-manager-dms`. No new channels (sprawl; DMs are where these audiences already get their reports). Manager messages are bound by **Field Communication Standard v3** (plain language, lead with the takeaway, ~100 words, no system names). Monthly CEO brief additionally saves a full doc to Drive and links it.
4. **Graceful degradation is mandatory.** The Monday producer chain has a documented silent-death history (8/3–8/21 outages). If a source section is missing, the brief says "not available this week," lists it in Joshua's exceptions section, and still ships. It never aborts, never blocks on one dead feed. Guardian coverage via `fleet/expected_outputs.json` entries (per HARDENING_STANDARD — no new bespoke watchdogs).
5. **Dedupe before sending** — read the target DM for a same-date brief before posting (safe for the fleet-guardian rerun manifest).

## Content spec

### Tier 1 — Joshua, weekly (Monday ~11:30 AM DM)
**Format revised 2026-08-24 after Joshua's live review of two samples: KPI scorecard + opportunity stores. NO leaderboards, NO categorical rankings — "categorical ranking is not actionable." Every KPI line names the worst store and its number. The brief must steer action.**
1. **One-line read of the week.**
2. **KPI scorecard** — each line: KPI, company number + trend, ✅/⚠️/🔴 status, and the OPPORTUNITY STORE (worst performer + its number). KPIs: net revenue pace ($/day vs prior month's rate), loan balance + WoW change per store (flag any shrinking book), PSC yield (PSC MTD ÷ loan balance), past-due 75d % vs 5% policy, FPD exposure $, **layaway yield % (collected MTD ÷ balance — from the layaway canvas)**, layaway trouble counts (Locates always flagged), retail sales pace WoW, aged >1yr inventory %, eBay 30-day sell-through + seller-standards flags.
3. **This week's steers** — 3–5 concrete actions, grouped by store: which store is the opportunity store (most red KPIs) and what to do there.
4. **People & compliance** — compressed: interviews/hiring, OT/coverage flags, FFL/gun-audit open items, policy items.
5. **Automation health** (Joshua-only; technical OK).
6. **Decisions waiting** — from `OPEN_ITEMS_REGISTER.md` Domain-1 rows blocked on Joshua.

Reads in under 2 minutes. Weekly = previous week + MTD (Joshua's spec).

### Tier 2 — Preston, weekly (same run)
Same KPI scorecard + opportunity-store logic (Preston needs KPIs and where they're missing, per Joshua), then a per-store detail block (each store: the 10 KPIs, employee callouts, timekeeping/coverage). No compliance-admin, no automation internals, never failure notices (standing policy).

### Tier 3 — Managers, weekly (same run, 5 DMs)
Their store only, plain language per v3: "Your week: sales $X (rank N of 5), loans written Y, past-due at Z% (policy: under 5%), N new reviews. Focus this week: {one item}." ~80 words.

### Monthly (1st of month ~11:30 AM)
Same three tiers, month-over-month + vs targets: monthly-analytics-report KPIs, monthly-employee-sales-rankings, bonus qualifier status, monthly gun audit + scrap + NICS (latest available), eBay ratings sweep, follower growth. CEO version saves a full Drive doc + links `compile-monthly-minutes` (which stays separate — minutes are the formal record; this is the performance digest). Manager monthly includes bonus standing.

## What this does NOT touch
No existing task modified. No Bravo pulls added. `compile-monthly-minutes`, `sunday-checklist-summary`, `weekly-loan-layaway-manager-dms` all continue unchanged. The three running audit sessions (email marketing, online store, marketing channel) are inputs later, not dependencies.

## Build sequence (on Joshua's go)
1. Build `weekly-enterprise-brief` SKILL.md (Execution Contract + v3 standard + failure policy), register, pin sonnet.
2. Manual proof run — Joshua sees all 3 tiers before any manager gets one (managers held out of run 1 if preferred).
3. Add expected_outputs.json entries; add to rerun manifest.
4. Build `monthly-enterprise-brief` the same way; first fire Sept 1.
5. CHANGELOG + BUSINESS_OS + Open Items Register entries.

## Open question for Joshua (only one)
Manager weekly snapshot: send Monday morning (recap of last week, arrives with everyone else's) — recommended — or Friday close-of-week? Default is Monday unless he says otherwise.
