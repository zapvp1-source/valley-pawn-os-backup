# VP Ops Engine — TRIAGE.md (Phase 0)

**Date:** 2026-07-26
**Scope:** Every folder in `Documents/Claude/Scheduled/` (165 total; 5 are support dirs, not tasks — `_ccr-trigger-export`, `_fpd-archive`, `_run-2026-05-18-csvs`, `_shared`, `_shared-bravo-data`) plus the cloud-only CCR trigger export. 160 task folders classified below by 4 parallel read-agents (SKILL.md + frontmatter + scripts).

**Tiers** (per BUILD_SPEC.md §3):
- **Tier 1** — must run without Claude (this project's build targets)
- **Tier 2** — judgment/content, stays on Claude, non-critical
- **NativeAlready** — launchd/AHK/script already, no LLM in runtime path — no action
- **DeadStale** — superseded/one-off/diagnostic — Joshua decides deletions, no action from this project
- **DO-NOT-TOUCH** — hardened/explicitly off-limits

---

## 0. DO-NOT-TOUCH

| Task | Why |
|---|---|
| `daily-funds-verification` | **WORKS — DO NOT TOUCH (Joshua 2026-07-26).** Out of scope entirely, per Hard Rule #1. |
| `monday-bravo-combined-run` | Rule #4 hardened infra — the Monday orchestrator; every weekly review depends on it. Job E (trigger_dropper) runs alongside it (05:30, before its ~05:38), never edits it. |

---

## 1. Tier 1 — build targets for VP Ops Engine

### 1a. Direct matches to BUILD_SPEC §4 Phase-1 jobs (A–G)

| Spec Job | Matching existing task(s) | Cadence | Destination |
|---|---|---|---|
| A `job_store_rankings` | `monday-store-rankings` **and** `weekly-store-kpis` (see duplicate flag §5) + `weekly-store-perf-canvas-refresh` | Mon ~10:30–11:15 AM | #store-performance |
| B `job_aged_inventory` | `weekly-aged-inventory-report` (+ `monday-bravo-combined-compile` also posts aged inventory — see §5) + `weekly-aged-inventory-canvas-refresh` | Weekly Mon | #aged-inventory-review |
| C `job_employee_rankings` | `weekly-employee-sales-rankings` (+ `monday-bravo-combined-compile` also posts employee — see §5); `monthly-employee-sales-rankings` is the separate monthly rollup, not a duplicate | Weekly Mon | #employee-performance |
| D `job_loan_layaway_review` | `weekly-loan-layaway-review` (+ `monday-bravo-combined-compile` also posts loan+layaway — see §5) + `weekly-loan-layaway-manager-dms` (downstream) + `weekly-loan-review-canvas-refresh` + `weekly-layaway-review-canvas-refresh` | Weekly Mon | #loan-review + #layaway-review |
| E `trigger_dropper` | No existing equivalent — net new, coexists with `monday-bravo-combined-run` per spec's duplicate-pull guard | New, 05:30 ET | — |
| F `job_daily_loan_inv_text` | `daily-loan-inventory-text` — native `daily_run.sh`/`compute.py` already exist; wrap, don't rewrite | Daily 7:30 AM ET | iMessage Joshua + Preston |
| G `watchdog` | No existing unified equivalent (many per-job watchdogs exist, see 1b) — net new, heartbeat-based | Daily 10:30 AM | DM Joshua only |

**⚠️ See §5 before building A–D** — each has a legacy standalone task AND a `monday-bravo-combined-compile` code path both claiming to post to the same canonical channel. Per Joshua's 2026-07-26 Slack audit both are currently broken/inconsistent (store rankings dead since 3/23, aged inventory canonical format never posted, employee+loan/layaway died in the 7/23–25 outage) — so golden-test the new renderer against the **most recent real Slack post** in each channel (per BUILD_SPEC §6), not against either legacy script's code.

### 1b. Other Tier-1 candidates found (recurring, mechanical, data-driven) — NOT in Phase-1 scope, backlog for later phases

Full-category watchdogs/mechanics already running that a later phase could port to the pure-Python engine. Per Rule #4 / spec discipline, **do not touch or rebuild these in Phase 1** — Phase 1 is jobs A–G only. Listed here so nothing is lost.

| Task | Cadence | What / destination |
|---|---|---|
| `asset-recovery-daily-refresh` | Daily 7:15 PM | Asset Recovery HTML artifact from Bravo EOM |
| `bald-rock-monday-briefing` | Mon 8 AM | Bald Rock STR briefing → #airbnb |
| `blog-publisher-watchdog` | Mon & Thu 2 PM | Verifies blog posted |
| `bravo-health-watchdog` | 2x daily | Bravo Health Gate — critical pipeline enabler |
| `brevo-preflight-watchdog` | Daily 7 AM | Brevo campaign tracking/UTM enforcement |
| `chekkit-new-review-alert` | Hourly 9–9 | New review → #google-reviews |
| `chekkit-unanswered-alert` | Daily 8 AM M–Sat | Unanswered Chekkit tally per store |
| `chekkit-weekly-review-requests` | Tue 4:40 PM | Chekkit review requests + Brevo import |
| `controlio-offline-agent-check` | Daily | Employee monitoring uptime |
| `daily-clockin-check` | M–Sat 10:15 AM | Gusto clock-in → #general |
| `daily-cloudcover-check` | Weekdays+Sat 10 AM | Pandora Cloud Cover status |
| `daily-intake-margin` / `daily-intake-prestage` | Daily 6:30/7:30 AM | Intake margin grading → #pawn-walks |
| `daily-items-to-price` | Daily 8 AM | Unpriced inventory → #items-to-price |
| `dashboard-data-collector` | Hourly | Dashboard Sheet aggregator (meta-monitoring) |
| `ebay-photo-enhance-done-notify` | Daily | eBay photo backlog notify |
| `email-analytics-weekly` | Fri 9 AM | Brevo click analytics → #email-campiagns |
| `eom-bravo-gl-export` | Monthly 5th | Consolidated GL export → QBO |
| `fb-token-health-check-daily` | Daily 3 AM | FB token health |
| `ffl-web-form-to-slack` | Every 15 min | FFL form → #ffl-transfer-notifications |
| `funds-verification-watchdog` | Daily 6:45 PM | Watchdog for daily-funds-verification |
| `gusto-keep-alive` | Every 2h | Gusto session keep-alive |
| `layaway-yield-weekly` | Mon 11:15 AM | Layaway Yield % → #layaway-review canvas |
| `mm-merchandisers-daily-scan` | Daily | M&M order scan → new-inv-intake |
| `monday-bravo-combined-compile` | Weekly Mon | Part 2 of combined run — posts 4 reports (see §5) |
| `monday-bravo-postcheck` | Mon 8:15 AM | Verify+backfill combined reports |
| `monthly-amazon-store-allocation` | Monthly 6th | Amazon spend by store |
| `monthly-analytics-prestage`/`-report`/`-watchdog` | Monthly | YoY analytics → #company-performance/#store-performance |
| `monthly-bonus-payout`/`-qualifiers`/`-targets` | Monthly 10th/EOM | Bonus computation chain |
| `monthly-cpa-report` | Monthly | CPA categorization |
| `monthly-employee-sales-rankings` | Monthly 1st | Final monthly employee rankings |
| `monthly-reconciliation-report` | Monthly | QBO recon → CPA |
| `monthly-sold-inventory-refresh` | Monthly 1st | Sold inventory CFO analysis → #cfo-analytics |
| `monthly-top-sales-review` | Monthly | Top sales → #store-performance |
| `new-inv-weekly-report` | Weekly Mon | New inventory sell-through → #new-inventory |
| `pawn-walk` / `sold-review` | Daily 6:30/7:45 AM | Intake/sold margin checks |
| `review-obtained-last-week` | Mon 3 AM | Review counts → #google-reviews |
| `sales-tax-monthly-update` | Monthly 6th | Sales tax workbook |
| `scheduled-task-history-logger` | Every 15 min | Task history logger |
| `tuesday-supply-checkout`/`-summary` | Tue | Amazon checkout automation (<$350 rule) |
| `vp-ai-search-health-check` | Weekly | Schema/NAP check → #ai-marketing |
| `vp-dashboard-refresh` | Nightly | Dashboard KPI parse+deploy |
| `vp-deal-of-week-monday-pick`/`-prompt`/`-reminder` | Mon | Deal-of-week mechanics |
| `vp-new-customer-report` | Monthly 3rd | New customer counts → #new-customers |
| `vp-os-github-nightly-backup` | Nightly | GitHub backup |
| `vp-publer-analytics-friday` | Fri 4 PM | Publer analytics digest |
| `vp-website-deals-weekly` / `-shop-nightly` / `-trend-daily-refresh` | Daily/Weekly | Website publish jobs |
| `vp-weekly-spot-price-update` | Daily 7 AM | Gold/silver spot price |
| `vsp-nics-fee-monthly-check` | Monthly 5th | NICS fee check |
| `weekly-aged-inventory-canvas-refresh`/`-employee-perf-canvas-refresh`/`-layaway-review-canvas-refresh`/`-loan-review-canvas-refresh`/`-store-perf-canvas-refresh` | Mon ~9:20–9:28 AM | Slack Canvas refreshes (companion artifacts, not duplicate posts) |
| `weekly-analytics-summary` | Mon 2:30 AM | GA4 weekly → #website |
| `weekly-loan-layaway-manager-dms` | Mon 9 AM | Per-store manager DMs |
| `weekly-loan-portfolio-refresh` | Mon 7 AM | Loan portfolio analysis |
| `weekly-payroll-to-qbo` | Weekly | Payroll → QBO JE |
| `weekly-returns-summary` | Mon 1 AM/9 AM | Returns summary — **needs OCR of handwritten forms, not pure formatting; flag for later** |
| `weekly-timekeeping-analysis` | Mon 2 AM/9 AM | Timekeeping summary |
| `weekly-website-kpi-artifact-refresh` | Weekly | Website KPI artifact |
| `wordpress-token-keepalive` | 2x daily | WP OAuth keepalive |
| `nightly-desktop-cleanup` | Nightly 3 AM | Desktop file sort (mechanical, not business analytics) |

---

## 2. Tier 2 — stays on Claude (judgment/content, non-critical)

`amazon-return`, `annual-board-review`, `bald-rock-15-day-contract`, `bald-rock-guest-reviews`, `brightlocal-weekly-sync-alerts-check`, `chekkit-review-responder`, `daily-distributor-application-monitor`, `daily-dress-code-check` (vision), `daily-ffl-transfer-check`, `daily-mail-unsubscribe`, `daily-social-media-content`, `daily-supply-order`, `dismiss-employee`, `ebay-title-enrichment-backlog`, `ebay-title-photo-accuracy-audit` (vision), `ebay-weekly-quality-fix`, `monthly-capability-drift-audit`, `monthly-gun-audit-report` (vision/OCR), `monthly-gun-audit-summary` (vision/OCR, overlaps report — see §5), `monthly-we-buy-gold-silver-email`, `nightly-chekkit-review-responses`, `preston-ebay-feedback-watch`, `salt-run-monthly-seo-audit`, `salt-run-quarterly-phase-check`, `salt-run-weekly-analytics`, `saturday-facebook-posts`, `sunday-checklist-summary`, `thursday-youtube-employee-clips`, `valley-pawn-blog-publisher`, `vp-ai-search-autofix`, `vp-ai-visibility-autofix`, `vp-ai-visibility-metrics`, `vp-casual-video-daily`, `vp-content-batch-postflight`, `vp-content-batch-preflight`, `vp-content-batch-weekly`, `vp-deals-social-wednesday`, `vp-hr-compliance-quarterly-review`, `vp-hr-policy-monthly-sync`, `weekly-jacksonville-property-search`, `weekly-st-augustine-property-search`, `wednesday-facebook-posts`, `weekly-email-cleanup`, `weekly-social-media-content`, `weekly-youtube-shorts`, `zoom-phone-activation-check`.

Plus **`hiring-inbox-watch`** (cloud-only CCR trigger, no local folder) — per BUILD_SPEC §7, stays on Claude.

---

## 3. Native already (no action)

| Task | Note |
|---|---|
| `vp-social-publisher` | Shared Publer executor — deterministic script, dry-run/live modes, no generation in this component |
| `weekly-ebay-sales-ranking` | Actual job is a native LaunchAgent + webhook; this task is just a monitor/nudge wrapper |
| `oura-daily-import` | Native bash+Python script; Claude just relays 2 numbers |

---

## 4. Dead/Stale (Joshua decides deletions — no action taken)

| Task | Superseded by / why |
|---|---|
| `bald-rock-auto-contract` | Superseded by `bald-rock-15-day-contract` |
| `bald-rock-signing-status` | Subsumed by `bald-rock-15-day-contract` + `bald-rock-monday-briefing` |
| `chekkit-watcher-heal-2026-06-10` | One-off remediation, self-disable design |
| `cloud-cover-keep-alive` | Vague placeholder; superseded by `daily-cloudcover-check` |
| `distributor-setup-monitor` | Near-duplicate of `daily-distributor-application-monitor` (Tier2) |
| `domain-transfer-check` | Domain transfer (GoDaddy→WP.com) completed months ago; should've self-disabled |
| `fpd-history-backfill` | One-time bootstrap utility |
| `gusto-qbo-first-sync-check` | One-time verification tied to 6/12 chart-of-accounts change |
| `itp-validate-restart-2026-06-09` | One-shot infra validation |
| `loan-portfolio-final-pass-2026-05-21` | Explicitly DISABLED in its own file |
| `model-check-temp` | One-time diagnostic probe |
| `monday-bravo-reminder` | Superseded by pipeline-driven `monday-store-rankings` (2026-05-23 change) |
| `nics-selector-autofix` | Self-disabling one-shot validation |
| `overnight-closing-reports-smoke-2026-05-29` | One-time smoke test |
| `postmaster-reputation-check-2026-06-23` | One-off dated diagnostic |
| `srj-watcher-restart-oneshot-2026-06-08` | One-off dated infra fix |
| `vp-bonus-revenue-fix-and-gold-yoy` | One-off correction/backfill project |
| `vp-content-batch-postflight-catchup-2026-07-20` | One-off catch-up run |
| `vp-content-batch-preflight-catchup-2026-07-20` | One-off catch-up run |
| `vp-content-batch-weekly-catchup-2026-07-20` | One-off catch-up run |
| `vp-mj-reachability-diagnostic-2026-07-21` | One-time diagnostic |
| `vp-new-customer-report-backfill-retry` | One-off historical backfill retry |
| `vp-publish-pending-batch-2026-07-20` | One-off stuck-batch cleanup |
| `weekly-fpd-ranking` | File states it stalled and was folded into `monday-bravo-combined-compile` (2026-07-22); "do not schedule it" |
| `weekly-new-deal-request` | Explicitly DISABLED 2026-05-28, superseded by `vp-deal-of-week-monday-prompt` |
| `weekly-timekeeping-analysis-mcp` | File states "Not scheduled. Not live." — parallel MCP-based candidate awaiting Joshua's cutover approval over the live `weekly-timekeeping-analysis` |
| `weekly-valley-pawn-email-campaign` | Explicitly DISABLED 2026-05-28, superseded by 12-week pre-staged Brevo calendar + deal-of-week tasks |
| `winback-build-and-schedule-2026-06-17` | One-off campaign build tied to that date |

**Empty/unreadable folder:** `weekly-aged-inventory-review` — 0 bytes, no SKILL.md or any file. Likely an abandoned duplicate of `weekly-aged-inventory-report` + `weekly-aged-inventory-canvas-refresh`. No action; flagging for Joshua.

---

## 5. Overlaps/duplicates flagged for clarification (not resolved by this triage)

1. **`monday-store-rankings` vs `weekly-store-kpis`** — both Monday, both parse the same 5 EOM CSVs into the same 8-category store ranking, both post to #store-performance. Likely true duplicates (one legacy, one newer). Needs Joshua/live-Slack-history check on which has actually been posting.
2. **`monday-bravo-combined-compile`** posts Aged Inventory + Loan + Layaway + Employee reports to the same 4 channels that `weekly-aged-inventory-report`, `weekly-employee-sales-rankings`, and `weekly-loan-layaway-review` also independently target. Unclear which path is currently live vs. legacy — per the spec's own Slack audit, evidence suggests **neither is currently working reliably** (aged inventory canonical format has never posted at all). Recommend: don't try to determine "the" source — golden-test Jobs B/C/D against the most recent real Slack post per channel, per BUILD_SPEC §6, and let both legacy paths continue running until cutover per Rule #4.
3. **`monthly-gun-audit-report` vs `monthly-gun-audit-summary`** — overlapping vision/OCR gun-audit tasks with conflicting date fields (7th vs 15th vs 16th). Both Tier 2 either way (out of scope for this project), flagging for Joshua's own cleanup.
4. **`distributor-setup-monitor`** (DeadStale) vs **`daily-distributor-application-monitor`** (Tier2) — same vendor list, same Gmail-scan pattern, same recipient. Likely the same job built twice.

None of the above are touched by this project — additive-only. Listed so Job A–D builders don't assume a single clean source of truth exists yet.

---

## 6. Bravo data-source freshness (Tier-1 Job A–D inputs) — verified 2026-07-26

| Cell | Most recent file date | Note |
|---|---|---|
| `end-of-month` (5 stores) | 2026-07-21 | Fresh — pipeline itself is healthy, survived the 7/23–25 outage (it's Claude-independent) |
| `aged-inventory-summary` (5 stores) | 2026-07-13 | Stale ~2 weeks — last Monday cycle (7/20 or 7/21) never ran, consistent with spec's outage narrative |
| `employee-activity` (5 stores) | 2026-07-01 | Stale — MTD file, needs a fresh pull before Job C can run |
| `loans-75-days-past-due` (5 stores) | 2026-07-13 | Stale ~2 weeks |
| `layaways` (5 stores) | 2026-07-13 | Stale ~2 weeks |
| `safe-register-journal` (5 stores) | 2026-07-23 | Fresh — confirms `daily-funds-verification`'s data path is intact and untouched |

**Conclusion:** the pipeline (watcher/AHK) itself is not broken — it's Claude-side triggering that stopped during the outage. Job E's trigger-dropper will need to pull fresh data for all 5 cells × 5 stores before Jobs A–D can golden-test against current numbers; don't test against the stale 7/13 files as "current."

---

## 7. Cloud-only CCR triggers cross-check

Compared `_ccr-trigger-export/ccr_triggers_export_2026-07-16.md` (17 triggers, stale export) against the local folder list — all named triggers in the export have matching local SKILL.md folders except:
- `dashboard-data-collector` trigger — explicitly noted in the export itself as DELETED 2026-07-16, replaced by native launchd job `com.valleypawn.dashboarddatacollector`. Confirms the local `dashboard-data-collector` folder's SKILL.md is now legacy/reference only for the hourly Sheet-aggregation task (still Tier1 candidate per §1b, but verify at build time whether it's the launchd version or the old CCR version still firing).
- `hiring-inbox-watch` (added 2026-07-23, per BUSINESS_OS) postdates this export and has no local folder — cloud-only, Tier2, out of scope.

No other cloud-only orphans found in the stale export; a live CCR trigger list was not independently pulled (out of scope for Phase 0 — the local Scheduled/ folders are the authoritative task inventory per BUILD_SPEC §3).

---

## Next: STATE.md

Per BUILD_SPEC §2, create `STATE.md` (per-job cutover state: shadow | verified | LIVE) when Phase 1 build begins on Job A.
