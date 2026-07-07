# Valley Pawn Business OS

> **Master operating reference for Full Circle Finance Inc DBA Valley Pawn.** Read this FIRST before any non-trivial work. This document maps every piece of infrastructure (skill, scheduled task, pipeline cell, saved report, GDrive folder, Slack channel) and tells you how they relate. It is the single source of truth for "what already exists" when starting any new project.

**Created:** 2026-05-20
**Owner:** Joshua Davis (jdavis@fcfpawn.com)
**Update cadence:** Update whenever a new piece of infrastructure ships, or a constraint changes.

---

## How To Use This Document

| You're about to... | Read this first |
|---|---|
| Start a new project | Section 2 (Domain map) — find your domain, see what already exists, plan ADDITIVE work |
| Resume an in-progress project | The project's own STATUS.md, then this doc for cross-cutting context |
| Add a new scheduled task | Section 4 (Pipeline & orchestration), then Section 6 (Project lifecycle) |
| Trigger a Bravo extract | Section 4 → pipeline cells already in production. Reuse first |
| Add a new Bravo report | Section 6 → 4-step additive pattern. Never modify "Claude Loan Reviews", "Claude Low Dollar Loans", "75 Days Past Due", or any other existing saved report |
| Answer "what does Claude do for the business?" | Section 2 + Section 7 (data flow) |
| Decide what to build next | Section 8 (gap analysis) + Section 9 (backlog) |

---

## Section 1 — TL;DR Map

**By the numbers (2026-05-20):**

- **8 business domains** (plus orchestration)
- **28 named skills** (context + workflow)
- **58 scheduled tasks** in `/Users/joshuadavis/Documents/Claude/Scheduled/` (mix of active and disabled)
- **18 Bravo pipeline handlers** (some production, some still being built)
- **10 active project folders** in `/Users/joshuadavis/Documents/Claude/Projects/`
- **5 retail stores** (CUL, HAR, LEX, ROA, WAY) + **1 vacation rental** (Bald Rock)
- **Cross-business:** Valley Pawn (primary) + Bald Rock STR + Salt Run Landscape Co.

**Critical "don't touch" list** (production, hardened, business-critical):
- `monday-bravo-combined-run` — Monday orchestrator, every weekly review depends on it
- `daily-funds-verification` — runs every 6 PM, cash-control safety net
- `weekly-loan-layaway-review` — primary risk-monitoring report
- `weekly-aged-inventory-report` — inventory health
- `weekly-employee-sales-rankings` — staff performance + bonus calc input
- `weekly-valley-pawn-email-campaign` — Thursday 10 AM marketing send
- `monthly-we-buy-gold-silver-email` — 1st of month marketing send
- `weekly-payroll-to-qbo` — Friday payroll journal entries
- `nightly-chekkit-review-responses` — daily reputation management
- `bravo_watcher.ahk` + `bravo_export.ahk` dispatch tables — modifying breaks the whole pipeline
- All saved Ad Hoc reports in Bravo (Claude Loan Reviews, Claude Low Dollar Loans, Claude Low Dollar Buys, Claude First Payment Default, 75 Days Past Due, layaway saved reports)

---

## Section 2 — Domain Map

Every piece of infrastructure is categorized into one of 8 domains. "Cross-domain" pieces (e.g. `daily-funds-verification` is both Ops and Finance) are listed in their primary domain with a cross-reference.

Status legend:
- **A = Active & scheduled** (cron-fired, runs without prompting)
- **T = Triggered** (manual on-demand or chained from another task)
- **M = Manual-assist** (Claude helps when asked, no automation)
- **B = Built but disabled** (code exists, schedule turned off)
- **G = Gap** (identified need, not yet built)

### Domain 1 — Operations & Loss Prevention

**Mission:** keep all 5 stores running cleanly day-to-day; catch problems before they compound.

| Infrastructure | Type | Status | Frequency | Notes |
|---|---|---|---|---|
| `daily-funds-verification` | Scheduled task | A | Daily 6pm | Reconciles Joshua's funds-sent against Bravo Safe Register Journal |
| `daily-cloudcover-check` | Scheduled task | A | Mon–Sat 10am | Pandora Cloud Cover camera/security check |
| `daily-dress-code-check` | Scheduled task | A | Mon–Sat 10:30am | Google Home cameras → dress code compliance |
| `daily-clockin-check` | Scheduled task | A | Mon–Sat 10:15am | Gusto clock-in audit. **MCP-first** (API `list_time_records`, headless — no browser/login) with the old Chrome flow retained as automatic fallback. Changed 2026-06-10. |
| `controlio-offline-agent-check` | Scheduled task | B | Daily 9am | Employee monitoring agent uptime |
| `monday-bravo-combined-run` | Scheduled task | T (manual) | Mondays | Orchestrator — fans out to 5 weekly reviews via pipeline |
| `monday-bravo-reminder` | Scheduled task | (folder, unverified) | — | |
| `monday-store-rankings` | Scheduled task | T (manual) | Mondays | Cross-store performance ranking from Company KPIs |
| `monthly-analytics-report` | Scheduled task | A | 1st of month 8am | Company KPI snapshot → #store-performance + Sheets |
| `weekly-loan-layaway-review` | Scheduled task | T (manual) | Weekly | Past-due loans + layaways across all stores |
| `weekly-loan-layaway-manager-dms` | Scheduled task | B | Mon 9am | Per-store manager DMs of the review |
| `monthly-gun-audit-report` | Scheduled task | A | 16th of month | Compliance — gun audit summary |
| `monthly-gun-audit-summary` | Scheduled task | B | 16th of month | Companion to above |
| `loan-layaway-review` | Skill | — | — | Reference implementation |
| `bravo-store-cycle` | Skill | — | — | Multi-store login orchestration (used by computer-use legacy flows) |
| `bravo-context` | Skill | — | — | Bravo reference doc |

**Gaps in Operations:**
- (G) No cross-store comparison dashboard refreshable on demand (the monthly is good, weekly is missing)
- (G) No "anomaly alert" — e.g. a store's safe count drifts >5% from rolling average → DM Joshua
- (G) No formal incident log / RCA template

---

### Domain 2 — HR / Payroll / People Ops

**Mission:** payroll runs cleanly every Friday; staff attendance, comp, and compliance auditable.

| Infrastructure | Type | Status | Frequency | Notes |
|---|---|---|---|---|
| `weekly-timekeeping-analysis` | Scheduled task | A | Mon 2am | Gusto Time Tracking via Chrome → #timekeeping-summary 9am. _Note 2026-06-10: the Gusto MCP (`list_time_records`) now returns real-time native shift data (the old "MCP returns empty" no longer holds) — migration candidate to drop Chrome, as done for daily-clockin-check._ |
| `weekly-employee-sales-rankings` | Scheduled task | T (manual) | Weekly | Pipeline-driven (`employee-activity`), MTD rankings |
| `monthly-employee-sales-rankings` | Scheduled task | A | 1st of month | Final monthly rankings → #employee-performance |
| `monthly-bonus-targets` | Scheduled task | T (manual) | Monthly | Generates next month's revenue bonus targets (Option B yield method) |
| `dismiss-employee` | Scheduled task | T (manual) | Ad hoc | Gusto termination flow |
| `gusto-keep-alive` | Scheduled task | (folder) | — | Session refresh |
| `daily-clockin-check` | Scheduled task | A | Daily 10:15am | (Cross-ref: Ops) — MCP-first w/ Chrome fallback (2026-06-10) |
| `weekly-payroll-to-qbo` | Scheduled task | A | Fri 10am | Pulls Gusto payroll, builds JEs by store class (cross-ref: Finance) |
| `onboard-employee` | Skill | — | — | Gusto self-onboarding invite flow |
| `daily-clockin-check` | Skill | — | — | (same name as scheduled task) |

**Gaps in HR:**
- (G) No automated 90-day review reminder
- (G) No staff training tracker
- (G) No employee NPS / satisfaction pulse

---

### Domain 3 — Finance / Accounting / Cash

**Mission:** books are reconciled monthly with zero drift; daily cash safe; QBO reflects reality.

| Infrastructure | Type | Status | Frequency | Notes |
|---|---|---|---|---|
| `daily-funds-verification` | Scheduled task | A | Daily 6pm | (Cross-ref: Ops) |
| `eom-bravo-gl-export` | Scheduled task | B | 5th of month | Cycles Bravo, exports Consolidated GL → QBO import |
| `monthly-reconciliation-report` | Scheduled task | B | 5th of month | QBO month-end recon → Silverline CPA |
| `monthly-cpa-report` | Scheduled task | (folder) | Monthly | |
| `weekly-payroll-to-qbo` | Scheduled task | A | Fri 10am | (also HR) |
| `qbo-context` | Skill | — | — | TWO QBO accounts warning (jdavis vs zapvp1 — bookkeeper's is read-only) |
| `quickbooks-online` | Skill | — | — | Web-app driver |

**Gaps in Finance:**
- (G) No real-time P&L / dashboard
- (G) No expense-anomaly detection (Amex outliers, unusual vendors)
- (G) No accounts-receivable aging tracker (if any A/R exists)
- (G) No tax-prep prep package compiled mid-year

**WARNING:** `qbo-context` mandates a TWO-ACCOUNT check before any QBO write. The bookkeeper's account (zapvp1@me.com) is STRICTLY READ-ONLY — never edit anything there.

---

### Domain 4 — Marketing / Brand / Email / Reputation

**Mission:** every customer touchpoint reinforces the unified Valley Pawn brand; reviews stay 4.5+; email engagement holds 25%+ open.

| Infrastructure | Type | Status | Frequency | Notes |
|---|---|---|---|---|
| `weekly-valley-pawn-email-campaign` | Scheduled task | A | Thu 10am | Brevo, rotating themes |
| `monthly-we-buy-gold-silver-email` | Scheduled task | A | 1st of month 9am | Brevo dedicated send |
| `weekly-new-deal-request` | Scheduled task | A | Tue 9am | DMs managers for deals to feature |
| `daily-social-media-content` | Scheduled task | B | Daily 9am | Canva → FB/IG/YouTube |
| `weekly-social-media-content` | Scheduled task | B | Mon 8am | IG/TikTok + WordPress blog draft |
| `tuesday-facebook-posts` | Scheduled task | B | Tue 10am | Deals & spotlights, all 5 FB pages |
| `wednesday-facebook-posts` | Scheduled task | B | Wed 12pm | Tips & education |
| `saturday-facebook-posts` | Scheduled task | B | Sat 9am | Community & local events |
| `thursday-youtube-employee-clips` | Scheduled task | B | Thu 8am | Employee video clips → Shorts/TikTok |
| `weekly-youtube-shorts` | Scheduled task | B | Sun 7pm | 7 Shorts/week generation |
| `valley-pawn-blog-publisher` | Scheduled task | A | Mon & Thu 9am | WordPress blog auto-post |
| `chekkit-new-review-alert` | Scheduled task | A | Hourly 9–9 | Alerts to #google-reviews |
| `chekkit-unanswered-alert` | Scheduled task | A | Mon 6pm (cron `1-6`) | DMs employees their store's count |
| `chekkit-review-responder` | Scheduled task | (folder) | — | |
| `nightly-chekkit-review-responses` | Scheduled task | A | Daily 7:30pm | Auto-respond to 4–5★ reviews |
| `chekkit-weekly-review-requests` | Scheduled task | B | Tue 4:40pm | Sends Chekkit review-request campaigns + imports to Brevo |
| `review-obtained-last-week` | Scheduled task | A | Mon 3am | Prior-week review-count ranking → #google-reviews |
| `brightlocal-weekly-sync-alerts-check` | Scheduled task | B | Tue 9am | Listing drift audit (GBP, Bing, Apple, FB, Yelp) |
| `directory-listing-monitor` | Skill | — | — | Reference implementation of weekly drift check |
| `directory-listing-push` | Skill | — | — | On-demand multi-directory broadcast (rebrand, move, etc.) |
| `weekly-analytics-summary` | Scheduled task | A | Mon 2:30am | Google Analytics prior-week → #claude-updates 9am |
| `wordpress-token-keepalive` | Scheduled task | A | 9am & 5pm daily | OAuth refresh |
| `brevo-context` | Skill | — | — | Brevo reference doc |
| `valley-pawn-context` | Skill | — | — | Brand voice, hard email requirements (logo + Call/Text + 5-store directory), canonical Maps URLs |
| `monthly-top-sales-review` | Scheduled task | B (manual) | Monthly | Top 5 categories + top 20 items, all stores |

**Hard rules carried in `valley-pawn-context`:**
1. Every customer email MUST include: VP logo header, Call+Text buttons (both showing the number on the button face), and the full 5-store directory at bottom.
2. NEVER mention firearms, guns, or weapons in social media content (Google/Meta policy).
3. NEVER use the legacy "Dixie Pawn" name — the Harrisonburg store is Valley Pawn.
4. Use canonical `Valley+Pawn+City+VA` Maps URLs, NOT raw-address URLs (the latter pulls stale Dixie Pawn photos for Harrisonburg).

**Publishing Infrastructure — Publer as the publishing layer (2026-06-19+):**

All FB Page + brand IG publishing now routes through **Publer Business tier ($50/mo)**. The direct-Graph-API path (the `facebook-post` skill, the System User token chain, the `tokens.json` file) is **deprecated for publishing operations** as of 2026-06-19.

- **Why the switch:** the sub-portfolio ownership tangle (Valley Pawn Waynesboro sub-portfolio is admin'd by an unrecoverable IG identity) blocked direct Graph API publishing to Waynesboro and Culpeper Pages. Meta also kept invalidating Page Access Tokens every 24-72 hours despite "long-lived" classification. Publer's OAuth bypassed both problems entirely.
- **Account map:** `/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/publer_accounts.json` — all 6 FB Pages (Brand, Lexington, Roanoke, Harrisonburg-Va, Culpeper, Waynesboro) + @valley_pawn IG mapped to Publer account IDs.
- **API config:** `/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/publer_config.json` — key + base URL + workspace ID.
- **API auth header style:** `Authorization: Bearer-API {key}` (Publer's custom format — NOT standard `Bearer {key}`).
- **Workspace ID:** `6a358d48fe216c70f7e65d4e` (Valley Pawn workspace).
- **30-day content calendar:** `/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/VP_30_DAY_CONTENT_CALENDAR.md` — brand pillars, store rotation, recurring categories.
- **What stays:** Midjourney for hero image gen (`vp-hero-image` skill), Canva for brand template wrap (`vp-asset-compose` skill), `vp-content-batch` for content orchestration and Bravo intake integration. These are upstream of Publer — they produce the assets that Publer schedules.
- **What's deprecated:** `facebook-post` skill (kept for reference; do not use for new publishing). Direct Graph API publishing flows. System User token regeneration cycles.
- **What pivots:** `friday_close_engagement.py` analytics source switches from Meta Graph API direct to Publer's analytics endpoint (cleaner, no scope wall).
- **Sub-portfolio status:** Meta Support ticket draft staged at `META_SUPPORT_FINAL_SUBMISSION.md`. Now OPTIONAL — Publer routes around the ownership issue for publishing. Submit only if Joshua wants the underlying Meta admin chain cleaned up.
- **B-status social tasks** in this domain (the disabled `daily-social-media-content`, `weekly-social-media-content`, `tuesday-facebook-posts`, `wednesday-facebook-posts`, `saturday-facebook-posts`, `thursday-youtube-employee-clips`, `weekly-youtube-shorts`) — these were broken by the token wall. Their Publer-routed replacements should be built as NEW tasks (Rule #4 additive). Suggested naming: `publer-daily-social`, `publer-weekly-social-batch`, etc. Don't try to fix the existing B-status tasks; clone alongside.

**Gaps in Marketing:**
- (G) No monthly performance digest (open/click rates + best-performing subject lines)
- (G) No email-list segmentation analysis (cold/warm/active customers)
- (G) No A/B testing framework
- (G) Many social tasks are DISABLED (B status) — *RESOLVED PATH 2026-06-19:* build Publer-routed replacements alongside as new additive tasks (see Publishing Infrastructure subsection above)
- (G) No SEO performance tracker for thevalleypawn.com keyword positions

---

### Domain 5 — Inventory / Procurement

**Mission:** the right merchandise is on the shelves at the right cost; old stock doesn't tie up capital.

| Infrastructure | Type | Status | Frequency | Notes |
|---|---|---|---|---|
| `weekly-aged-inventory-report` | Scheduled task | T (manual) | Weekly | Pipeline-driven via `aged-inventory-summary` cell |
| `weekly-aged-inventory-review` | Scheduled task | B | Mon 5:32am | (Older duplicate?) |
| `new-inv-weekly-report` | Scheduled task | B | Mon 8am | Sell-through + margin + aging for new inventory |
| `new-inv-intake` | Skill | — | — | Log new wholesale purchase → New Inventory Tracker sheet + Bravo receiving + Slack #new-inventory |
| `daily-supply-order` | Scheduled task | A | Tue 6am | Scan #supply-request → Amazon order data |
| `tuesday-supply-summary` | Scheduled task | A | Tue 10:45am | Auto-approve <$350 or ping Joshua |
| `tuesday-supply-checkout` | Scheduled task | A | Tue 11am–7pm /15min | Amazon Business cart checkout |
| `mm-merchandisers-daily-scan` | Scheduled task | A | Daily 9am | Gmail scan for M&M order summary emails (triggers `new-inv-intake`) |
| `monthly-gun-audit-report` | Scheduled task | A | 16th of month | (Cross-ref: Ops) |
| `monthly-sold-inventory-refresh` | Scheduled task | (folder) | Monthly | |
| `distributor-setup-monitor` | Scheduled task | A | Daily 9am | Gmail scan for new distributor accounts |
| `daily-distributor-application-monitor` | Scheduled task | (folder) | Daily | |
| `bravo-context` | Skill | — | — | aged-inventory views, inventory module |

**Gaps in Inventory:**
- (G) No vendor performance scorecard (lead time, defect rate, margin by vendor)
- (G) No reorder-point automation for fast-movers
- (G) No category mix analysis (what % of capital in each category vs. sell-through rate)
- (G) No competitive price scrape (is our retail priced right?)

---

### Domain 6 — Loans / Portfolio (the loan side of pawn)

**Mission:** maximize true ROI per $ deployed; minimize forfeit/FPD exposure.

| Infrastructure | Type | Status | Frequency | Notes |
|---|---|---|---|---|
| `weekly-loan-layaway-review` | Scheduled task | T (manual) | Weekly | (Cross-ref: Ops) |
| `weekly-fpd-ranking` | Scheduled task | B | Mon 9am | FPD ranking by store + category. Pipeline-driven via "Claude First Payment Default" saved report. Standalone (NOT in monday-bravo-combined-run) |
| `fpd-history-backfill` | Scheduled task | (folder) | — | Historical FPD backfill |
| `weekly-loan-layaway-manager-dms` | Scheduled task | B | Mon 9am | (Cross-ref: Ops) |
| `Optimize Loan Portfolio` | Project folder | In progress | — | **CURRENT PROJECT.** True-ROI analysis by collateral category. STATUS.md inside. |
| `Deep KPI analysis` | Project folder | (existing) | — | Earlier KPI analysis work |

**Existing saved Bravo reports relevant here:**
- "Claude Loan Reviews" — currently has BUY/$1–$5 criteria (essentially low-dollar buys; NOT portfolio analysis). Used by `loan-reviews` pipeline cell.
- "Claude Low Dollar Loans" — low-dollar loan filter. Used by `low-dollar-loans` pipeline cell.
- "Claude Low Dollar Buys" — low-dollar buy filter. Used by `low-dollar-buys` pipeline cell.
- "Claude First Payment Default" — FPD cohort. Used by `fpd-cohort` pipeline cell. Needs per-store saved reports finished.
- "75 Days Past Due" — 75-day past-due loans. Used by `loans-75-days-past-due` pipeline cell.

**Gaps in Loans/Portfolio:**
- (P) **Portfolio cohort analysis with true ROI by category** — the current Optimize Loan Portfolio project addresses this. Requires NEW saved Ad Hoc report "Claude Loan Portfolio 2026" (additive — don't modify "Claude Loan Reviews") and NEW handler `LoanPortfolio2026.ahk`.
- (G) No LTV-vs-redemption curve dashboard
- (G) No "high-watermark loan" alert (loans above some $ threshold for visibility)
- (G) No customer-tier segmentation (Joshua explicitly excluded this from the current project; it's a future build)

---

### Domain 7 — Online Sales

**Mission:** eBay inventory is priced right, listings are healthy, returns are managed.

| Infrastructure | Type | Status | Frequency | Notes |
|---|---|---|---|---|
| `weekly-ebay-sales-ranking` | Scheduled task | B | Mon 11:33am | Verifies a LaunchAgent script posted eBay rankings to #ebay-performance |
| `ebay-context` | Skill | — | — | eBay store operating reference |

**Gaps in Online Sales:**
- (G) No automated listing-health audit (stale listings, mispriced items)
- (G) No buyer-message auto-triage
- (G) No cross-channel inventory sync verification (Bravo ↔ eBay)
- (G) No web store activity (if thevalleypawn.com has shop functionality)

---

### Domain 8 — Property / Real Estate

**Mission:** Bald Rock STR runs cleanly; future real-estate moves are tracked.

| Infrastructure | Type | Status | Frequency | Notes |
|---|---|---|---|---|
| `bald-rock-15-day-contract` | Scheduled task | A | Daily 9am | Auto-send DocuSign 15 days before check-in |
| `bald-rock-auto-contract` | Scheduled task | B | Daily 8am | Older variant (probably superseded by 15-day) |
| `bald-rock-signing-status` | Scheduled task | B | Daily 3am | DocuSign signing status check |
| `bald-rock-property` | Skill | — | — | Property operating manual (Wi-Fi, lockbox, check-in, pricing) |
| `send-guest-contract` | Skill | — | — | Manual DocuSign send |
| `weekly-jacksonville-property-search` | Scheduled task | (folder) | Weekly | Future expansion property search |
| `weekly-st-augustine-property-search` | Scheduled task | (folder) | Weekly | Future expansion property search |
| `Short Term Rental Optimization` | Project folder | — | — | |
| `Landscape design` | Project folder | — | — | |

**Gaps in Property:**
- (G) No automated guest-review monitoring (Airbnb/VRBO)
- (G) No pricing-optimization layer (compare against comp rentals weekly)
- (G) No maintenance-issue tracker

---

### Cross-Domain / Other

| Infrastructure | Type | Status | Notes |
|---|---|---|---|
| `amazon-return` | Scheduled task | T (manual) | Process Amazon returns autonomously |
| `amazon-returns` | Skill | — | Return-handling reference (Joshua's preferences) |
| `compile-monthly-minutes` | Skill | — | Monthly business minutes from Lainie's emails + Slack |
| `annual-board-review` | Scheduled task | A | Jan 1, midnight | Annual board presentation generator |
| `monthly-capability-drift-audit` | Scheduled task | A | 1st of month 7am | Diffs live skills/plugins/connectors/scheduled-tasks vs Section 13; auto-updates BUSINESS_OS.md additively, stages `SKILL_DELTA_*` for skill edits, posts deltas to `#claude-notifications`. The self-maintaining half of the capability inventory. Created 2026-06-29 |
| `weekly-returns-summary` | Scheduled task | A | Mon 1am | Customer returns tracking |
| `weekly-email-cleanup` | Scheduled task | (folder) | Weekly | Inbox hygiene |
| `daily-mail-unsubscribe` | Scheduled task | (folder) | Daily | Unsubscribe management |
| `domain-transfer-check` | Scheduled task | (folder) | — | |
| `cloud-cover-keep-alive` | Scheduled task | (folder) | — | |
| `setup-cowork` | Skill | — | — | Onboarding skill |
| `skill-creator` | Skill | — | — | Skill authoring |

**Other businesses (separate from Valley Pawn):**

- **Salt Run Landscape Co.** — `salt-run-weekly-analytics` (A), `salt-run-monthly-seo-audit` (A), `salt-run-quarterly-phase-check` (A). Separate business with its own analytics/SEO cadence.
- **Bald Rock STR** — see Domain 8.

---

## Section 3 — Skills Catalog (28 total)

Skills are loaded via the Skill tool. They split into two types: **context skills** (reference docs Claude reads) and **workflow skills** (procedural recipes Claude follows).

### Context skills (read-then-apply)
- `valley-pawn-context` — Brand, locations, team, hard rules. 580 lines. The mother doc.
- `bravo-context` — Bravo POS reference (modules, reports, gotchas, additive-only rule)
- `qbo-context` — QBO state, dual-account warning
- `quickbooks-online` — QBO web-app driver
- `brevo-context` — Brevo email marketing reference
- `ebay-context` — eBay store reference
- `bald-rock-property` — STR property reference

### Workflow skills (do-the-task)
- `loan-layaway-review` — Weekly past-due review
- `weekly-loan-layaway-review` — On-demand variant
- `monday-bravo-combined-run` — The Monday orchestrator
- `bravo-store-cycle` — Multi-store login flow
- `daily-clockin-check` — Gusto attendance check
- `daily-funds-verification` — Daily safe verification
- `directory-listing-monitor` — Weekly listings drift audit
- `directory-listing-push` — On-demand multi-directory broadcast
- `compile-monthly-minutes` — Monthly minutes from Lainie's emails + Slack
- `onboard-employee` — Gusto self-onboarding invite
- `new-inv-intake` — Log wholesale purchase → tracker + Bravo + Slack
- `new-inv-weekly-report` — Weekly sell-through report
- `amazon-returns` — Autonomous Amazon return flow
- `send-guest-contract` — DocuSign guest contract
- `pdf`, `xlsx`, `docx`, `pptx` — Document creation skills
- `schedule` — Create/update scheduled tasks
- `skill-creator` — Author/edit/eval skills
- `setup-cowork` — Onboarding

---

## Section 4 — Bravo Data Extraction Pipeline (the central nervous system)

**Pipeline root:** `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/`

The pipeline is the load-bearing infrastructure that powers all Bravo-touching scheduled tasks. It is an AHK-based service running inside a Windows VM in Parallels. Drop a trigger JSON in `triggers/`, the watcher picks it up, drives Bravo via UIA, writes a CSV to `output/`, writes a result to `results/`.

**Last watcher restart (verified 2026-05-20):** 08:19:39, build tag `claim-fix-2026-05-13`, 18 handlers registered.

### Registered pipeline handlers (the cells you can trigger)

| Cell name | Handler file | What it pulls | Production-ready? |
|---|---|---|---|
| `safe-register-journal` | SafeRegisterJournal.ahk | Per-store Safe register journal for a given day | ✅ Yes (daily-funds-verification uses) |
| `till-register-journal` | TillRegisterJournal.ahk | Till register journal | ⚠️ Built, unverified at scale |
| `loans-75-days-past-due` | Loans75DaysPastDue.ahk | 75-day past-due loans (uses saved report "75 Days Past Due") | ✅ Yes (weekly-loan-layaway-review uses) |
| `layaways` | Layaways.ahk | Layaway badge counts | ✅ Yes |
| `aged-inventory-summary` | AgedInventorySummary.ahk | Aged inventory by category × age bucket | ✅ Yes (weekly-aged-inventory-report uses) |
| `aged-jewelry-markdown` | AgedJewelryMarkdown.ahk | Aged jewelry items for markdown | ⚠️ Built |
| `aged-general-merch-markdown` | AgedGeneralMerchMarkdown.ahk | Aged general merch for markdown | ⚠️ Built |
| `employee-activity` | EmployeeActivity.ahk | Per-employee sales/activity | ✅ Yes (weekly-employee-sales-rankings uses) |
| `company-kpis` | CompanyKpis.ahk | Company-wide KPIs (SSRS report) | ⏳ Stub — needs SSRS URL captured |
| `sales-by-vendor` | SalesByVendor.ahk | Sales by vendor | ⏳ Needs Sold Inventory date dialog fix |
| `chekkit-inactives` | ChekkitInactives.ahk | Inactive customers for Chekkit review-requests | ⏳ Needs row-walk refactor |
| `loan-reviews` | LoanReviews.ahk | Saved report "Claude Loan Reviews" output (currently low-dollar buys, not portfolio) | ⚠️ Working but saved report has narrow criteria |
| `fpd-cohort` | FpdCohort.ahk | FPD cohort (uses saved report "Claude First Payment Default") | ⏳ Per-store saved reports incomplete |
| `low-dollar-loans` | LowDollarLoans.ahk | Loans <$5 | ✅ Working |
| `low-dollar-buys` | LowDollarBuys.ahk | Buys <$5 | ✅ Working |
| `fpd-lookback-12mo` | (handler) | 12-month FPD lookback | ⚠️ Built |
| `active-inv-details` | (handler) | Active inventory detail rows | ⚠️ Built |
| `inventory-details` | (handler) | Inventory details | ⚠️ Built |
| `sold-inv-details` | (handler) | Sold inventory details | ⚠️ Built |
| `buys-from-public` | (handler/lib) | Buys from public (used by other handlers' grid walk) | ✅ Library |
| `uia-discover` | (handler) | UIA element discovery tool (debugging) | 🛠 Dev only |

**Trigger schema:**
```json
{
  "id": "<task-id>-YYYY-MM-DDTHH-MM-SS",
  "requested_at": "<ISO8601>",
  "reports": [
    {"name": "<cell-name>", "stores": ["CUL","HAR","LEX","ROA","WAY"], "date": "YYYY-MM-DD" or "YYYY-MM-DD..YYYY-MM-DD"}
  ]
}
```

**Trigger drop:** use `mcp__Control_your_Mac__osascript` with `do shell script "echo '<json>' > <triggers-path>/<id>.json"`. See `daily-funds-verification/SKILL.md` for the canonical pattern.

**Poll for completion:** check `results/<id>.result.json`. Typical run time: 30s per cell.

---

## Section 5 — Operating Principles (consolidated)

Every rule that's been baked into skills + memory, in one place. Read this whenever starting a new build.

### Rule 1 — Claude does the work (valley-pawn-context, Rule #1)
Take action; don't ask. The only exceptions: irreversible mistakes (sending wrong recipient, deleting permanently, spending money). Don't say "would you like me to…" — just do it.

### Rule 2 — Never ask Joshua to log in (valley-pawn-context, Rule #2)
Use Chrome MCP with saved passwords. Never ask Joshua to click "sign in" or enter credentials.

### Rule 3 — Always check prior work first (valley-pawn-context, Rule #3 + memory `feedback_check_prior_work.md`)
Before asking a clarifying question, before any extract, before any new analysis — inventory what exists:
1. Project folder STATUS.md / README.md / FINDINGS.md
2. Bravo Data Extraction pipeline `output/` folder for overlapping date ranges
3. Relevant Slack channel for recent posts
4. Memory files

Lead plans with "here's what we have" and "here's the gap" — never with "here's what I'd build from scratch."

### Rule 4 — Build new alongside; never modify what works (valley-pawn-context, Rule #4 + memory `feedback_additive_only.md` + bravo-context Additive-Only section)
Off-limits without explicit ask:
- Existing saved Ad Hoc reports in Bravo
- Existing AHK handlers in `Bravo Data Extraction/reports/`
- Existing entries in `bravo_watcher.ahk` / `bravo_export.ahk` dispatch tables
- Monday combined Bravo run + every other production scheduled task

New work pattern (4 steps):
1. NEW saved Ad Hoc report in Bravo (project-specific name)
2. CLONE existing handler → NEW file with distinct function + constants
3. ADD a NEW pipeline cell name to dispatch tables (don't edit existing rows)
4. Restart watcher

### Rule 5 — Two QBO accounts; one is read-only (qbo-context)
- `jdavis@fcfpawn.com` = full access
- `zapvp1@me.com` = bookkeeper's, **READ-ONLY**, never edit anything there

### Rule 6 — Email send hard requirements (valley-pawn-context)
Every customer email MUST include:
1. VP logo header (linked, with UTMs)
2. Per-store **Call AND Text** buttons (both showing the number on the button face)
3. Full 5-store directory at the bottom with Name + Address + Directions + Call + Text per row

### Rule 7 — Brand integrity (valley-pawn-context)
- All 5 stores are "Valley Pawn" — never use "Dixie Pawn" anywhere
- Canonical Maps URLs use `Valley+Pawn+City+VA`, never raw addresses
- No firearms/guns/weapons in social media content (Google/Meta policy)

### Rule 8 — Pipeline trigger discipline
- Drop trigger via `osascript` `do shell script` (Write tool can't reach the pipeline folder)
- Poll `results/<id>.result.json` for completion
- 0 rows is a legitimate result, not a failure — always check the row_count
- Watcher must be the foreground Windows app when its cells need to drive Bravo (Bravo must be foreground inside the VM)

### Rule 9 — Bravo gotchas (bravo-context)
- "Past Payment Due Date" filter LIES — use Custom Layaway Report instead
- "Loans To Expire" badge ≠ "75-Days-Past-Due" — measure against the saved report, not the badge
- Dismiss "Overdue Task Reminder" pop-up with "Remind Me Later" before any work
- Can't switch stores from inside a working view — Cancel out to Dashboard first
- Bravo is slow; clicks may take 1+ second to register

### Rule 10 — File and folder conventions
- Project work goes in `/Users/joshuadavis/Documents/Claude/Projects/<Project Name>/`
- Every project has a `STATUS.md` at its root (the living log)
- Outputs intended for sharing go to the user's workspace folder (the one they selected)
- Pipeline output is in `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/` — OUTSIDE the file-tool sandbox; reach via `osascript`
- Scheduled task SKILL.md files live in `/Users/joshuadavis/Documents/Claude/Scheduled/<task-name>/`

### Rule 11 — Social media publishing routes through Publer (2026-06-19+)
For all Facebook Page + brand IG publishing operations, use Publer's API (`https://app.publer.com/api/v1` with `Authorization: Bearer-API {key}` and `Publer-Workspace-Id: 6a358d48fe216c70f7e65d4e`). Do NOT use the direct Meta Graph API publishing path. The `facebook-post` skill and `tokens.json` System User token chain are deprecated for publishing. Content production (Midjourney + Canva + vp-content-batch) stays upstream and unchanged. Account ID map at `/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/publer_accounts.json`.


---

## Section 6 — Standard Project Lifecycle

The same 5 phases for any new business-management initiative, large or small.

### Phase 1 — Inventory (read-only, ~10 min)

1. Read this BUSINESS_OS.md (top to relevant domain section)
2. ls the relevant project folder if one exists
3. ls `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/` for overlapping data
4. Read project-specific STATUS.md if any
5. Search relevant Slack channel for recent posts on the topic

### Phase 2 — Propose ADDITIVE plan

Frame as: *"here's what we already have | here's the gap | here's what I'll add (no modifications to existing infrastructure)."*

Get explicit go-ahead on the additive plan before building anything.

### Phase 3 — Build (additive only)

For a Bravo-touching build:
1. New saved Ad Hoc report in Bravo (option: Claude drives via computer-use, ~3 min)
2. New AHK handler file (clone existing, rename functions/constants)
3. New pipeline cell name registered in `bravo_watcher.ahk` and `bravo_export.ahk` (ADD lines)
4. Restart watcher (run `restart_watcher.bat` inside VM)
5. Validate with a small probe trigger before the full run

For a Gusto/QBO/Brevo/eBay build:
1. New skill file or new scheduled task folder
2. Wire to MCP tools (don't reinvent — connectors exist)
3. Dry-run before scheduling

### Phase 4 — Run / verify

1. Drop the actual trigger (or run the script)
2. Poll results
3. Sanity-check output before sharing

### Phase 5 — Deliver

1. Outputs go to the user's selected workspace folder
2. Update the project STATUS.md
3. Update this BUSINESS_OS.md if the build adds new infrastructure
4. Provide `computer://` links to deliverables

---

## Section 7 — Data Flow Diagram

```mermaid
graph TD
    %% Upstream data sources
    Bravo[("Bravo POS<br/>5 stores in Windows VM")]
    Gusto[(Gusto<br/>Payroll & Time)]
    QBO[(QBO<br/>Books)]
    Brevo[(Brevo<br/>Email lists)]
    Chekkit[(Chekkit<br/>Reviews & SMS)]
    eBay[(eBay<br/>Online sales)]
    Gmail[(Gmail<br/>jdavis@fcfpawn.com)]
    GBP[(Google Business<br/>Profile)]
    Amazon[(Amazon Business<br/>Supplies)]
    DocuSign[(DocuSign<br/>Contracts)]
    GA[(Google Analytics)]
    GHome[(Google Home<br/>cameras)]
    CloudCover[(CloudCover<br/>cameras)]

    %% Pipeline as central nervous system
    Pipeline{{"Bravo Data Extraction<br/>Pipeline (AHK watcher)"}}
    Bravo --> Pipeline

    %% Outputs
    Slack[Slack Channels]
    GDrive[Valley Pawn Drive]
    Sheets[Google Sheets]

    %% Domain automations
    Pipeline -->|safe-register-journal| DailyFunds[daily-funds-verification]
    Pipeline -->|aged-inventory-summary| AgedInv[weekly-aged-inventory]
    Pipeline -->|employee-activity| EmpRank[weekly-employee-rankings]
    Pipeline -->|loans-75-days| LoanRev[weekly-loan-layaway-review]
    Pipeline -->|layaways| LoanRev
    Pipeline -->|fpd-cohort| FPDRank[weekly-fpd-ranking]
    Pipeline -->|company-kpis| StoreRank[monday-store-rankings]
    Pipeline -->|sales-by-vendor| NewInv[new-inv-weekly-report]
    Pipeline -->|chekkit-inactives| ChekkitReq[chekkit-weekly-review-requests]

    Gusto --> ClockIn[daily-clockin-check]
    Gusto --> Timekeeping[weekly-timekeeping-analysis]
    Gusto --> Payroll[weekly-payroll-to-qbo]
    Payroll --> QBO

    Brevo --> EmailCampaign[weekly-valley-pawn-email-campaign]
    Brevo --> GoldEmail[monthly-we-buy-gold-silver-email]
    ChekkitReq --> Brevo

    Chekkit --> ReviewAlerts[chekkit-new-review-alert]
    Chekkit --> ReviewResponses[nightly-chekkit-review-responses]
    Chekkit --> ReviewCounts[review-obtained-last-week]

    Gmail --> MMScan[mm-merchandisers-daily-scan]
    MMScan --> NewInvIntake[new-inv-intake]
    Gmail --> DistMonitor[distributor-setup-monitor]
    Gmail --> SupplyOrder[daily-supply-order]
    SupplyOrder --> SupplyCheckout[tuesday-supply-checkout]
    SupplyCheckout --> Amazon

    GA --> WeeklyAnalytics[weekly-analytics-summary]
    GHome --> DressCode[daily-dress-code-check]
    CloudCover --> CloudCheck[daily-cloudcover-check]
    GBP --> DirMonitor[brightlocal-weekly-sync]

    DocuSign --> BaldRock[bald-rock-15-day-contract]

    %% Outputs to humans
    DailyFunds --> Slack
    AgedInv --> Slack
    AgedInv --> GDrive
    EmpRank --> Slack
    EmpRank --> Sheets
    LoanRev --> Slack
    LoanRev --> GDrive
    FPDRank --> Slack
    StoreRank --> Slack
    StoreRank --> Sheets
    EmailCampaign --> Customers((Customers))
    GoldEmail --> Customers
    ReviewAlerts --> Slack
    ReviewResponses --> Customers
    ClockIn --> Slack
    Timekeeping --> Slack
    Payroll --> Slack
    WeeklyAnalytics --> Slack
    DressCode --> Slack
    CloudCheck --> Slack
    DirMonitor --> Slack
    BaldRock --> Guests((Guests))
    NewInvIntake --> Slack
    NewInvIntake --> Bravo
```

**Blast-radius cheat sheet:**

- **Bravo Data Extraction pipeline goes down** → 12 scheduled tasks degrade or fail. Restart `bravo_watcher.ahk` in VM.
- **Bravo store-cycle UIA breaks** → multi-store pipeline cells fail; single-store still works.
- **Gusto login token expires** → Chrome-based Gusto tasks degrade (weekly-timekeeping-analysis, weekly-payroll-to-qbo, onboard/dismiss-employee). _daily-clockin-check no longer affected — moved to MCP-first 2026-06-10; Chrome is fallback only._
- **Slack down** → most reports queue messages; Brevo/customer-facing flows unaffected.
- **Chrome MCP extension disconnected** → most web-driving tasks pause (GA, Gusto Time, eBay, BrightLocal).
- **Modifying any existing saved Bravo report** → unknown chain of downstream task breakage. ALWAYS additive.

---

## Section 8 — Gap Analysis (highest-value opportunities)

Cross-referenced from each domain. Roughly ranked by business impact × low effort.

### High-impact, ready-to-build now
1. **Loan portfolio true-ROI by category** (Domain 6) — current Optimize Loan Portfolio project. Path is clear: new saved Bravo report + new handler + new cell.
2. **Cross-store anomaly alerts** (Domain 1) — drift detection on key metrics (safe count, loan balance, sales). Pipeline data already exists; build a rolling-average comparator.
3. **Monthly email performance digest** (Domain 4) — Brevo has the data; no automation pulls it. ~1 hour to build.
4. **Vendor performance scorecard** (Domain 5) — pull new-inventory tracker + Bravo sell-through; rank vendors by margin × lead time. ~2 hours.

### Medium-impact, modest build
5. **Customer-tier segmentation** (Domain 6, deferred from current project) — A/B/C/D tiers by redemption history. Useful for marketing AND loan decisions.
6. **Real-time P&L dashboard** (Domain 3) — QBO data is there; assemble a weekly snapshot.
7. **eBay listing-health audit** (Domain 7) — find stale or mispriced listings.
8. **SEO position tracker** (Domain 4) — weekly rank check for key terms.

### Lower-priority, larger build
9. **Customer NPS / satisfaction pulse** (Domain 4) — post-loan survey
10. **Maintenance issue tracker for Bald Rock** (Domain 8)
11. **Pricing-optimization layer for Bald Rock** (Domain 8) — comp-rental scrape

### Cleanup / hygiene
12. **Resolve duplicate scheduled tasks** — several B-status tasks look like older variants of newer A-status tasks (`weekly-aged-inventory-review` vs `weekly-aged-inventory-report`; `bald-rock-auto-contract` vs `bald-rock-15-day-contract`). Quick audit + delete the old.
13. **Capture SSRS URL for `company-kpis`** — unblocks `monday-store-rankings` becoming pipeline-driven (currently requires Parallels).
14. **Finish `chekkit-inactives` row-walk** — unblocks pipeline-driven `chekkit-weekly-review-requests`.
15. **Build per-store saved Ad Hoc for `fpd-cohort`** — ~15 min × 5 stores = 75 min once.

---

## Section 9 — Active Backlog (prioritized)

Current build order, subject to Joshua's redirects.

| # | Build | Domain | Effort | Status |
|---|---|---|---|---|
| 1 | Optimize Loan Portfolio: new saved Bravo report + handler + cell + analysis | Loans | 2–4 hr | **IN PROGRESS** (paused for this OS build) |
| 2 | Monthly email performance digest | Marketing | 1 hr | Queued |
| 3 | Vendor performance scorecard | Inventory | 2 hr | Queued |
| 4 | Cross-store anomaly alerts | Operations | 3 hr | Queued |
| 5 | Cleanup pass — delete superseded scheduled tasks | Hygiene | 30 min | Queued |
| 6 | Capture SSRS URL → make `monday-store-rankings` pipeline-driven | Pipeline | 30 min | Queued |
| 7 | Finish `fpd-cohort` per-store saved reports | Loans | 75 min | Queued |
| 8 | Customer-tier segmentation | Loans + Marketing | 4 hr | Backlog |
| 9 | eBay listing-health audit | Online Sales | 3 hr | Backlog |
| 10 | Real-time P&L weekly snapshot | Finance | 4 hr | Backlog |

---

## Section 10 — Active Project Folders

`/Users/joshuadavis/Documents/Claude/Projects/`

| Folder | Purpose | Active? |
|---|---|---|
| `Bravo Data Extraction` | The pipeline itself | **CRITICAL — never modify casually** |
| `Daily Funds Verification` | Companion docs for daily-funds-verification | A |
| `Deep KPI analysis` | Earlier KPI work | Reference |
| `Landscape design` | Personal/Salt Run? | — |
| `Monday Morning Review` | Manual Monday review notes | Reference |
| `New Inventory Procurement` | New-inv project | Reference |
| `Optimize Loan Portfolio` | **CURRENT PROJECT** — STATUS.md inside | **A** |
| `Quickbooks Set UP` | QBO setup history | Reference |
| `Short Term Rental Optimization` | Bald Rock STR project | Reference |
| `Valley Pawn OS` | **THIS document** — created 2026-05-20 | **A** |

---

## Section 11 — Change Log

| Date | Change | Reason |
|---|---|---|
| 2026-05-20 | Initial creation | Joshua: "we are building a complete business management workflow... what's the best plan to look at all of this holistically" |
| 2026-06-19 | Added Publer Business tier ($50/mo) as the publishing layer for all FB Pages + brand IG. Deprecated direct Graph API publishing (token wall + sub-portfolio block). Added Rule 11. Marked B-status social tasks for additive Publer-routed replacement. | Token wall + sub-portfolio ownership issue made direct Graph API publishing structurally unworkable; Publer's OAuth bypassed both. |
| 2026-06-29 | Added Section 13 (Tooling, Connectors & Capability Inventory) + Rule 0 (MCP-first) + Section 12 end-of-session update ritual. Staged `SKILL_DELTA_2026-06-29.md` for the `enterprise-map` + `valley-pawn-context` skill edits Joshua applies in Settings. | Joshua: keep the enterprise map + skills current with what tools/skills/connectors each session already has, so sessions stop re-explaining and can keep building efficiently. Board recommendation: one source of truth (BUSINESS_OS.md) + live-truth queries, not per-skill duplication. |
| 2026-06-29 | Created `monthly-capability-drift-audit` scheduled task (1st of month, 7am → `#claude-notifications`) to keep Section 13 self-maintaining. | Make the capability inventory update itself instead of relying on each session to remember. |
| 2026-07-01 | Monthly capability drift audit run. Registered ~30 new scheduled tasks (see 2026-07-01 addendum) that had shipped since 2026-05-20 (58 → 77 tasks live). Flagged 8 previously-active tasks now showing `enabled:false` (incl. `weekly-payroll-to-qbo`, `weekly-valley-pawn-email-campaign`) for Joshua. Plugins (16) + Section-13 connector snapshot in sync. No skill delta required. | Scheduled `monthly-capability-drift-audit`, autonomous run. |

---

## Section 12 — How To Update This Document

When something ships or a constraint changes:

1. **New scheduled task / skill / pipeline cell** → add to the matching Domain section's table (Section 2)
2. **New saved Bravo report** → add to Section 4 handlers table
3. **New Operating Rule** → add to Section 5 with numbered rule
4. **New project folder** → add to Section 10
5. **Gap filled** → strike through the gap line in the relevant domain; consider adding to Change Log
6. **Backlog reordered** → update Section 9

7. **New MCP connector / plugin / skill becomes available** → add to Section 13 (Tooling &
   Capability Inventory). This is the "stop re-explaining what we have access to" step.

**End-of-session update ritual (do this before you wrap any build/fix session):**
1. Did this session add or change infrastructure (task, skill, pipeline cell, report, connector,
   plugin, folder, rule)? If yes → register it the same session (Rule 14).
2. BUSINESS_OS.md is editable from any session that has the `Valley Pawn OS` folder connected —
   edit it directly and additively (never delete others' entries).
3. **Skill files are NOT editable from a session** (read-only cache). When a *skill* needs new
   facts, stage a `*_DELTA_<date>.md` patch file in the `Valley Pawn OS` folder and tell Joshua to
   apply it in **Settings → Capabilities**. (Pattern already used: `VALLEY_PAWN_CONTEXT_DELTA_2026-06-22.md`.)
4. Add a one-line Change Log row (Section 11).

**Where this doc lives:**
- Canonical: `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/BUSINESS_OS.md`
- Future: consider also referencing from `valley-pawn-context` skill so it's auto-loaded every session

---


---

## 2026-06-19 ADDENDUM — Social Media Stack Expansion

_Applied automatically by Claude per Joshua directive 2026-06-19. Source: /Refine Social Media/BUSINESS_OS_REGISTRATION_DELTA.md_

# BUSINESS_OS.md — Registration Delta (2026-06-19)

This file is an **additive patch** to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/BUSINESS_OS.md`. It registers every new domain, account, platform, script, file, and skill that landed during the 2026-06-19 social media build, per the enterprise-map rule (Joshua's directive).

**How to apply:** copy each section below into the corresponding section of BUSINESS_OS.md. All additions are additive — no existing entries are removed or modified (Rule #4).

---

## 1. New external domains / URLs to register

| Domain / URL | Purpose | Status | Owner | Notes |
|---|---|---|---|---|
| `follow.thevalleypawn.com` | Branded subdomain for Publer Linkie page (in-store QR card destination) | Planned (DNS task #48) | Valley Pawn | CNAME → Publer Linkie host (look up in Publer Linkie settings once page is built) |
| `x.com/valleypawnva` | Brand X (Twitter) account — display name "Joshua Davis," handle @valleypawnva, intentional conservative-demographic strategy | Live (logo + bio + first post live 2026-06-19) | Joshua | Posts as Joshua, not as a brand handle |
| `instagram.com/valley_pawn` | Brand Instagram account | Live (logo swapped 2026-06-19 from V-mark to full landscape) | Joshua | |
| `tiktok.com/@thevalleypawn` | Brand TikTok account (Phase 2 reel pipeline target) | Live (logo set 2026-06-19) | Joshua | Live-selling planned per giveaway-strategy memory |

## 2. New software platforms registered

| Platform | Role | Tier / Cost | Auth | Replaces |
|---|---|---|---|---|
| **Publer** | Social media publishing layer (all 9 accounts) + analytics + Linkie (Link-in-Bio) | Business tier, $50/mo (all pages included) | Bearer-API token in `publer_config.json` | Direct Meta Graph API path (now LEGACY); `facebook-post` skill (now LEGACY); 8 disabled scheduled tasks (now LEGACY — see vp-social-publisher SKILL) |
| **Publer Linkie** | One-page "follow Valley Pawn everywhere" hub at follow.thevalleypawn.com | Included in Publer Business | Same as Publer | New capability — no prior tool |

## 3. New connected social accounts (Publer workspace `6a358d48fe216c70f7e65d4e`)

All 9 accounts mapped in `publer_accounts.json`:

- **Brand FB** (`6a3596d6fe216c70f7e6726c`) — Valley Pawn brand Page
- **BrandIG** (`6a35979ebbd130d6e889c0bb`) — @valley_pawn
- **BrandTikTok** (`6a359ca0bbd130d6e889cb78`) — @thevalleypawn ⬅ NEW 2026-06-19
- **BrandTwitter** (`6a359c454dd914c27c77f9c5`) — @valleypawnva ⬅ NEW 2026-06-19
- **Culpeper** (`6a3596d3fe216c70f7e67261`)
- **Harrisonburg** (`6a3596d807e1b3bf83f1c379`)
- **Lexington** (`6a3596d4fe216c70f7e67266`)
- **Roanoke** (`6a3596d2bbd130d6e889bf58`)
- **Waynesboro** (`6a3596d789dea67771497918`)

## 4. New scripts / Python modules (in `/Refine Social Media/`)

| File | Role | Depends on |
|---|---|---|
| `publer_client.py` | Single source of truth for ALL Publer API calls. Bulk/networks payload structure (per Publer API docs). Includes `schedule_post`, `job_status`, `wait_for_job`, `post_insights` | `publer_config.json`, `publer_accounts.json`, `requests` |
| `vp_social_publisher.py` | Manifest executor — reads approved-manifest JSON, routes items to correct accounts via routing tier, calls Publer API hands-off | `publer_client.py` |
| `friday_close_engagement_publer.py` | Publer-routed engagement analytics for Friday close (replaces direct Meta Graph API path) | `publer_client.py` |
| `friday_close_engagement.py` | LEGACY — direct Meta Graph API version. Preserved as fallback. Not actively called. | — |

## 5. New skills / planned skill files

| Skill | Location | Status |
|---|---|---|
| `vp-social-publisher` | `/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media/vp-social-publisher_SKILL.md` | Drafted 2026-06-19. **Joshua: add this to Settings → Capabilities so it becomes a real skill.** Currently lives as a stub file. |
| `vp-brand-studio` | Existing | Needs additive update with X + TikTok voice notes (task #36) — Joshua to edit in Settings |
| `expert-review-board` | Existing | Needs PERMANENT seat: "Pawn shop executive/operator" on every Valley Pawn board (rule saved to memory, but skill file needs Joshua to add in Settings) |
| `valley-pawn-context` | Existing | Should reference the new X / IG / TikTok handles + Publer as publishing layer + $100/mo giveaway program |

## 6. New folder structure (`/Refine Social Media/`)

```
Refine Social Media/
├── brand_assets/                              # 2026-06-19 — for X/IG/TikTok profile setup
│   ├── valley_pawn_profile_1080.png           # 1080×1080 square logo (X/IG/TT profile)
│   └── valley_pawn_x_header_1500x500.png      # X header banner
├── Meta Business Verification/                # 2026-05-26 — for Meta business verification submission
├── publer_config.json                          # API auth + workspace_id
├── publer_accounts.json                        # store_key → Publer ID mapping (9 accounts)
├── publer_client.py                            # Publer API client (bulk/networks payload)
├── vp_social_publisher.py                      # Manifest executor
├── vp-social-publisher_SKILL.md                # Stub skill — install via Settings
├── friday_close_engagement.py                  # LEGACY direct-Meta
├── friday_close_engagement_publer.py           # Publer-routed engagement analytics
├── BUSINESS_OS_REGISTRATION_DELTA.md           # THIS FILE — additive patch for BUSINESS_OS.md
├── REFINE_SOCIAL_MEDIA_INDEX.md                # Folder index for future Claude sessions
└── (various playbook + report markdown files)
```

## 7. New scheduled tasks (planned, additive)

| Task | Cadence | Purpose | Status |
|---|---|---|---|
| `vp-content-batch-weekly` | Sun 8 PM | Generate weekly content + auto-publish via vp_social_publisher.py + Publer | Existing — needs verification it fires hands-off (task #45) |
| `vp-giveaway-monthly-draw` | Last day of each month | Draw random row from Brevo entries list, email winner, generate announcement post | NEW — to build (task #47) |
| `reel-comment-alert` | Trigger: 30 min after Meta post publish | DM Joshua + Lainie with comment digest + draft replies | Existing — keep using |

## 8. Strategic rules added (2026-06-19)

- **Rule 11** (existing): Social media publishing routes through Publer.
- **Rule 12** (NEW): Every expert-review-board panel for Valley Pawn must seat a pawn shop executive/operator as a permanent member.
- **Rule 13** (NEW): Social media adoption incentive is a $100/month giveaway with email-capture entry, not per-transaction discount. VA-compliant Official Rules required.
- **Rule 14** (NEW): All NEW domains, accounts, platforms, scripts, and folders must be registered additively in BUSINESS_OS.md the same session they're created.

## 9. Change log entry

```
2026-06-19 — Social media stack expansion + adoption infrastructure
  - Connected X @valleypawnva, TikTok @thevalleypawn to Publer workspace
  - Replaced direct Meta Graph API path with Publer (vp_social_publisher.py + publer_client.py)
  - Fixed Publer API payload (bulk/networks structure per Publer docs)
  - Set brand identity (logo + header + bio) on X, IG, TikTok
  - First X test post published successfully via Publer UI
  - Pawn shop operator added as permanent board seat (rule #12)
  - $100/month giveaway model adopted (rule #13)
  - Planned: follow.thevalleypawn.com subdomain → Publer Linkie page
  - Planned: in-store QR counter cards (5 stores, Amazon premade ~$50)
  - Deprecated 6 Meta-direct-API tasks (now obsolete via Publer)
```

---


---

## 2026-06-19 ADDENDUM 2 — WordPress + Plan Upgrade

**New account added:** BrandBlog (Valley Pawn WordPress.com site at thevalleypawn.com)
- Publer ID: 6a393e159231ae095ada7b6a
- Provider: wordpress_oauth → posts as `wordpress` network in Publer API

**Plan change:** Publer Business tier upgraded from 9-account ($50/mo) to 10-account ($63/mo). Joshua: $13/mo upgrade to keep all stores in hands-off auto-publish while adding the SEO compound channel. Free trial in effect at upgrade time.

**Routing update (vp_social_publisher.py):**
- `brand` tier now fans out to: Brand FB + BrandIG + BrandTwitter + BrandBlog (4 channels, was 2)
- `fan-out` tier now includes BrandTwitter alongside existing 7 channels
- `BrandBlog` NOT in fan-out (SEO quality > quantity, blog stays cornerstone-only)
- `BrandTikTok` still excluded from both tiers (video-first, awaits vp-reel-pipeline)

**New rule:** Default to upgrade tier over channel drop when SaaS automation hits its limit ([[feedback-dont-cheap-out-on-automation-slots]] memory).

---


---

## 2026-06-22 ADDENDUM 3 — Linkie + DNS Setup

**6 Linkie pages built** (linkie.bio):
- /valley_pawn (BRAND master, 7 links: FB + IG + X + TikTok + YouTube + Website + Blog)
- /valleypawn_lexington (1 link: Lexington FB)
- /valleypawn_roanoke (1 link: Roanoke FB)
- /valleypawn_harrisonburg (1 link: Harrisonburg FB)
- /valleypawn_waynesboro (1 link: Waynesboro FB)
- /valleypawn_culpeper (1 link: Culpeper FB)

**DNS CNAME added in WordPress.com:**
- follow.thevalleypawn.com → app.linkie.bio
- Verified live via dig + 8.8.8.8

**Outstanding:** custom domain registration on Linkies side (may need Linkie paid plan). Until done, QR cards work via linkie.bio/... direct URLs.

**6 counter card PDFs** generated at /Refine Social Media/counter_cards/ ready to print on 5x7 cardstock.

---


---

## 2026-06-22 ADDENDUM 4 — PERMANENT Landing-Page Architecture (Option D)

After board review (pawn-shop seat + web-infra seat), the QR-destination architecture was upgraded from Linkie-hosted to **self-hosted on thevalleypawn.com**. This is the permanent solution. Linkie pages stay as the secondary tier.

**PRIMARY landing pages (thevalleypawn.com WordPress):**
- thevalleypawn.com/follow — brand master (all-locations)
- thevalleypawn.com/lexington
- thevalleypawn.com/roanoke
- thevalleypawn.com/harrisonburg
- thevalleypawn.com/waynesboro
- thevalleypawn.com/culpeper

Built via WP REST API in one batch (POST /wp-json/wp/v2/pages, page IDs 748–753). Each page has: Valley Pawn header, family-owned tagline, $100/month giveaway callout, email-capture placeholder (Brevo embed TBD), large store-specific FB CTA, social buttons row (IG/X/TikTok/YouTube), website link, and Find Another Store footer.

**SECONDARY tier (linkie.bio — fallback + IG bio link):**
- linkie.bio/valley_pawn (brand master, 7 social links)
- linkie.bio/valleypawn_lexington (and 4 more store Linkies, 1 FB link each)

**DNS:**
- thevalleypawn.com → existing WP A record
- follow.thevalleypawn.com → CNAME app.linkie.bio (fallback / IG bio link path; Linkie custom-domain setup pending)

**Counter card QR codes** now encode thevalleypawn.com/{store} URLs (regenerated 2026-06-22).

**Why this is permanent (per board):** (1) $0 ongoing cost — uses owned infra; (2) zero third-party dependency on primary path; (3) every visit builds thevalleypawn.com SEO; (4) full marketing flexibility (A/B tests, seasonal promos, inline deals); (5) editable by Joshua/Lainie in WordPress.

**Rule 15 (NEW):** Owned-infrastructure paths beat rented SaaS paths for any customer-facing destination that needs to last >1 year. The default is build-on-WordPress, not rent-on-Linktree-clone.

---


---

## 2026-06-22 ADDENDUM 5 — Brevo Giveaway Form + WP embed

**Brevo signup form created:**
- Name: $100 Monthly Giveaway Entry
- Form ID: 6a396f870ded3d8920b69c63
- Contact list (new): Giveaway Entries (Your First Folder)
- Confirmation: No confirmation email (instant entry, lowest friction)
- Success message: Youre entered! Winners are drawn the last day of each month — check your email.
- Share URL: https://7e2d5125.sibforms.com/serve/MUIFAO...

**Embedded on all 6 WP landing pages** (IDs 748–753) via WP REST API PUT — replaced the placeholder div with Brevo iframe. Verified rendering live on /lexington.

**Monthly draw flow now end-to-end:**
1. Customer scans store QR card → lands at thevalleypawn.com/{store}
2. Drops email in Brevo form → enters Giveaway Entries list
3. Last day of month: giveaway_monthly_draw.py pulls list, picks winner, generates announcement
4. vp_social_publisher.py publishes winner post across FB / IG / X / WordPress (brand routing tier)
5. Next month resets — entries from new period only

---


---

## 2026-06-22 ADDENDUM 6 — Public-Facing Audit + Architecture Cleanup

**Scope:** First comprehensive audit of all public-facing surfaces (Big-5 directories + socials + WordPress + Brevo + eBay) against the canonical NAP in valley-pawn-context. Triggered by Joshua's "have we done a full review of all our pages to make sure information and branding is correct on all, all channels?"

### Audit checked and findings

**✅ Clean across the board:**
- Google Knowledge Panels — all 5 stores: name, address, phone, hours (6PM close), website — correct
- WordPress location pages (Lexington, Roanoke, Harrisonburg, Waynesboro, Culpeper) — all 5 phones correct, no Dixie Pawn references, full 5-store directory present
- Instagram @valley_pawn — bio + link clean
- TikTok @thevalleypawn — bio matches brand voice ("Virginia's modern pawn shop. Fair deals + 30-day warranty. Family-owned since 2014.")
- X @valleypawnva — display name "Valley Pawn" (the recent Joshua-name rename stuck)
- Roanoke "Suite C" — confirmed present on Google Knowledge Panel

**⚠️ Drift / chronic issues surfaced:**
1. **Bing Harrisonburg** still shows "Dixie Pawn, Inc - Harrisonburg Va" alongside Valley Pawn. Chronic per directory-listing-monitor skill — needs Bing Places admin push.
2. **MapQuest Lexington** shows stale "439 East Nelson St" in secondary search results (aggregator drift; Google's actual GBP is correct at 125 Walker St).
3. **brightlocal-weekly-sync-alerts-check** scheduled task is currently DISABLED (enabled: false). This is why drift went undetected weekly.

### Fixes shipped in this session

1. **follow.thevalleypawn.com SSL error → FIXED.** Deleted the broken `CNAME follow → app.linkie.bio` record in WordPress.com DNS. Subdomain now returns NXDOMAIN cleanly instead of an `ERR_SSL_VERSION_OR_CIPHER_MISMATCH` browser warning. No customer-facing path is affected:
   - Counter card QR codes point to `thevalleypawn.com/{store}` (primary)
   - IG bio link points to `thevalleypawn.com` (root)
   - Per Addendum 4 the architecture had already migrated to self-hosted primary
2. **Harrisonburg "Ste 22" truth resolved.** Joshua confirmed: 1790 East Market Street, **Ste 22**. Google + WordPress JSON-LD both already showed Ste 22; canonical NAP in valley-pawn-context skill did NOT. Delta patch staged at `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/VALLEY_PAWN_CONTEXT_DELTA_2026-06-22.md` for Joshua to apply via Settings → Capabilities.

### Outstanding from this audit (carries forward)

- **Bing Harrisonburg "Dixie Pawn" push** — needs Bing Places admin OR BrightLocal session push. Tracked in Tasks.
- **BrightLocal session** — Joshua's active session is on a separate Chrome window not visible to the MCP. Pending: Joshua moves the session into the MCP-driven tab OR signs in once for me to drive multi-directory analysis.
- **Apple Maps, Yelp deep-checks** — anti-bot blocks on curl; require Chrome browser session for full inspection. Top-5 audit deferred to BrightLocal completion.
- **eBay store audit** — not yet checked.
- **Brevo email templates** — not yet audited; require login.
- **YouTube channel** — not yet checked.

### Re-enable consideration (decision held until BrightLocal session is in)

The `brightlocal-weekly-sync-alerts-check` task is currently disabled (B status per BUSINESS_OS Section 2 Domain 4). After today's BrightLocal-driven audit completes, the expert review board should weigh re-enabling — likely needs a session-refresh shim built first since BrightLocal sessions expire and the task hasn't run in weeks.

### Rule 16 (NEW)

**Subdomain deletions are safer than broken-SSL subdomains** when no customer-facing path depends on them. An NXDOMAIN ("Server not found") is a cleaner failure than `ERR_SSL_VERSION_OR_CIPHER_MISMATCH` (which trains customers to bypass security warnings). Before keeping a subdomain CNAME, verify (a) the destination resolves cleanly with valid SSL and (b) something owned and customer-facing actually depends on it.

---

## Section 13 — Tooling, Connectors & Capability Inventory (2026-06-29)

> **Why this section exists.** A fresh session does not automatically know which tools, MCP
> connectors, plugins, and skills are already wired up. Without this, every session re-discovers
> (or re-asks) the same thing. This is the durable answer to *"what do I already have access to?"*
> Treat it as a **thin, stable snapshot** — the volatile detail lives behind the live queries at
> the bottom. When this list and a live query disagree, **the live query wins.**

### Rule 0 — MCP-first (carries Joshua's global instruction)
Always reach for a **native MCP connector** before Chrome, computer-use, or osascript. Order of
preference for any task: **(1) dedicated MCP connector → (2) Claude-in-Chrome (web app, no MCP) →
(3) computer-use / osascript (native desktop, Bravo pipeline folder).** Only drop to a lower tier
when the tier above genuinely can't do it. *(This is why `daily-clockin-check` moved Gusto-MCP-first
on 2026-06-10 and why `weekly-timekeeping-analysis` is a migration candidate — see Domain 2.)*

### A. Native MCP connectors (business data — use these first)
| Connector | Use it for | Notes |
|---|---|---|
| **Slack** | All channel posts, DMs, search, canvases | Every automation reports here; primary human-facing output |
| **Gmail** | Read/search threads, drafts, labels (jdavis@fcfpawn.com) | MM-scan, distributor monitor, supply requests all read Gmail |
| **Google Calendar** | Events, scheduling | |
| **Google Drive** | Read/write/search Drive files, Sheets exports | Reports + minutes land here |
| **Gusto** | Employees, payroll, time records, comp | MCP returns real-time shift data now (the old "empty" caveat is gone) |
| **DocuSign** | Envelopes, templates, agreements | Bald Rock contracts; `send-guest-contract` |
| **Canva** | Designs, brand templates, export | Asset wrap stage (`vp-asset-compose`) |
| **QuickBooks Online** | Books, P&L, categorization | ⚠️ TWO accounts — `zapvp1@me.com` is READ-ONLY (Rule 5) |
| **Brevo** | Email lists, campaigns, signup forms | Giveaway form `6a396f870ded3d8920b69c63` |
| **WordPress.com** | thevalleypawn.com pages/blog (REST) | Landing pages 748–753, blog publisher |
| **eBay** | Online-sales listings, orders | |
| **Indeed** | Job posts, candidate/resume data | Hiring |
| **GoDaddy** | Domain availability/registration | |
| **Tax (Aiwyn / Column)** | Tax calc, jurisdictions, return PDFs | Quarterly/EOY prep handoff |
| **Reviews/Reputation** | Category + overall review summaries, action plans | Reputation analytics |
| **Travel** (Kiwi.com, lastminute.com) | Flights / hotel packages | Personal/ad-hoc |
| **MCP Registry** | Discover + suggest new connectors | Use when a task implies an app we may not have yet |

### B. Local / desktop control MCPs
**Control your Mac** (`osascript` — required for the Bravo pipeline folder, which is outside the
sandbox) · **Claude in Chrome** (web apps via saved passwords — never ask Joshua to log in, Rule 2)
· **computer-use** (native-app desktop control) · **scheduled-tasks** (`mcp__scheduled-tasks__*`) ·
**pdf-viewer** · plus local app bridges seen this session: **Apple Notes**, **iMessage**, **Word**.

### C. Installed plugin marketplaces (skill bundles available via the Skill tool)
| Plugin | What it adds | VP relevance |
|---|---|---|
| **anthropic-skills** | The custom Valley Pawn OS bundle (all `vp-*`, `bravo-*`, `qbo-*`, loan/inventory/property skills + `enterprise-map`, `expert-review-board`) | **Core — this is our business** |
| **small-business** | Cash-flow, invoice-chase, month-end, payroll plan, tax, campaigns | **High — built for SMBs like VP** |
| **finance** | Close mgmt, reconciliation, journal entries, financial statements, variance | High — pairs with QBO work |
| **marketing** | Campaign plan, content, SEO audit, brand review, email sequences | High — pairs with Brevo/Publer |
| **legal** | Contract review, NDA triage, compliance check, signature routing | Medium — vendor/lease contracts |
| **operations** | Runbooks, process docs, risk register, vendor review, status reports | Medium — SOPs for the 5 stores |
| **productivity** | Memory management, task tracking | Medium |
| **customer-support** | Ticket triage, escalation, KB articles, response drafting | Medium |
| **sales / zoominfo / vpai** | Pipeline, forecasting, prospecting, B2B contact data | Low for retail pawn; situational |
| **product-management** | PRD/spec, roadmap, sprint planning | Low |
| **twilio-developer-kit** | SMS/voice/WhatsApp build kit | Future — customer comms |
| **slack-by-salesforce** | Channel digests, search, announcements | Utility |
| **pdf-viewer** | Interactive view / annotate / sign / fill | Utility |
| **cowork-plugin-management** | Build/customize new plugins | Meta |

Document creation skills (always available): **docx, xlsx, pptx, pdf**.

### D. Live-truth queries (run these instead of trusting the snapshot above)
- **Skills:** `mcp__skills__list_skills` — what's installed right now
- **Plugins:** `mcp__plugins__list_plugins` — installed marketplaces
- **Scheduled tasks:** `mcp__scheduled-tasks__list_scheduled_tasks` — the real cadence + enabled state (the authority; ~per Section 2 but verify live)
- **New connectors:** `mcp__mcp-registry__search_mcp_registry` — when a task needs an app we may not have
- **Deferred tools:** the session's tool registry surfaces connector tools by ID; load with `ToolSearch` before calling

### E. What this section deliberately does NOT freeze
Connector tool *names/IDs*, exact scheduled-task counts, and per-plugin skill lists drift fast.
This section records the **stable facts** (which connectors are authorized, the MCP-first order,
which plugins are installed and how relevant they are). For anything volatile, run a query in D.

---

## 2026-07-01 ADDENDUM 7 — Monthly Capability Drift Audit

_Autonomous run of `monthly-capability-drift-audit`. Additive registration of infrastructure that shipped since the last full map. No existing rows modified; nothing removed._

**Live counts (2026-07-01):**
- **Scheduled tasks:** 77 total (~35 enabled / ~42 disabled). Up from 58 documented on 2026-05-20.
- **Installed plugin marketplaces:** 16 — matches Section 13.C exactly (anthropic-skills, small-business, finance, marketing, legal, operations, productivity, customer-support, sales, zoominfo, vpai, product-management, twilio-developer-kit, slack-by-salesforce, pdf-viewer, cowork-plugin-management). **No change.**
- **Connectors:** Section 13.A stable-fact snapshot still accurate (Slack, Gmail, GCal, GDrive, Gusto, DocuSign, Canva, Indeed, GoDaddy, Tax, Reviews/Reputation, Travel, MCP Registry all live this run). QBO / Brevo / WordPress / eBay were not surfaced as native MCP tools in this headless run — **retained, not removed** (likely driven via web-app/REST skills rather than a native MCP, or simply not authorized in this session). Verify next run before treating as drift.

### NEW scheduled tasks (live but not in Section 2 / prior addenda) — registered here

| Task | State | Cadence | Likely domain |
|---|---|---|---|
| `vp-weekly-spot-price-update` | enabled | Daily 4:09am | Marketing/Inventory (metals pricing) |
| `bald-rock-monday-briefing` | enabled | Mon 4:09am | Property |
| `bald-rock-guest-reviews` | enabled | Daily 11am | Property — **fills the Domain 8 guest-review-monitoring gap** |
| `fb-token-health-check-daily` | enabled | Daily 3:10am | Marketing (Meta token watchdog) |
| `email-analytics-weekly` | enabled | Fri 3:04am | Marketing — **fills the "monthly email performance digest" gap** |
| `asset-recovery-daily-refresh` | enabled | Daily 7:17pm | Ops/Loans |
| `vp-website-trend-daily-refresh` | enabled | Daily 2:40am | Marketing/Web |
| `vp-website-deals-weekly` | enabled | Mon 1:05pm | Marketing/Web |
| `weekly-website-kpi-artifact-refresh` | enabled | Mon 3:35am | Marketing/Web |
| `vp-deal-of-week-monday-prompt` | enabled | Mon 8:01am | Marketing |
| `vp-deal-of-week-monday-pick` | enabled | Mon 12:33pm | Marketing |
| `vp-dashboard-refresh` | enabled | Daily 8:15am & 7pm | Ops (dashboard) |
| `funds-verification-watchdog` | enabled | Daily 6:47pm | Finance — watchdog on `daily-funds-verification` |
| `daily-intake-margin` | enabled | Daily 7:34am | Inventory (buy-margin) |
| `daily-intake-prestage` | enabled | Daily 6:36am | Inventory (prestage) |
| `daily-items-to-price` | enabled | Daily 8:05am | Inventory (pricing queue) |
| `monthly-analytics-prestage` | enabled | Days 28–31 8pm | Ops |
| `monthly-analytics-watchdog` | enabled | 1st 7am | Ops |
| `nightly-desktop-cleanup` | enabled | Daily 3:09am | Infra hygiene |
| `daily-ffl-transfer-check` | enabled | Daily 8:03am | Compliance (FFL) |
| `ffl-web-form-to-slack` | enabled | Every 15 min | Compliance (FFL) |
| `bravo-health-watchdog` | enabled | Daily 5am & 5pm | Pipeline health |
| `blog-publisher-watchdog` | enabled | Mon/Thu 2pm | Marketing (blog watchdog) |
| `monday-bravo-postcheck` | enabled | Mon 8:22am | Pipeline (Monday run postcheck) |
| `monthly-amazon-store-allocation` | enabled | 6th 9am | Inventory/Procurement |
| `vp-ai-search-health-check` | enabled | Mon 8:09am | Marketing (AI/LLM visibility) |
| `vp-ai-visibility-metrics` | enabled | Fri 9am | Marketing (AI/LLM visibility) |
| `vsp-nics-fee-monthly-check` | enabled | 5th 9am | Compliance (NICS) |
| `sunday-checklist-summary` | enabled | Sun 8:08pm | Ops |
| `oura-daily-import` | enabled | Daily 8:08am | Personal (Oura ring) |
| `zoom-phone-activation-check` | enabled | one-time 7/1 | Infra |
| `vp-content-batch-weekly` | enabled | Mon 2am | Marketing (was "planned" in Addendum 7-prev; confirmed live) |
| `weekly-loan-portfolio-refresh` | disabled | Mon 3:10am | Loans (Optimize Loan Portfolio project) |
| `chekkit-watcher-heal` | disabled | Every 12 min | Marketing (Chekkit watcher self-heal) |
| `nics-selector-autofix` | disabled | Every 15 min | Compliance (NICS UI autofix) |
| `scheduled-task-history-logger` | disabled | Every 15 min | Infra/observability |
| one-time build/smoke tasks | disabled | — | `loan-portfolio-final-pass-2026-05-21`, `overnight-closing-reports-smoke-2026-05-29`, `monday-bravo-combined-compile`, `srj-watcher-restart-oneshot-2026-06-08`, `itp-validate-restart-2026-06-09`, `gusto-qbo-first-sync-check`, `model-check-temp`, `winback-build-and-schedule-2026-06-17`, `postmaster-reputation-check-2026-06-23` (spent one-shots; kept for history) |

### ⚠️ State flips to review (documented as ACTIVE, now `enabled:false`) — NOT changed by this audit

These previously-active tasks now show disabled. Recorded here for visibility; **not re-enabled** (state changes on money/customer-facing tasks are Joshua's call). Flagged to `#claude-notifications`.

- `weekly-payroll-to-qbo` — was A (critical "don't touch"). Now disabled. Confirm payroll JEs aren't silently dropping.
- `weekly-valley-pawn-email-campaign` — was A (Thu marketing send). Now disabled.
- `weekly-new-deal-request` — was A. Now disabled.
- `distributor-setup-monitor` — was A. Now disabled.
- `mm-merchandisers-daily-scan` — was A (feeds `new-inv-intake`). Now disabled.
- `salt-run-weekly-analytics`, `salt-run-monthly-seo-audit`, `salt-run-quarterly-phase-check` — Salt Run trio, all were A. Now disabled.

(Some may be intentional post-Publer / project-pause decisions. No action taken — reporting only.)

### Skills observed live but not yet in the Section 3 catalog (28-count is stale)

Section 13.C already covers these at the bundle level ("anthropic-skills includes all `vp-*` … + `enterprise-map`, `expert-review-board`"), so no Section 13 edit needed. New individual skills seen: `vp-brand-studio`, `vp-hero-image`, `vp-asset-compose`, `vp-content-batch`, `vp-ad-engine`, `enterprise-map`, `expert-review-board`, `store-credentials`, `amazon-business-ordering`, `daily-intake-margin`, `reel-comment-alert`, `consolidate-memory`, `monday-bravo-combined-run`. Section 3 could be refreshed for completeness, but it is not the capability inventory this audit maintains (Section 13 is).

**Skill delta staged:** No — no connector-level drift required an `enterprise-map` / `valley-pawn-context` patch this month.

---

**End of BUSINESS_OS.md**
