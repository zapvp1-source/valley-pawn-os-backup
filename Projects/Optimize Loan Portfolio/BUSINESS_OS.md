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
| `daily-clockin-check` | Scheduled task | A | Mon–Sat 10:15am | Gusto clock-in audit |
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
| `weekly-timekeeping-analysis` | Scheduled task | A | Mon 2am | Gusto Time Tracking via Chrome → #timekeeping-summary 9am |
| `weekly-employee-sales-rankings` | Scheduled task | T (manual) | Weekly | Pipeline-driven (`employee-activity`), MTD rankings |
| `monthly-employee-sales-rankings` | Scheduled task | A | 1st of month | Final monthly rankings → #employee-performance |
| `monthly-bonus-targets` | Scheduled task | T (manual) | Monthly | Generates next month's revenue bonus targets (Option B yield method) |
| `dismiss-employee` | Scheduled task | T (manual) | Ad hoc | Gusto termination flow |
| `gusto-keep-alive` | Scheduled task | (folder) | — | Session refresh |
| `daily-clockin-check` | Scheduled task | A | Daily 10:15am | (Cross-ref: Ops) |
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

**Gaps in Marketing:**
- (G) No monthly performance digest (open/click rates + best-performing subject lines)
- (G) No email-list segmentation analysis (cold/warm/active customers)
- (G) No A/B testing framework
- (G) Many social tasks are DISABLED (B status) — possibly the right call; verify with Joshua
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
- **Gusto login token expires** → 3 tasks degrade.
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

---

## Section 12 — How To Update This Document

When something ships or a constraint changes:

1. **New scheduled task / skill / pipeline cell** → add to the matching Domain section's table (Section 2)
2. **New saved Bravo report** → add to Section 4 handlers table
3. **New Operating Rule** → add to Section 5 with numbered rule
4. **New project folder** → add to Section 10
5. **Gap filled** → strike through the gap line in the relevant domain; consider adding to Change Log
6. **Backlog reordered** → update Section 9

**Where this doc lives:**
- Canonical: `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/BUSINESS_OS.md`
- Future: consider also referencing from `valley-pawn-context` skill so it's auto-loaded every session

---

**End of BUSINESS_OS.md**
