# Reporting & Analytics Fleet Audit — Valley Pawn
**As of 2026-09-05.** Sources: scheduled-task registry dump (164 registered / 148 enabled / 16 disabled / 12 on-disk-unregistered), all `~/Documents/Claude/Scheduled/*/SKILL.md` frontmatter, `PUBLICATION_CALENDAR.md`, `SCHEDULED_TASK_RELIABILITY_PLAN.md`, `fleet/expected_outputs.json`, `fleet-guardian/SKILL.md`, `BUSINESS_OS.md` §§4/7/8/9 + LIVE STATE, `CHANGELOG.md` Aug 1 – Sep 5.

---

## 1. Every analytics / reporting task

Legend for **Table**: `MODEL` = model hand-renders the table in-session (drift risk); `SCRIPT` = deterministic formatter/compiler owns the output bytes. Guardian = present in `fleet/expected_outputs.json` (Step 1b output verification).

### 1a. Daily analytics/reporting

| Task ID | Cron (ET) | Model pin | Enabled | Data source | Output (channel + marker) | Table | Watchdog / guardian |
|---|---|---|---|---|---|---|---|
| `bravo-morning-pull` | `50 6 * * *` | sonnet-5 | ✅ | Bravo pipeline (intake-detail, sold-discount-detail, items-to-price × 5) | **none** — writes `logs/_morning_pull_status_<DATE>.txt` CLEAN/FAILED certificate | n/a (data pull) | No expected_outputs entry (silent by design). `bravo-prestaging-7am`, `bravo-health-watchdog`, `monday-bravo-postcheck` partially cover |
| `bravo-prestaging-7am` | `30 6 * * *` | sonnet-5 | ✅ | Bravo process control (Type C, direct) | none | n/a | none |
| `bravo-preflight-relaunch` | `0 4 * * *` | sonnet-5 | ✅ | Bravo/watcher relaunch | DM on failure only | n/a | none |
| `bravo-health-watchdog` | `0 5,17 * * *` | sonnet-5 | ✅ | Bravo health gate | DM only if unrecoverable | n/a | is itself the watchdog |
| `pawn-walk` | `15 7 * * *` | sonnet-5 | ✅ | Bravo pipeline `intake-detail` (fast-path off morning-pull cert) | `#pawn-walks` · `Daily Pawn Walk` | **MODEL** (T1/T2/T3 margin table) | ✅ guardian, grace 4h |
| `sold-review` | `45 7 * * *` | sonnet-5 | ✅ | Bravo `sold-discount-detail` (shared pull w/ discount-review) | Joshua DM + `#sold-review` · `SOLD REVIEW` | **MODEL** | ✅ guardian, grace 4h |
| `discount-review` | `25 8 * * *` | sonnet-5 | ✅ | same shared `sold-discount-detail` pull | Joshua DM + `#discount-review` · `DISCOUNT REVIEW` | **MODEL** | ✅ guardian, grace 4h |
| `daily-items-to-price` | `0 8 * * *` | sonnet-5 | ✅ | Bravo `items-to-price` ×5 (fast path) | `#items-to-price` · `Items to Price` | **MODEL** (all-5-or-nothing gate) | ❌ not in expected_outputs |
| `daily-funds-verification` | `0 18 * * *` | sonnet-5 | ✅ | Bravo `safe-register-journal` ×5 + Slack funds channels | `#daily-funds-reconcilation` · `Daily Funds Verification` | **MODEL** (format "LOCKED" in SKILL) | ✅ `funds-verification-watchdog` 18:45 **+** guardian |
| `funds-verification-watchdog` | `45 18 * * *` | sonnet-5 | ✅ | Slack read + re-run | silent; never posts | n/a | is the watchdog |
| `jewelry-onhand-nightly-pull` | `30 20 * * 1-6` | sonnet-5 | ✅ | Bravo `jewelry-case-counts-v2` (1 trigger/store) + Chrome vision read of `#end-of-day` photos | `#jewlery-counts` · `Jewelry Count —` | **MODEL** | `jewelry-onhand-catchup` 7:45 + `jewelry-pull-watchdog` 9:15; ❌ not in expected_outputs |
| `jewelry-onhand-catchup` | `45 7 * * 2-7,0` | sonnet-5 | ✅ | same | same channel | MODEL | self-heal layer |
| `jewelry-pull-watchdog` | `15 9 * * 2-7,0` | haiku-4-5 | ✅ | filesystem check | DM only | n/a | watchdog |
| `asset-recovery-daily-refresh` | `15 19 * * *` | haiku-4-5 | ✅ | Reuses latest 5-store Bravo `end-of-month` CSVs (fresh pull fallback) | Cowork artifact "Asset Recovery 2025 vs 2026" | SCRIPT-ish (artifact) | ❌ none; silent on failure |
| `vp-dashboard-refresh` | `15 8,19 * * *` | sonnet-5 | ✅ | Re-parses Slack reports + artifacts | vp-dashboard.pages.dev | SCRIPT | ❌ none |
| `vp-website-trend-daily-refresh` | `45 0 * * *` | haiku-4-5 | ✅ | **GA4** D/W/M/Q/A | `vp-website-trend` artifact | SCRIPT | ❌ none (was a documented permission-stall victim 9/3–9/4) |
| `daily-unopened-email-eval` | `0 18 * * *` | sonnet-5 | ✅ | Apple Mail ×5 store inboxes | `#emails-missed` + HTML trend report | MODEL | ❌ none |
| `zoom-voicemail-eod-review` | `45 17 * * *` | haiku-4-5 | ✅ | Zoom Phone admin (Chrome) | `#voicemails-calls-missed` | MODEL | ❌ none |
| `daily-clockin-check` | `15 10 * * 1-6` | sonnet-5 | ✅ | **Gusto MCP** (Chrome fallback) | `#general` · `Daily Clock-In Check` | MODEL | ✅ guardian, grace 3h |
| `morning-brief` | `0 8 * * 1-5` | sonnet-5 | ✅ | multi (calendar/Slack/mail) | HTML artifact / DM | MODEL | ❌ none |
| `ceo-mail-brief` | `0 7,16 * * *` | sonnet-5 | ✅ | Gmail MCP + unified-search index | Joshua DM | MODEL | ❌ none |
| `chekkit-unanswered-alert` / `-eod-followup` | `0 8 * * 1-6` / `0 19 * * 1-6` | haiku / sonnet | ✅ | Chekkit (Chrome) | `#chekkit-messages-missed` / `#chekkit-unanswered-summary` | MODEL | ❌ none |
| `precious-metals-settlement-handler` | `0 9 * * *` | sonnet-5 | ✅ | Gmail (Elemetal) + Bravo scrap CSVs | REVIEW workbook, silent no-op | SCRIPT+MODEL | ❌ none |
| `business-os-daily-refresh` | `0 5 * * *` | sonnet-5 | ✅ | registry + launchd + filesystem | BUSINESS_OS LIVE STATE + CHANGELOG | SCRIPT (`refresh_live_state.py`) | ❌ none |

### 1b. Weekly analytics/reporting

| Task ID | Cron (ET) | Model pin | Enabled | Data source | Output + marker | Table | Guardian |
|---|---|---|---|---|---|---|---|
| `monday-bravo-combined-run` | `0 18 * * 0` (Sun) | sonnet-5 | ✅ | Bravo pipeline — ONE combined trigger: `aged-inventory-summary`, `loans-75-days-past-due`, `layaways`, `employee-activity`, `chekkit-inactives` × 5 stores | Joshua DM · `Sunday Bravo pull dispatched` + heartbeat file | n/a (trigger drop) | ✅ guardian, grace 2h |
| `monday-bravo-combined-compile` | `0 8 * * 1` | sonnet-5 | ✅ | reads result.json + CSVs from disk | 6 posts: `#aged-inventory-review` `#store-performance` `#loan-review` `#layaway-review` `#employee-performance` `#first-payment-default` | **MIXED** — aged-inventory now **SCRIPT** (`bin/format_aged_inventory.py`, 9/5); loan/layaway/employee/FPD still **MODEL** | ✅ guardian (sentinel `#store-performance` marker `Store`) + `monday-bravo-postcheck` |
| `monday-bravo-postcheck` | `30 8 * * 1` | sonnet-5 | ✅ | same CSVs; last-resort fresh trigger drop | backfills missing of the 4 | inherits compile logic | ✅ guardian (`#loan-review` · `Weekly Past-Due Loan Review`) |
| `weekly-loan-review-canvas-refresh` | `20 9 * * 1` | haiku-4-5 | ✅ | pipeline output | `#loan-review` Canvas | MODEL | ❌ |
| `weekly-layaway-review-canvas-refresh` | `22 9 * * 1` | haiku-4-5 | ✅ | pipeline output | `#layaway-review` Canvas | MODEL (has self-heal Step 1b) | ❌ |
| `weekly-employee-perf-canvas-refresh` | `24 9 * * 1` | haiku-4-5 | ✅ | employee rankings file | `#employee-performance` Canvas | MODEL (staleness check + self-heal) | ❌ |
| `weekly-aged-inventory-canvas-refresh` | `26 9 * * 1` | haiku-4-5 | ✅ | per-store aged CSVs | `#aged-inventory-review` Canvas | MODEL (own 5-store stop gate) | ❌ |
| `weekly-store-perf-canvas-refresh` | `28 9 * * 1` | haiku-4-5 | ✅ | weekly store KPI files | `#store-performance` Canvas | MODEL | ❌ |
| `weekly-store-kpis` | `30 10 * * 1` | sonnet-5 | ✅ | Bravo `end-of-month` XLSX ×5 MTD (reuse-check first) | `#store-performance` · `Weekly Store Performance Rankings` (2 msgs) | **SCRIPT** (`store_kpis_compile.py`, 8 metrics + rank) | ✅ guardian, grace 4h |
| `layaway-yield-weekly` | `15 11 * * 1` | sonnet-5 | ✅ | Bravo MTD layaway deposits | `#layaway-review` · `Layaway Yield` + Details sheet + Canvas | MODEL | ✅ guardian |
| `nics-weekly-mtd-ranking` | `30 9 * * 1` | sonnet-5 | ✅ | Bravo FFL transfers MTD ×5 | `#ffl-transfer-performance` · `Month-to-Date` | MODEL | ✅ guardian |
| `weekly-markdown-verification-pull` | `0 19 * * 0` | sonnet-5 | ✅ | Bravo `markdown-verification` ×5 | Joshua DM · `Markdown-verification pull dispatched` | n/a | ✅ guardian, grace 2h |
| `weekly-markdown-verification-review` | `35 9 * * 1` | sonnet-5 | ✅ | Sunday pull CSVs + `results/*.result.json` | `#mark-downs-summary` / `#items-to-markdown` · `Markdown` | MODEL | ❌ (hardened Step 1/1b instead) |
| `weekly-loan-layaway-manager-dms` | `0 9 * * 1` | sonnet-5 | ✅ | compile output | per-store manager DMs | MODEL | ❌ |
| `weekly-timekeeping-analysis` | `30 0 * * 1` | sonnet-5 | ✅ | **Gusto MCP** `list_time_records` (Chrome fallback) | `#timekeeping-summary` · `Weekly Timekeeping` | MODEL (sanity gate ≥5 emp, 150–600h) | ✅ guardian |
| `weekly-returns-summary` | `20 1 * * 1` | sonnet-5 | ✅ | Slack `#returns` + xlsx trend | `#weekly-returns-summary` · `Returns — Week of` | MODEL + xlsx | ✅ guardian |
| `review-obtained-last-week` | `15 1 * * 1` | sonnet-5 | ✅ | **Chekkit** (Chrome) | `#google-reviews` · `ranked` | MODEL | ✅ guardian **+** `google-reviews-post-watchdog` 10:45 |
| `google-reviews-post-watchdog` | `45 10 * * 1` | sonnet-5 | ✅ | Slack read + Chekkit re-pull | backfill post | MODEL | watchdog |
| `weekly-analytics-summary` | `0 1 * * 1` | sonnet-5 | ✅ | **GA4** | `#website` · `Weekly Website Analytics` (scheduled 9 AM) | MODEL | ✅ guardian |
| `weekly-website-health-audit` | `15 5 * * 1` | sonnet-5 | ✅ | site crawl + WP REST | `#website` · `Weekly Website Health Audit` | MODEL + history.json | ✅ guardian |
| `vp-website-shop-weekly-report` | `40 7 * * 1` | sonnet-5 | ✅ | site + WooCommerce + eBay | Joshua DM | MODEL | ❌ |
| `weekly-social-media-recap` | `40 9 * * 1` | sonnet-5 | ✅ | **Publer** (read-only verify) | `#social-media` · `Weekly Social Recap` | MODEL | ✅ guardian |
| `vp-follower-growth-monthly-check` | `50 9 * * 1` | sonnet-5 | ✅ | Publer | Joshua DM | MODEL | ❌ |
| `vp-publer-analytics-friday` | `0 16 * * 5` | sonnet-5 | ✅ | Publer API | Joshua DM + `weekly-adjustments.json` | SCRIPT+MODEL | ❌ |
| `email-analytics-weekly` | `30 3 * * 5` | sonnet-5 | ✅ | **Brevo API** per-link clicks | `#email-campiagns` · `Email — Week of` + master Sheet + dashboard | MODEL | ✅ guardian |
| `brevo-weekly-efficiency-audit` | `0 8 * * 5` | sonnet-5 | ✅ | Brevo | `#email-campiagns` · `Email channel efficiency` | MODEL | ✅ guardian |
| `ebay-weekly-channel-audit` | `45 11 * * 1` | sonnet-5 | ✅ | **eBay Trading API** ×5 | `#ebay-performance` · `Channel Pulse` + dashboard | MODEL | ❌ |
| `weekly-online-store-audit` | `0 8 * * 0` | sonnet-5 | ✅ | eBay + website | `#ebay-performance` · `Weekly Online Store Audit` (webhook) | MODEL | ✅ guardian, grace 6h |
| `ebay-markdown-terminal-weekly` | `15 12 * * 1` | sonnet-5 | ✅ | eBay API | `#ebay-performance` · `markdown floor` | MODEL | ❌ |
| `ebay-title-photo-accuracy-audit` | `0 8 * * 0` | sonnet-5 | ✅ | eBay | manager DMs + Joshua DM | MODEL | ❌ |
| `ebay-weekly-quality-fix` | `0 11 * * 1` | sonnet-5 | ✅ | eBay | manager DMs | MODEL | ❌ |
| `ebay-feedback-reply-weekly` | `20 10 * * 4` | **NONE** | ✅ | eBay Trading API + `~/ebay_feedback_answered.json` | Joshua DM | SCRIPT-backed | ❌ |
| `vp-ai-search-health-check` | `10 6 * * 1` | sonnet-5 | ✅ | schema/llms.txt/Google+Bing NAP (Chrome) | `#ai-marketing` · `AI-search health check` | MODEL | ✅ guardian |
| `vp-ai-visibility-metrics` | `30 6 * * 5` | sonnet-5 | ✅ | 5 AI engines + **GA4** AI-referrals | `#ai-marketing` · `Visibility` + Tracker sheet | MODEL | ✅ guardian (marker flagged "approximate") |
| `vp-ai-search-autofix` / `vp-ai-visibility-autofix` | `30 8 * * 1` / `30 9 * * 5` | sonnet-5 | ✅ | same lanes | `#ai-marketing` Fixed/Needs-you | MODEL | ❌ |
| `vp-presence-audit-weekly` | `20 16 * * 0` | sonnet-5 | ✅ | rolls up the 3 above + off-site sweep | `#ai-marketing` · `WEEKLY PRESENCE AUDIT` + `presence_scorecard_latest.json` | MODEL + JSON | ✅ guardian, grace 6h |
| `marketing-ceo-briefing-weekly` | `30 11 * * 1` | sonnet-5 | ✅ | rolls up 8 lane audits from Slack (does not re-run) | Joshua DM · `Marketing CEO Briefing` + artifact | MODEL + history.json | ✅ guardian |
| `sunday-checklist-summary` | `0 20 * * 0` | sonnet-5 | ✅ | Slack `#in-store-checklists` photos via Chrome vision | `#in-store-checklists` + Apple Reminders | MODEL | ❌ |
| `vp-content-batch-quota-watchdog` | `0 10 * * 2` | sonnet-5 | ✅ | live Publer | Joshua DM on 2-week shortfall | SCRIPT (`quota_watchdog.py`) | ❌ |
| `chekkit-weekly-review-requests` | `30 16 * * 2` | sonnet-5 | ✅ | Bravo `chekkit-inactives` (stashed by Monday run) + Brevo | `#chekkit-updates` + `#email-campaigns` counts | MODEL | ✅ (calendar) |
| `bravo-brevo-attribute-sync` | `30 17 * * 2` | sonnet-5 | ✅ | Bravo customer data → Brevo | `#email-campiagns` · `Weekly Email Upload` | MODEL | ✅ (calendar) |
| `bald-rock-monday-briefing` | `15 4 * * 1` | sonnet-5 | ✅ | Guesty/Airbnb/VRBO | `#airbnb` · `Bald Rock` | MODEL | ✅ (calendar) |
| `scheduled-task-model-audit-weekly` | `0 5 * * 1` | sonnet-5 | ✅ | registry + SKILL frontmatter | log | SCRIPT | meta |

### 1c. Monthly / quarterly / annual analytics

| Task ID | Cron (ET) | Model pin | Enabled | Data source | Output + marker | Table | Guardian |
|---|---|---|---|---|---|---|---|
| `monthly-analytics-prestage` | `0 20 28-31 * *` | **haiku-4-5** | ✅ | Bravo `end-of-month` × 6 date-windows × 5 stores (30 sidecars) via native `bin/monthly_prestage_runner.py` | staged XLSX + `{YYYY-MM} Prestage.md` | **SCRIPT** since 9/5 (was model loop) | ❌ silent on failure |
| `monthly-analytics-report` | `45 1 1 * *` | sonnet-5 | ✅ | reads prestaged sidecars (`parse_eom.py`) | `#company-performance` · `Monthly Analytics -` + Google Sheet | SCRIPT parse + **MODEL** post | ✅ guardian (added 9/5) **+** `monthly-analytics-watchdog` 7 AM |
| `monthly-analytics-watchdog` | `0 7 1 * *` | sonnet-5 | ✅ | Slack read | short plain DM only (Rule 16/18) | n/a | watchdog |
| `monthly-employee-sales-rankings` | `0 2 1 * *` | sonnet-5 | ✅ | Bravo **new** cell `employee-activity-range` (built 9/5) | `#employee-performance` · `FINAL` + workbook | MODEL, metric locked to *Retail Sales Excluding Fees* | ✅ guardian (added 9/5) |
| `monthly-scrap-rankings` | `30 4 1 * *` | sonnet-5 | ✅ | Bravo scrap buckets (`scrap_rankings.py`) | `#scrap-rankings` · `gold scrap` | **SCRIPT** | ✅ guardian (added 9/5) |
| `nics-monthly-ranking` | `30 9 1 * *` | sonnet-5 | ✅ | Bravo FFL ×5 | `#ffl-transfer-performance` · `(final)` | MODEL | ✅ guardian |
| `monthly-ebay-ratings-sweep` | `0 10 1 * *` | sonnet-5 | ✅ | **eBay Seller Hub scrape via Chrome** | `#ebay-performance` · `Ratings Sweep` + monthly doc | MODEL | ✅ guardian |
| `vp-new-customer-report` | `0 7 3 * *` | sonnet-5 | ✅ | Bravo `chekkit-invites-range` ×5 | `#new-customers` · `New Customers —` (Slack **first** since 9/5), then artifact | MODEL | ✅ guardian (added 9/5) |
| `monthly-bonus-targets` | `0 9 2 * *` | **opus-4-8** | ✅ | Bravo pipeline (Option B yield) | Joshua DM · `Bonus Targets` + VP BONUS FINAL sheet | MODEL | ✅ guardian |
| `monthly-bonus-qualifiers` | `0 9 10 * *` | sonnet-5 | ✅ | Chekkit invites + review pulls + scrap buckets + Publer + Bravo EOM | `#bonus-goals` · `qualif` + MASTER xlsx | MODEL | ❌ (calendar flags July's missing) |
| `monthly-bonus-payout` | `30 11 10 * *` | sonnet-5 | ✅ | qualifiers output | Joshua DM draft (never auto-sent) | MODEL | ❌ |
| `monthly-eom-recap` | `30 10 1 * *` | **NONE** | ✅ | each channel's own verified weekly/daily posts | "Month in Review" into 15 analytics+marketing channels | MODEL | ❌ (brand new) |
| `eom-bravo-gl-export` | `0 6 1 * *` | sonnet-5 | ✅ | Bravo `post-to-accounting-post` + Consolidated GL ×5 → Drive → **QBO via Chrome** | Joshua DM (ledger link) | SCRIPT+MODEL | ✅ `eom-bravo-gl-export-watchdog` day 2 8 AM |
| `sales-tax-monthly-update` | `0 8 1 * *` | sonnet-5 | ✅ | reuses eom-GL per-store CSVs | `Sales Tax.xlsx` | SCRIPT | self-alerting |
| `monthly-gun-audit-report` | `30 2 16 * *` | sonnet-5 | ✅ | Slack forms + **Chrome** → Trends Sheet | `#monthly-gun-audit` · `Monthly Gun Audit Summary` | MODEL | ✅ guardian, grace 24h |
| `monthly-amazon-store-allocation` | `0 9 6 * *` | sonnet-5 | ✅ | Amazon Business shipments report | Joshua DM + xlsx | MODEL | ❌ |
| `monthly-capability-drift-audit` | `40 7 1 * *` | sonnet-5 | ✅ | live tools/skills/registry vs BUSINESS_OS §13 | Slack deltas + staged patch | MODEL | ❌ |
| `vp-comms-drift-monthly-check` | `0 8 3 * *` | sonnet-5 | ✅ | Slack channels vs Field Comm Standard | Joshua DM | MODEL | ❌ |
| `task-hygiene-sweep` | `0 4 1 * *` | sonnet-5 | ✅ | registry | Joshua review list | MODEL | ❌ |
| `vp-hr-policy-monthly-sync` | `35 8 1 * *` | sonnet-5 | ✅ | Slack `#policy-announcements` | P&P/Handbook docs | MODEL | ❌ |
| `quarterly-capex-sweep` | `0 9 1 1,4,7,10 *` | sonnet-5 | ✅ | GDrive + iCloud | CAP GAIN trackers | MODEL | ❌ |
| `vp-hr-compliance-quarterly-review` | `0 8 2 1,4,7,10 *` | **opus-4-8** | ✅ | law vs Handbook/P&P | review doc | MODEL | ❌ |
| `vp-creative-refresh-quarterly` | `40 7 1 1,4,7,10 *` | opus-4-8 | ✅ | performance + season | creative ledger | MODEL | ❌ |
| `annual-board-review` | `0 0 1 1 *` | opus-4-8 | ✅ | prior-year data | Drive presentation | MODEL | ❌ |

### 1d. DISABLED analytics tasks (registered, `enabled:false`) — flagged

| Task ID | Cron | Why disabled | Anyone own the job? |
|---|---|---|---|
| `weekly-website-kpi-artifact-refresh` | `45 2 * * 1` | Superseded 2026-08-03 by `vp-website-trend-daily-refresh` (stop duplicate GA4 pulls) | ✅ yes |
| `jewelry-onhand-nightly-compare` | `45 21 * * 1-6` | Folded into `jewelry-onhand-nightly-pull` | ✅ yes |
| `jewelry-count-reconciliation` | `47 19 * * *` | Superseded, no `lastRunAt` ever | ✅ yes |
| `preston-ebay-feedback-watch` | `0 9 * * *` | Superseded 8/26 by `preston-interactive-assistant` | ⚠️ **partly** — CHANGELOG 9/5 notes nothing automates eBay feedback replies; `ebay-feedback-reply-weekly` was created after |
| `weekly-social-media-content` | `0 8 * * 1` | Superseded by `vp-content-batch-weekly` (last ran 4/9) | ✅ yes |
| `store-mail-archive-sweep` | `*/10 * * * *` | Replaced by native Gmail filters 8/24 | ✅ yes |
| `wordpress-token-keepalive` | `0 3,15 * * *` | dormant since 7/30 | ⚠️ unclear |
| One-shots (disabled after firing) | — | `bald-rock-payout-verification-sep1`, `interview-schedule-monday-dm`, `ffl-mtd-ranking-verify-20260824`, `ebay-return-policy-retry`, `icloud-forward-verify-check`, `qbo-rent-reconcile-resume`, `store-supplies-corp-split-2025`, `bald-rock-vrbo-rate-sync-recheck`, `catchup-monthly-analytics-aug-2026`, `catchup-scrap-rankings-aug-2026` | n/a — spent |

**Rollback holds:** the 9 migrated cloud triggers left DISABLED 2026-08-21 as rollback holds were to be deleted "after a clean proving week (~8/28)" — that deletion is **not recorded anywhere in the CHANGELOG**, so they are still-open debris. Separately, 12 `com.valleypawn.vpops.job_*` launchd plists sit **DISABLED** (aged_inventory, daily_loan_inv_text, employee_rankings, fpd_ranking, gold_trend, loan_layaway_review, monthly_analytics, monthly_prestage, store_rankings, trigger_dropper, watchdog, publish_dashboard) — the old native reporting fleet, superseded by Cowork tasks.

### 1e. ON DISK, NEVER REGISTERED (never fire) — 12 folders

| Folder | Analytics? | Who owns the job now |
|---|---|---|
| `weekly-aged-inventory-report` | ✅ | `monday-bravo-combined-compile` (banner added 9/5 pointing to `format_aged_inventory.py`) |
| `weekly-aged-inventory-review` | ✅ | same — a **second** stale variant, BUSINESS_OS §8 item 12 flagged this duplicate |
| `weekly-employee-sales-rankings` | ✅ | `monday-bravo-combined-compile` (MTD) + `monthly-employee-sales-rankings` (FINAL) |
| `weekly-loan-layaway-review` | ✅ | `monday-bravo-combined-compile` |
| `daily-intake-prestage` | ✅ | merged into `pawn-walk` |
| `daily-intake-margin` | ✅ | merged into `pawn-walk` |
| `daily-loan-inventory-text` | ✅ | **ORPHANED** — its launchd agent `com.valleypawn.vpops.job_daily_loan_inv_text` is DISABLED, yet `weekly-store-kpis` Step 2.5 still says "the native `daily-loan-inventory-text` job pulls this exact cell at ~7:30 AM daily." That reuse-check can never hit. **Live defect.** |
| `new-inv-weekly-report` | ✅ | **nobody** — vendor/new-inventory sell-through reporting is dark |
| `mm-merchandisers-daily-scan` | partly | nobody (referenced by `new-inv-intake` skill) |
| `monday-bravo-part1-watchdog` | ✅ | intentionally deleted 8/21; replaced by guardian + `expected_outputs` entry. Folder is residue |
| `dashboard-data-collector` | ✅ | **owned** by loaded launchd agent `com.valleypawn.dashboarddatacollector` |
| `close-fl-manager-posting`, `cybertruck-wrap-tint-quote-followup` | ❌ | deliberately dead |

**Referenced-but-nonexistent:** `monthly-publication-audit` (2nd + 4th, 10 AM) is documented in `PUBLICATION_CALENDAR.md` as "the monthly net" and in `expected_outputs.json` prose — **it exists neither in the registry nor on disk.** CHANGELOG 9/5 (5) explains why: "NOT REGISTERED (permission classifier blocked autonomous creation — needs Joshua's click)… Ready-to-register SKILL.md files in `Valley Pawn OS/pending-tasks/`." `monthly-eom-recap` was in the same blocked batch but has since been registered. **The monthly safety net is documented but does not run.**

**Native launchd reporting agents** (outside Cowork, no model pin, invisible to fleet-guardian): `com.valleypawn.ebay-daily-listings` (1:30 PM → `#ebay-listings`), `com.valleypawn.ebay-efficiency-weekly` (Fri 3:30 PM → `#ebay-performance` · `eBay Efficiency`), `com.valleypawn.ebay-weekly-rankings` (Mon 9:30 AM · `eBay Weekly Sales Rankings`), `com.valleypawn.ebay-markdown-monthly` (1st 6 AM — the actual markdown engine), `com.valleypawn.dashboarddatacollector`, `com.valleypawn.fleet-health` (13:30 + 22:30, Layer 0), `com.valleypawn.disk-health`, `com.valleypawn.preston-watch`.

---

## 2. Sunday → Monday chain

```
SUN 16:20  vp-presence-audit-weekly ──────────────► #ai-marketing (WEEKLY PRESENCE AUDIT)
SUN 18:00  monday-bravo-combined-run  [PART 1, ~3 min wall]
             ├─ preflight: watcher alive? BravoAutoLogin? trigger queue empty?
             ├─ drops ONE combined trigger: aged-inventory-summary | loans-75-days-past-due |
             │  layaways | employee-activity | chekkit-inactives   × CUL,HAR,LEX,ROA,WAY  (25 cells)
             ├─ writes completion HEARTBEAT (added 8/21)
             └─ DM "Sunday Bravo pull dispatched"           ── guardian marker, grace 2h
                        │  (~60–75 min of VM time overnight)
SUN 19:00  weekly-markdown-verification-pull [PART 1] → 5-store markdown-verification trigger
             └─ DM "Markdown-verification pull dispatched"  ── guardian marker, grace 2h
SUN 20:00  sunday-checklist-summary → #in-store-checklists + Reminders
SUN 21:45  fleet-guardian pass  (catches a silent PART-1 death; rerun-safe → re-drops)
                        │
MON 00:30  weekly-timekeeping-analysis (Gusto MCP)  → schedules 9 AM #timekeeping-summary
MON 00:45  vp-website-trend-daily-refresh (GA4)
MON 01:00  weekly-analytics-summary (GA4)           → schedules 9 AM #website
MON 01:15  review-obtained-last-week (Chekkit)      → schedules 9 AM #google-reviews
MON 01:20  weekly-returns-summary                   → schedules 9 AM #weekly-returns-summary
MON 01:30  valley-pawn-blog-publisher
MON 05:00  scheduled-task-model-audit-weekly · 05:15 weekly-website-health-audit
MON 06:10  vp-ai-search-health-check
MON 06:30  bravo-prestaging-7am · 06:50 bravo-morning-pull (daily lane, separate 15 cells)
MON 07:15/07:45/08:00/08:25  pawn-walk · sold-review · daily-items-to-price · discount-review
MON 07:40  vp-website-shop-weekly-report
MON 08:00  monday-bravo-combined-compile  [PART 2, fixed cron since 8/21 — no longer re-armed by PART 1]
             reads results/*.result.json + CSVs (PIPELINE_DATE = Sunday, not "today")
             ├─ #aged-inventory-review   ← bin/format_aged_inventory.py, verbatim stdout or NOTHING
             ├─ #store-performance       (guardian sentinel, marker "Store")
             ├─ #loan-review             (hand-rendered)
             ├─ #layaway-review          (hand-rendered)
             ├─ #employee-performance    (MTD, hand-rendered)
             ├─ #first-payment-default   (hand-rendered — Culpeper cell failing all Aug)
             └─ Joshua DM rollup; Word/Excel saved
MON 08:10  vp-deal-of-week-monday-prompt · 08:30 vp-ai-search-autofix
MON 08:30  monday-bravo-postcheck  ── verifies the 4 ops reports; backfills;
             if pipeline data entirely absent → drops a fresh trigger (last-resort self-heal, 8/21)
MON 09:00  weekly-loan-layaway-manager-dms   · 09:05 vp-gusto-signature-chase
MON 09:20  weekly-loan-review-canvas-refresh
MON 09:22  weekly-layaway-review-canvas-refresh
MON 09:24  weekly-employee-perf-canvas-refresh
MON 09:26  weekly-aged-inventory-canvas-refresh
MON 09:28  weekly-store-perf-canvas-refresh      ← Phase 2 wants these 5 merged into 1 session
MON 09:30  nics-weekly-mtd-ranking (#ffl-transfer-performance)
MON 09:35  weekly-markdown-verification-review (#items-to-markdown)  ← consumes Sunday 19:00 pull
MON 09:40  weekly-social-media-recap · 09:50 vp-follower-growth-monthly-check
MON 10:30  weekly-store-kpis  ── OWN 5-store end-of-month XLSX pull (reuse-check first),
             store_kpis_compile.py → 2 locked messages → #store-performance
MON 10:45  google-reviews-post-watchdog (backfills the 01:15 producer)
MON 11:00  vp-content-batch-preflight · 11:10 deal-of-week reminder
MON 11:15  layaway-yield-weekly → #layaway-review + Canvas
MON 11:30  marketing-ceo-briefing-weekly  ── rolls up 8 lane audits, does NOT re-run them
MON 11:45  ebay-weekly-channel-audit · 11:50 brevo-weekly-draft-guard · 12:15 ebay-markdown-terminal
MON 12:30  vp-deal-of-week-monday-pick → 13:05 vp-website-deals-weekly → 13:40 vp-content-batch-weekly
MON 12:45  fleet-guardian pass #1 (verifies the whole Monday pack against expected_outputs)
MON 14:30/15:10/15:45  vp-deal-reels · vp-community · vp-engagement
MON 16:40  vp-content-batch-postflight · 21:45 fleet-guardian pass #2
```

**Structural note:** `weekly-store-kpis` (10:30) drives Bravo *again* for `end-of-month` even though `monday-bravo-combined-compile` posted a `#store-performance` message at 8:00 — two writers, two pulls, same channel, 2.5 h apart.

---

## 3. Monthly chain

```
LAST DAY 20:00  monthly-analytics-prestage   [haiku]
                  launches bin/monthly_prestage_runner.py (native, idempotent, resumable)
                  6 date-windows × 5 stores = 30 EOM XLSX sidecars  (~60 min VM)
                  writes "{YYYY-MM} Prestage.md" + logs/;  Cowork task = launcher+verifier ONLY
                          │
DAY 1 01:45  monthly-analytics-report  ── parse_eom.py 30/30 → Rule-18 gate (ALL 30 CSVs + ALL 5 stores)
                  → #company-performance "Monthly Analytics - <Month>"  + Google Sheet
                  → (#store-performance post DELETED 2026-09-05 by standing decision)
DAY 1 02:00  monthly-employee-sales-rankings → #employee-performance "FINAL" (employee-activity-range ×5)
DAY 1 02:15  monthly-we-buy-gold-silver-email (Brevo, preflight-gated)
DAY 1 04:00  task-hygiene-sweep
DAY 1 04:30  monthly-scrap-rankings → #scrap-rankings (scrap_rankings.py)
DAY 1 06:00  eom-bravo-gl-export  ── post unposted days ×5 → Consolidated GL ×5 → Drive → QBO (Chrome)
DAY 1 07:00  monthly-analytics-watchdog  ── verifies #company-performance; plain DM only if late
DAY 1 07:40  monthly-capability-drift-audit  ·  08:00 sales-tax-monthly-update (reuses GL CSVs)
DAY 1 08:35  vp-hr-policy-monthly-sync
DAY 1 09:00  monthly-cloudcover-music-refresh
DAY 1 09:30  nics-monthly-ranking → #ffl-transfer-performance "(final)"
DAY 1 10:00  monthly-ebay-ratings-sweep → #ebay-performance "Ratings Sweep"
DAY 1 10:30  monthly-eom-recap  ── "Month in Review" into 15 analytics+marketing channels,
                  built ONLY from each channel's own verified weekly/daily posts; per-channel gates
DAY 2 08:00  eom-bravo-gl-export-watchdog (DM w/ diagnostics only on failure)
DAY 2 09:00  monthly-bonus-targets [OPUS] → Joshua DM draft → he posts to #bonus-goals
DAY 2 + DAY 4 10:00   monthly-publication-audit   ◄── DOES NOT EXIST (never registered)
DAY 3 07:00  vp-new-customer-report → #new-customers FIRST, artifact second (reordered 9/5)
DAY 3 08:00  vp-comms-drift-monthly-check
DAY 6 09:00  monthly-amazon-store-allocation
DAY 10 09:00 monthly-bonus-qualifiers → #bonus-goals  (rails: Chekkit invites, Monday review pulls,
                  scrap buckets CLOSED in month, Publer FB gains, Bravo EOM revenue)
DAY 10 11:30 monthly-bonus-payout → Joshua DM draft (never auto-sent, never touches Gusto)
DAY 16 02:30 monthly-gun-audit-report → #monthly-gun-audit
```

---

## 4. Daily chain

```
04:00  bravo-preflight-relaunch      relaunch Bravo + watcher to clean logged-in state
05:00  bravo-health-watchdog (AM)    proactive health gate before the morning batch
05:00  business-os-daily-refresh · document-photos-index-refresh
06:30  bravo-prestaging-7am          Type C direct process control, foreground-guarded
06:50  bravo-morning-pull            ONE combined trigger, 15 cells (intake-detail,
                                     sold-discount-detail, items-to-price × 5 stores)
                                     watcher singleton hygiene (_restart_watcher_v2.ps1) + health gate
                                     → writes per-report CLEAN/FAILED certificate. SILENT ALWAYS.
07:00  brevo-preflight-watchdog · backup-health-watchdog · ceo-mail-brief · vp-website-shop-nightly
07:15  pawn-walk                     fast path off certificate → #pawn-walks (T1/T2/T3 margins)
07:45  sold-review                   shared sold-discount pull → DM + #sold-review
07:45  jewelry-onhand-catchup        (Tue–Sun) reruns a missed night inside the freeze window
08:00  daily-items-to-price          ALL-FIVE-OR-NOTHING → #items-to-price
08:00  northwest-registered-agent-daily-check · 08:10 morning-brief · 08:15 vp-dashboard-refresh
08:25  discount-review               same shared pull → DM + #discount-review
08:45  oura-daily-import · 08:50 ffl-transfer-email-responder
09:00  precious-metals-settlement-handler
10:15/10:25/10:30  daily-clockin-check (Gusto) / cloudcover / dress-code → #general
12:45  fleet-guardian pass #1        · 13:30 native fleet-health sentinel (Layer 0)
17:00  bravo-health-watchdog (PM)    gate before the 6 PM funds run
17:45  zoom-voicemail-eod-review
18:00  daily-funds-verification      safe-register-journal ×5 (~63–85 s/cell serial, 5–7 min)
                                     → #daily-funds-reconcilation + per-store funds channels
18:00  daily-unopened-email-eval → #emails-missed
18:45  funds-verification-watchdog   silent re-run if no post found
19:15  asset-recovery-daily-refresh  reuse-first off latest EOM CSVs → artifact, silent on failure
20:30  jewelry-onhand-nightly-pull   (Mon–Sat) ONE TRIGGER PER STORE, 8 categories each,
                                     inside the 6 PM–10 AM freeze window; + Chrome vision read of
                                     #end-of-day PM sheets → #jewlery-counts
21:45  fleet-guardian pass #2        · 22:30 native fleet-health sentinel
09:15 (next AM) jewelry-pull-watchdog  DM if last night's CSVs are absent
```

---

## 5. Bravo touch count and VM minutes

**Per day (every day):** 13 tasks touch Bravo — `bravo-preflight-relaunch`, `bravo-health-watchdog` (×2 fires), `bravo-prestaging-7am`, `bravo-morning-pull`, `pawn-walk`, `sold-review`, `daily-items-to-price`, `discount-review`, `daily-funds-verification`, `funds-verification-watchdog`, `asset-recovery-daily-refresh`, plus `jewelry-onhand-catchup` (Tue–Sun) and `jewelry-onhand-nightly-pull` (Mon–Sat).

Only **3–4 of those actually pull data** on a healthy day; the 4 morning reports fast-path off the certificate.

| Daily consumer | Cells | Documented time |
|---|---|---|
| `bravo-morning-pull` | 15 (3 reports × 5 stores) | **30–40 min**; poll cap ~50 min; retry round cap +20 min |
| `daily-funds-verification` | 5 | 63–85 s each, serial → **5–7 min** (10-min timeout) |
| `jewelry-onhand-nightly-pull` | 5 triggers × 8 categories | 6–15 min/store, up to 35 for a flaky store → **30–75 min** (Mon–Sat) |
| health gates / relaunch | — | ~3–12 min combined |
| downstream fallback pulls | 0 when cert CLEAN | 85 min on 2026-08-16 when contention hit |

**Daily VM ≈ 70–125 min** (≈ 45–55 min Sundays, no jewelry pull).

**Per week (on top of daily):** 6 Bravo-touching tasks — `monday-bravo-combined-run` (25 cells, **~60–75 min**), `weekly-markdown-verification-pull` (5 stores @ 2.5–4.5 min → **12–25 min**), `weekly-store-kpis` (5 EOM XLSX → **8–12 min**, skipped if the reuse-check passes — see the orphan defect), `layaway-yield-weekly`, `nics-weekly-mtd-ranking`, `chekkit-weekly-review-requests` (consumes Monday's stashed CSVs, no new pull). Reader-only downstream: `monday-bravo-combined-compile`, `monday-bravo-postcheck`, 5 canvas refreshes, `weekly-markdown-verification-review`.

**Weekly incremental VM ≈ 90–130 min.** Weekly total (daily × 7 + weekly) ≈ **9.5–15.5 VM-hours**.

**Per month (on top):** 8 Bravo-touching tasks — `monthly-analytics-prestage` (30 cells, **~60 min**, first window 5/5 in 10 min on the 9/5 rebuild), `monthly-analytics-report` (reads only), `monthly-employee-sales-rankings` (5 `employee-activity-range` cells, ~5–10 min; CUL needed a 120 s preview budget), `monthly-scrap-rankings` (5 single-store pulls), `nics-monthly-ranking` (5), `vp-new-customer-report` (5 `chekkit-invites-range`), `eom-bravo-gl-export` (post-to-accounting ×5 + GL ×5, **~70 s per GL** once unblocked, but the post step is the historic blocker), `monthly-bonus-targets`/`-qualifiers` (Bravo EOM re-read). **Monthly incremental VM ≈ 100–150 min.**

**Monthly grand total ≈ 40–55 VM-hours.** Against a hard constraint the plan names but the VM budget doesn't: **3 concurrent Cowork sessions fleet-wide**, with **7,876 queue-wait skips in the last 7 days** (LIVE STATE) / 8,428 in 8 days (reliability plan).

---

## 6. Failure & friction patterns, Aug 1 – Sep 5

| # | Category | Count | Dated examples |
|---|---|---|---|
| 1 | **Queue contention / 3-slot global limit** | 8,428 skips in 8 days (500–1,200/day; **2,900 on 8/29**); 49 enabled tasks fire 8:00–9:59 AM, ~20 on Monday 9:00–9:59 | 9/4 root cause: `global_limit (active=3, limit=3)`, server-side, not adjustable. Mislabeled "usage cap" in LIVE STATE + the `scheduled-task-models` skill until 9/4 |
| 2 | **Chrome/computer permission stall → hung-run reaper kills at 1,800 s** | **10 of 318 runs in 40 h (3%)**, each holding a slot 30–70 min producing nothing; 15–17 enabled tasks use the Chrome extension; only 2 of 163 had `skip_all_permission_checks` | 9/3–9/4 victims: `vp-ai-visibility-metrics`, `gusto-keep-alive` ×3, `zoom-voicemail-alert`, `sold-review`, `northwest-registered-agent-daily-check`, `ffl-transfer-email-responder`, `vp-new-customer-report`, `vp-website-trend-daily-refresh`, `gdrive-cache-refresh`. 8/18: `vp-content-batch-quota-watchdog` stalled on `request_cowork_directory`. 8/21: `weekly-store-perf-canvas-refresh` stalled mid-run on a folder approval |
| 2b | **MCP sibling-tool approval stall** (same class, non-Chrome) | **67 enabled tasks with partial approvals**; dry-run added **697 approvals across 66 tasks** | 9/4 04:11 `bald-rock-15-day-contract` stalled on `listRecipients` (not in stored approvals, count=4), killed before its own failure DM; same class as its 8/7 dark period (2 guest contracts never sent, caught manually 8/21) |
| 3 | **Silent death at a non-essential step** | ≥5 distinct | 9/3 `vp-new-customer-report` died at the artifact-update tool *after* the data was complete → Slack post never happened (fixed 9/5: Slack first, artifact best-effort). 7/27→8/21 `vp-deal-of-week-monday-pick` died at Brevo `POST /v3/media` (endpoint doesn't exist) → W10/W11/W12 never sent, 3 weeks dark. 8/10 + 8/17 `vp-website-deals-weekly` produced nothing downstream of it. 8/10 + 8/17 `weekly-timekeeping-analysis` fired but posted nothing (Chrome Gusto scrape). 8/17 `review-obtained-last-week` started 01:25, no post, no failure DM |
| 3b | **Session ended before copy / ran out of context mid-run** | 3 | **July AND August** `monthly-analytics-prestage` — 60-min drop→poll→copy loop ended its session before copying, and the 6 windows shared an end-date filename so they overwrote each other. 2026-05-29 precedent: combined run produced all 25 CSVs but compile/post never ran (why PART1/PART2 exists). 8/21 `vp-deal-of-week-monday-pick` replied "No response requested" to a resume nudge and sat idle forever → **107 of 129 tasks were missing the Execution Contract resume-discipline block**, all patched 8/21 |
| 4 | **Hand-rendered table drift** | 3 documented instances, 1 channel fixed | `#aged-inventory-review`: **8/10** lost its header row + gained a stray fence; **8/24** silently dropped the TOTAL row; **8/31** posted a 1-of-5-store table with **Waynesboro's $123,029.24 Inventory Balance in the Total column** instead of its $9,557.10 aged total, an unbalanced code fence and a duplicated "Sent using Claude" — illegible. Root cause: "the table was re-rendered as free text by the model on every run." Fixed 9/5 with `bin/format_aged_inventory.py` (exit 2 → post nothing). **Explicitly not fixed:** loan, layaway, employee, FPD posts in the same task are still hand-rendered with identical exposure |
| 5 | **Rule 18 withholds / incomplete posts** | Rule created 8/31, 3 real violations fixed | 8/31 Joshua: "we are never supposed to post incomplete or inaccurate data… zero technical garbage anywhere on Slack" — `#aged-inventory-review` 1-of-5, `#loan-review` 4-of-5, `#first-payment-default` 2-of-5, each with an in-channel technical caveat (double violation, Rule 16 repeat). Fixed in `monday-bravo-combined-compile` + `monday-bravo-postcheck`. **Third violation found in the 8/31 sweep of ~53 Slack-posting tasks:** `monthly-analytics-report` was posting on a lenient 26-of-30-CSV / 4-of-5-store threshold → now requires 30/30 and 5/5. Rule 18 gate also legitimately withheld `#first-payment-default` from `monthly-eom-recap` on 9/5 (no complete week in August — Culpeper cell failing all month) and `#pawn-walks` (14/26 days) |
| 6 | **Rule 17 refusals** | 2 | 9/1 `monthly-scrap-rankings` "stopped to object to its own execution contract and never pulled" → August rankings missed entirely, catch-up 9/5 16:22. 8/25 (origin of Rule 17) a session refused to run `bald-rock-15-day-contract` calling it a probable prompt injection on the strength of its `uploads/` path |
| 7 | **Classifier-blocked writes / task creation** | **7 blocked actions** | 9/5: installing the Rule-17 preamble at `_pubaudit/scrap.SKILL.md` blocked; registering `monthly-eom-recap` and `monthly-publication-audit` blocked; the August employee-FINAL re-post blocked (draft left for Joshua); posting 3 of 15 Month-in-Review channels blocked (`#daily-funds-reconcilation`, `#pawn-walks`, `#website`); `ebay_markdown_engine.py --apply` blocked by the desktop permission gate. 9/4: `northwest-registered-agent-daily-check` cron change refused by the auto-mode classifier; `chromeperms`/`taskperms` registry edits + `unified-search-verify` creation all needed Joshua's click. 8/21: `shop-in-store-sync` registration blocked **twice**; 8/16 audit fix commands blocked from writing to the Scheduled folder |
| 8 | **App closed / scheduler didn't fire** | 1 multi-day outage + 1 recurring | **8/18 ~10:30 AM → 8/21 ~08:39 AM: the local Cowork fleet ran NOTHING** — 3 days of daily reports missed. Initially blamed on the Mac being down; **corrected 8/21** — `kern.boottime` proved the machine ran continuously from 8/12 to an unclean reboot 8/21 08:36, so it was the **Claude app** that stopped. Root cause still unconfirmed. Mitigations: `com.valleypawn.claude-keepalive` launchd agent (8:20 PM + 7:35 AM) — which then **exited 126 nightly** (script not executable / needs `~/bin/vp-runner`). Jewelry gap 8/18–8/20 = "app closed at run time"; 8/20 recovered by catch-up, **8/18–8/19 unrecoverable** |
| 9 | **Stale path / stale source** | 4 | 9/1 `monthly-employee-sales-rankings` still pointed at a cloud-era shared folder → improvised with data through 8/30 and the wrong metric ("Total Productivity" instead of Retail Sales Excluding Fees) → **post had to be deleted**. 8/24 `monday-bravo-combined-compile` Step 4 hard-required per-store EOM **CSVs** that stopped being produced 2026-06-22 (EOM moved to .xlsx) → store rankings silently skipped **8/10 and 8/24**. 8/24 `weekly-markdown-verification-review` used `ls -t \| grep \| head -5` against a ~2,200-file Parallels-shared `output/` and got a truncated listing showing only 8/13 files while 8/21 and 8/23 sets existed → false "no fresh data," failure DM, week skipped. Live now: `weekly-store-kpis` Step 2.5 reuse-check depends on `daily-loan-inventory-text`, whose launchd agent is DISABLED |
| 10 | **Duplicate posts / duplicate work** | 4 (all caught by guards) | 9/5 `catchup-scrap-rankings-aug-2026` second invocation hit the duplicate guard at 16:50 and exited. 9/5 `monthly-eom-recap` second same-day run: 0 posted / 13 duplicate-skipped. 9/5 `monthly-employee-sales-rankings` duplicate guard hit at 16:34. **Real damage once:** 9/5 two eBay markdown apply passes ran the same day → up to 63 Culpeper items took **two 10% cuts in one day**; floor held but cadence accelerated a month → `MIN_DAYS_BETWEEN_CUTS=25` added. Structural duplicates removed 8/21: 4 cloud twins were **double-running** (`content-batch-weekly`, `website-trend-daily`, `casual-video-daily`, `publer-analytics-friday`) |
| 11 | **Watcher restarts / Bravo cascade** | ~6 | 8/16 wedged AHK watcher: one 5-store trigger cannot finish 5×8 jewelry categories inside the hardcoded 45-min per-trigger wall → ROA/WAY skipped; **plus** JewelryCaseCountV2 wrong-report class produced clean-looking wrong counts (CUL Rings 43, HAR Pendants 173, HAR Necklaces 25). 8/16 `sold-review` 5/5-store failure from a stranded stacked-dialog state (`_cleanup_stale_claims.ps1` quarantined **95 orphaned claims**; `_restart_watcher_v2.ps1` added). 8/24 the **Monday-specific** intake-detail failure: `IntakeDetail.ahk` couldn't distinguish a zero-intake Sunday from "wrong report loaded," burned 3 retries × 5 stores (~20 min), wedged the watcher and **starved `items-to-price` entirely** — F/F/F on 8/17 and 8/24, clean every non-Monday. 8/30 EnsureStore cascade: CUL/HAR/LEX/ROA all failed aged-inventory, only WAY (last) succeeded → root cause had been documented since 2026-06-07 and never fixed; recovery-to-Dashboard + 2-strike fail-fast shipped 8/31. 8/11 a wedged LEX login screen caused **13 hours** of failed retries. 9/5 watcher restarted twice (PID 12700 → 3028) to register `employee-activity-range` |
| 12 | **Chrome + VM contention / machine melt** | 3 | 8/21 **load average 176 / 171** on the 10-core M1 Max, 14.1/15.3 GB swap, disk 92% full — five concurrent `refresh.sh` chains (~45 workers). Mechanism: **the osascript MCP tool times out on long commands and reports "command failed" while the process keeps running**, so retries stack. Froze Slack web + Chrome renderers repeatedly. Fixes: fcntl lock, `os.nice(10)`, worker cap 4, `perf-guard` agent. Codified rule 8/21: "never drive Chrome while the Parallels VM is pulling." 9/4 root cause #4: iCloud Desktop&Documents **evicted 27,352 of 61,262 files** under `~/Documents/Claude` (data volume 94–97% full) including **47 task SKILL.md files**, 3,813 Bravo Data Extraction files and `.fleet_health_state.json` → `Resource deadlock avoided` in launchd/vp-runner. 9/4 `document-photos-index-refresh` died at a 300 s `osxphotos.PhotosDB()` timeout because the 3:30 AM unified-search refresh churns the same disk |
| 13 | **Model-pin drift** | 2 waves | 8/16 audit: **7 enabled tasks unpinned** (could fire on Fable); one run actually went out on Fable. 8/21: last 11 pinned, "0 unpinned remain of 128." 9/4: **7 tasks had `model:` outside the first frontmatter block** so it was ignored — `mail-brief-reply-executor` ran **94× in 40 h on Opus** |
| 14 | **Watchdog false positives** | 3 | 8/21 `blog-publisher-watchdog` DM'd "no post today" when post 1084 had published at 9:10 AM (public WP.com REST cache lag). 8/24 `weekly-markdown-verification-review` false failure. 7/24→9/4 `backup-health-watchdog` sent a false `offsite=~1000h` CRIT on **every** DM because it judged GitHub freshness by the mtime of a log written only on failure — "a classic Rule 12 violation living inside the watchdog itself" — and then sent **ten identical CRIT DMs 8/26→9/4 with no escalation** |
| 15 | **Contention gate misapplied** | 1 | 8/21 `weekly-markdown-verification-pull` silently skipped twice on a false-BUSY Bravo contention check — it only writes a trigger file and never touches Bravo's screen. Check removed; task reclassified rerun-safe |

**Missed-publication tally, August 2026 (from `PUBLICATION_CALENDAR.md`):** monthly tier 4 of 12 broken — `#company-performance` MISSED (also July), `#employee-performance` posted-then-deleted, `#scrap-rankings` MISSED, `#new-customers` MISSED; `#monthly-gun-audit` last real post 8/3 (June period), 8/16 run produced nothing; `#bonus-goals` July qualifiers not found in channel. Daily/weekly tiers read healthy 8/31–9/5.

---

## 7. Redundancy, overlap, orphans

**Same job twice**
- `monday-bravo-combined-compile` (Mon 8:00, from Sunday's pull) **and** `weekly-store-kpis` (Mon 10:30, its own fresh 5-store EOM pull) both post store performance to `#store-performance`, 2.5 h apart, with a third writer at 9:28 (`weekly-store-perf-canvas-refresh`).
- `weekly-aged-inventory-report` **and** `weekly-aged-inventory-review` — two on-disk unregistered variants of the same report; BUSINESS_OS §8 item 12 has flagged this since the OS was written.
- `#employee-performance` has three writers: compile (Mon MTD), `monthly-employee-sales-rankings` (1st FINAL), `weekly-employee-perf-canvas-refresh` (Mon canvas).
- eBay reporting is split across **Cowork tasks and native launchd agents** that nothing reconciles: `ebay-weekly-channel-audit` (Mon 11:45), `weekly-online-store-audit` (Sun 8:00), `com.valleypawn.ebay-efficiency-weekly` (Fri), `com.valleypawn.ebay-weekly-rankings` (Mon 9:30), `ebay-weekly-quality-fix`, `ebay-title-photo-accuracy-audit`, `ebay-markdown-terminal-weekly` — all touching #ebay-performance/#ebay-listings. The 8/16 audit named the "eBay audit pair" as a live overlap; only the "GA4 double-pull" (fixed 8/3) and the "deal-of-week trio" have been rationalized. The "canvas five-pack" is still five separate dispatches.
- `discount-review` and `sold-review` correctly **share** one pull — the good pattern.
- `preston-interactive-assistant` + `preston-claude-evening-check` are deliberate complements sharing a dedupe file; `com.valleypawn.preston-watch` is a third layer.

**Orphaned / unowned**
- `new-inv-weekly-report` — on disk, unregistered, no other owner. Vendor/new-inventory sell-through, margin, aging and CapEx reporting **is dark**. BUSINESS_OS §8 item 4 still lists "Vendor performance scorecard" as a to-build.
- `daily-loan-inventory-text` — unregistered and its launchd agent DISABLED, but `weekly-store-kpis` Step 2.5 still assumes it runs daily at 7:30 AM. The reuse-check is dead code that forces a redundant EOM pull every Monday.
- `monthly-publication-audit` — **documented as the monthly safety net in two places, exists nowhere.** SKILL.md sits in `Valley Pawn OS/pending-tasks/` awaiting one click.
- eBay negative/neutral feedback: `preston-ebay-feedback-watch` disabled 8/26 as "superseded by `preston-interactive-assistant`," but that task only acts on Preston's Slack requests. Gap ran until `ebay-feedback-reply-weekly` was created (still **unpinned**).
- `#first-payment-default` — the Culpeper `fpd-cohort` cell failed all August (no complete week), which is why the Month-in-Review gate skipped it. BUSINESS_OS §4 marks `fpd-cohort` "⏳ Per-store saved reports incomplete" and §8 item 15 has "~15 min × 5 stores = 75 min once" queued since the OS was written.
- Two BUSINESS_OS §4 pipeline rows — `aged-jewelry-markdown`, `aged-general-merch-markdown` — are **stale entries for handler files that do not exist** (verified 8/13).
- `monthly-analytics-report` still posts to `#store-performance`?? No — removed 9/5. But **`vp-new-customer-report` still posts to `#store-performance` on day 3**, contradicting the 9/5 standing decision that the channel is weekly-only. Flagged to Joshua, unresolved.

**Rollback holds / debris**
- 9 disabled cloud triggers from the 8/21 migration, due for deletion "~8/28" — no deletion recorded.
- 12 disabled `com.valleypawn.vpops.job_*` launchd plists (the pre-Cowork native reporting fleet).
- 51 dead task folders archived to `Scheduled/_archive-20260821/`; the current 12 on-disk-unregistered set is the post-cleanup residue.
- `Scheduled/` still holds loose report artifacts (17 `Loan_Layaway_Review_*.docx`, 11 `employee-sales-rankings-*.xlsx`, `STATUS-*.md`, `.tmp` files, VM screenshots) mixed in with task folders.

**Unpinned tasks still live:** `monthly-eom-recap`, `ebay-feedback-reply-weekly`, `unified-search-verify` (plus the disabled one-shots). Opus pins that look mis-tiered against the Haiku/Sonnet/Opus framework: `monthly-bonus-targets`, `monthly-we-buy-gold-silver-email`, `nightly-chekkit-review-responses`, `annual-board-review`, `dismiss-employee`, `vp-content-batch-weekly`, `vp-comedy-reel-weekly`, `vp-creative-refresh-quarterly`, `vp-hr-compliance-quarterly-review`, `weekly-social-media-content` (disabled).

---

## 8. What the reliability plan and fleet-guardian already do — and their gaps

**`fleet-guardian`** (12:45 PM + 9:45 PM daily, sonnet-5, run logs in `fleet/guardian_runs/`)
- **Step 1** — cron math against the registry: MISSED = last scheduled fire > 20 min ago AND `lastRunAt` older than it.
- **Step 1b** (added 8/21) — output verification against `fleet/expected_outputs.json`: search each entry's channel for its `marker` within cadence + `grace_hours`. This is the layer that catches fires-then-dies-silently, the class that kept the Brevo emails dark 3 weeks. It caught `bald-rock-15-day-contract` on 9/4 with a perfectly healthy `lastRunAt`.
- **Step 2** — classify against `fleet/rerun_manifest.json`: ~78 `rerun_safe`; everything else (unlisted included) is verify-only and is **never** executed — external messaging, publishing, money, HR, Bravo-driving.
- **Step 3** — re-run up to 5 per pass, honoring each task's own duplicate guards, then read the output back (Rule 12).
- **Step 4** — silent when everything recovers; one plain-language DM for unrecovered items only.
- Additive-only, never-guess manifest maintenance; guardian may add verified entries itself.
- **Layer 0 beneath it:** native `com.valleypawn.fleet-health` (13:30 + 22:30, deliberately after each guardian pass) — cron-aware missed-start detection, skip-burst rate, launchd agent state, Claude.app alive, Bravo morning-pull certificate. Detect-and-DM only. Exists because the guardian is itself a Cowork task and dies with the app (the 8/18–8/21 common-mode failure).

**Known guardian gaps**
1. **The 48-hour staleness rule blinds it to monthly misses.** "Ignore any task whose missed fire is more than 48 hours old" means a missed 1st-of-month post is invisible by the 3rd. This is exactly why the entire monthly tier failed unnoticed in July and August. Partially patched 9/5 by adding monthly entries with "since the 1st" semantics — but the 48-h rule itself is unchanged in the SKILL.
2. **Coverage is 38 of ~90 reporting tasks.** Uncovered analytics producers include `daily-items-to-price`, `jewelry-onhand-nightly-pull`, all 5 canvas refreshes, `asset-recovery-daily-refresh`, `vp-dashboard-refresh`, `vp-website-trend-daily-refresh`, `weekly-markdown-verification-review`, `ebay-weekly-channel-audit`, `ebay-markdown-terminal-weekly`, `monthly-bonus-qualifiers`, `monthly-bonus-payout`, `monthly-amazon-store-allocation`, `monthly-eom-recap`. Reliability Plan Phase 2 explicitly lists "extend expected_outputs so fleet-guardian verifies every report task's Slack output, not just the current 2 entries."
3. **Marker false positives.** Documented three times in the manifest itself: `vp-community-weekly` (exact phrase absent but the post was correct), `vp-staff-video-prompt` (a correct open-ask guard-skip is indistinguishable from a miss), `vp-deal-of-week-monday-pick` (marker absent since 7/27 while the actual Brevo campaigns sent fine — "only the Step 8 PUBLIC Slack channel post is failing… root cause not yet found"). An exact-marker search cannot distinguish guard-skip from failure.
4. **Marker absence ≠ correctness.** The manifest verifies *presence*, never *shape*. It would have passed the 8/31 `#aged-inventory-review` post with `$123,029.24` in the Total column. Completeness gate ≠ correctness gate — that gap is what `format_aged_inventory.py` closes, for exactly one of six channel posts.
5. **Verify-only tasks are never recovered**, only noted — correct by design, but it means the highest-value publications (anything Bravo-driving) still depend on their own bespoke watchdogs.
6. **Load-bearing Slack markers block Rule 16 cleanup.** `weekly-markdown-verification-pull`'s dispatch DM reads as technical noise but removing it would silently blind the guardian ("a regression dressed as compliance").
7. **Native agents are outside guardian scope entirely** — the eBay weekly/daily/monthly reporting agents have no output verification at all.

**`SCHEDULED_TASK_RELIABILITY_PLAN.md` (2026-09-04) status**

- **Phase 0 — done or staged.** Model pins fixed on 7 tasks (`bin/fix_model_pins_20260904.py`); pollers moved off the `:00` minute and thinned (~40 fewer dispatches/day); 8–9 AM pile spread across 7 tasks; the "usage cap" label corrected to "3-slot queue wait." **Blocked on Joshua's one click:** `chromeperms_registry_edit.py` (`chromePermissionMode: skip_all_permission_checks` on 27 Chrome/Gusto tasks + `userSelectedFolders` fleet-wide + the northwest cron the classifier refused) and the `claude-keepalive` plist fix (`~/bin/vp-runner` instead of `/bin/bash` → currently exit 126 every run). The taskperms one-shot (697 read-only approvals across 66 tasks) **did** run at 02:10 on 9/4.
- **Phase 1 — launch→exit→verify.** Only `unified-search-verify` (4:50 AM) is live. The other five babysitters — `document-photos-index-refresh`, `jewelry-onhand-nightly-pull` (up to 81 min), `bravo-morning-pull` (40 min), `bald-rock-15-day-contract` (44 min for a daily check), `gdrive-cache-refresh` (63 min) — are unconverted and still hold slots.
- **Phase 2 — not started.** Canvas five-pack merge, 10 AM ops-check merge, Zoom Phone API (needs Joshua's OK on an OAuth app), expected_outputs extension.
- **Phase 3 — not started.** `bin/dispatch_health.py` on launchd every 30 min writing `fleet/DISPATCH_HEALTH.md` — the zero-usage visibility layer that would replace "Joshua has to ask."

**Structural gaps neither layer addresses**
- Hand-rendered tables remain the default. Five of six `monday-bravo-combined-compile` channel posts, every canvas, and nearly every weekly/monthly summary are re-rendered as free text by the model each run. The CHANGELOG says so plainly: "Not audited this pass: the other channel posts in the same task (loan, layaway, employee, FPD) are still hand-rendered tables with the same drift exposure."
- The permission classifier blocks the fleet from repairing itself autonomously — 7 blocked actions on 9/5 alone, including the registration of the monthly audit net that would have caught the failure being audited.
- Backup: Time Machine has produced nothing since **2026-08-25 13:50**; the NAS destination is physically gone; the data volume is 97% full; 11 local snapshots are currently the only backup. Every scheduled report's source data sits on an unbacked disk.
- The 3-slot ceiling is server-side and non-negotiable. Everything else is capacity management around a fleet of 148 enabled tasks and ~8,000 queue-waits a week.