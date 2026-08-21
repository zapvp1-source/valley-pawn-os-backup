# Scheduled Task Audit — 2026-08-21 (~9:30 AM ET; corrected + migration addendum ~10:15 AM)

> **CORRECTION (confirmed by Joshua + evidence, ~9:35 AM):** The outage below was NOT a usage-cap problem. The Mac Studio itself was down — it booted at 8:36 AM on 8/21 (sysctl kern.boottime), Claude.app started 8:47, and the skip log shows ZERO skips recorded on 8/19–8/20 (an app that's off can't record skips). The 1,264 `global_limit` skips stamped on 8/21 are the relaunch catch-up burst being throttled, not a standing cap crisis. Background cap pressure does exist (~150–250 skips/day on 8/14–8/17) but is a secondary issue, not the outage cause. Sections below are preserved as written for the record; read them with this correction.

Follow-up to `Scheduled_Task_Audit_2026-08-16.md`. Verified against outputs (Rule 12), not run records. Three layers checked: cloud triggers (17), local Cowork fleet (110 registered / 103 enabled), native launchd agents (7 loaded).

## Headline finding — local fleet outage Aug 18 → Aug 21

**The local Cowork scheduled-task layer ran NOTHING from ~2026-08-18 10:30 AM ET until ~2026-08-21 8:39 AM ET (~3 full days).** Evidence, all cross-confirmed:

- Registry (`scheduled-tasks.json`): every daily task's `lastRunAt` stops between 8/18 04:21 and 8/18 14:21 UTC; nothing again until today 12:39 UTC.
- Recorded skips grew 1,113 (8/18 live-state) → **1,989** now, reason `global_limit` (usage cap), with skips still being recorded minutes before this audit.
- Bravo pipeline `output/`: newest CSV 8/18 12:02. `triggers/processed/`: newest 8/18 08:03. Morning-pull certificate: last one is `_morning_pull_status_2026-08-18.txt` — none for 8/19, 8/20, 8/21.
- Slack: `#sold-review` last post 8/18 (covering 8/17). No pawn-walk, sold-review, items-to-price, discount-review, funds-verification, or jewelry-count posts since.
- `BUSINESS_OS.md` LIVE STATE last refreshed 8/18; CHANGELOG last entry 8/17 (business-os-daily-refresh down with everything else).

**Partial recovery is underway this morning without intervention:** scheduler resumed at ~8:39 AM ET (chekkit alerts, clock-in check, supply tasks, dress-code, blog publisher, bald-rock-15-day all ran 8:39–9:12 AM); the Bravo watcher restarted 8:38 AM, health-gated PASS, and jewelry-onhand 8/20 eval triggers were dropped 9:05 AM (CUL claimed/in flight, HAR/LEX/ROA/WAY queued). But `global_limit` skips are STILL firing for other tasks, so the cap is still binding intermittently.

**Missed work in the outage window (daily tasks, 3 misses each):** bravo-morning-pull, pawn-walk, sold-review, daily-items-to-price, discount-review, daily-funds-verification (+watchdog), jewelry-onhand-nightly-pull (8/19 data likely unrecoverable in Bravo same-day terms; 8/20 backfilling now), vp-dashboard-refresh, vp-website-shop-nightly, vp-website-trend-daily-refresh (cloud copy DID run — see below), vp-os-github-nightly-backup, oura-daily-import, zoom-voicemail-alert/eod, indeed-applicant-outreach, northwest-registered-agent-daily-check, gdrive-cache-refresh, nightly-desktop-cleanup, asset-recovery-daily-refresh, business-os-daily-refresh, and the weekly Monday set already ran 8/17 (before the outage) so weeklies were NOT hit — next Monday 8/24 is at risk only if the cap persists.

## Cloud triggers (claude.ai scheduled tasks) — HEALTHY

13 enabled, all fired on schedule; last_fired timestamps match cron for every one (Precious Metals Settlement 8/20✓, Bravo Pre-Flight Relaunch 8/21 04:05✓, nightly-bravo-restart 8/21 04:03✓, hiring-inbox-watch 8/20 18:10✓, vp-website-trend-daily-refresh 8/21 06:34✓, vp-casual-video-daily 8/19✓, vp-publer-analytics-friday 8/14✓ (due today 4 PM), vp-ai-visibility-autofix 8/14✓ (due today 9:32), vp-ai-search-autofix 8/17✓, vp-content-batch-weekly 8/17✓, eBay Ratings Sweep 8/1✓, monthly-scrap-rankings + Quarterly Capex Sweep pending first/next run — normal).

4 disabled cloud triggers (residue, no action urgent):

| Trigger | Disabled since | Coverage |
|---|---|---|
| sold-review (cloud) | 8/13 | Migrated to local task — which was then cap-blocked; see outage |
| In-Store Inventory Slack→Website Sync | 8/12 | Local `vp-website-shop-nightly` owns it |
| vp-dashboard-preopen-refresh | 8/2 | Local `vp-dashboard-refresh` owns it |
| Salt Run Weekly Analytics | ~8/3 | **NO owner in either layer** (local `salt-run-weekly-analytics` is unregistered). Gap if Salt Run reporting is still wanted. |

## Native launchd agents — HEALTHY

All 7 loaded agents show last exit 0, including `com.valleypawn.unified-search-refresh` (exit 126 TCC failure from the 8/16 audit is FIXED — now exiting 0).

## Still outstanding from the 8/16 audit

1. **7 never-run tasks**: task-hygiene-sweep, eom-bravo-gl-export-watchdog, vp-comms-drift-monthly-check, nics-monthly-ranking, annual-board-review, vp-hr-compliance-quarterly-review, jewelry-pull-watchdog (new since 8/16). The three that missed August first-runs still have never fired.
2. **Model pins** on the 7 unpinned tasks — staged commands in 8/16 report §6, still unapplied.
3. **63 unregistered task folders + disabled residue** — cleanup still pending.
4. **Usage-cap capacity decision (Joshua)** — flagged 8/16 as ~1,100 skips; it has now escalated from "tasks occasionally skip" to "the entire local fleet went dark for 3 days." This is the single decision blocking everything else: either plan capacity increases, or the fleet gets triaged down to fit the cap (fewer/consolidated tasks, more native launchd agents that don't consume Claude usage, staggered schedules).

## Recommended next actions (in order)

1. Joshua: capacity/plan decision (see #4 above) — everything else is downstream.
2. Let today's self-recovery finish; tonight's cycle will confirm. Spot-check tomorrow ~8 AM: morning-pull certificate for 8/22 present + #sold-review post.
3. One targeted backfill worth doing once cap allows: daily-funds-verification for 8/18–8/20 (money-movement verification, cheap, CSV-driven) and the EOM GL export watchdog proof-run before month-end.
4. Apply the staged 8/16 §6 fixes (model pins, folder cleanup) in a session with Scheduled-folder write approval.
5. ~~Decide whether Salt Run weekly analytics is retired or re-registered~~ — RESOLVED: Joshua retired it; cloud trigger deleted, folders archived (see addendum).

---

# ADDENDUM — Cloud→Local Migration + Folder Cleanup (executed 2026-08-21, ~9:25–10:10 AM ET)

Joshua directed mid-session: delete Salt Run weekly tasks, move ALL cloud scheduled tasks to local, and clean up folders. All three executed.

## Redundancy findings (Joshua asked)

- `nightly-bravo-restart` ≡ `Bravo Pre-Flight Relaunch (~4 AM ET)` — word-for-word the same job (same script, same steps, same 4 AM run). Merged into ONE local task: **bravo-preflight-relaunch** (daily 4:00 AM ET).
- 4 cloud tasks were exact twins of already-enabled local tasks and had been double-running: vp-content-batch-weekly, vp-website-trend-daily-refresh (daily GA4 double-pull), vp-casual-video-daily, vp-publer-analytics-friday (ran twice on 8/14). Cloud copies DELETED.
- 3 disabled cloud residue triggers (sold-review, In-Store Inventory sync, vp-dashboard-preopen-refresh) — local tasks own these jobs. DELETED.
- The eBay tasks are NOT redundant with each other (monthly public-ratings sweep vs Preston's personal-account watch vs weekly listing-quality audits) — all kept.
- Flag for later: locally there are now THREE Bravo morning-prep tasks (4:00 AM relaunch, pre-7AM `bravo-prestaging-7am`, 6:50 AM `bravo-morning-pull` hygiene+gate). Kept all three deliberately (different failure windows); the 4 AM one may be collapsible into prestaging after a clean proving week.

## Migration (8 jobs, cloud → local Cowork tasks, all pinned claude-sonnet-5)

| New/updated local task | Schedule (ET, local cron) | Source |
|---|---|---|
| precious-metals-settlement-handler | daily 9:00 AM | new folder, cloud prompt adapted |
| quarterly-capex-sweep | 9:00 AM, 1st of Jan/Apr/Jul/Oct | new folder |
| bravo-preflight-relaunch | daily 4:00 AM | new folder — merges the redundant cloud pair |
| monthly-ebay-ratings-sweep | 10:00 AM, 1st | new folder |
| hiring-inbox-watch | 10a/12p/2p/4p/6p Mon–Sat | new folder |
| monthly-scrap-rankings | 4:30 AM, 1st | existing folder, registered |
| vp-ai-visibility-autofix | Fri 9:30 AM | existing folder, registered — local run RESTORES the GA4/Facebook/Sheets access the cloud version had permanently lost (its own prompt had been requesting this move since 7/20) |
| vp-ai-search-autofix | Mon 8:30 AM | existing folder, registered |

Registration required quiescing the entire Claude.app process tree (a background helper holds the scheduler registry in memory and clobbers file edits — two earlier attempts were reverted this way). Final procedure: full pkill of Claude.app tree → 30s mtime-quiet check → atomic registry edit → relaunch → verified 8/8 entries survived the daemon's own rewrite. Local registry now 118 tasks. Backups: `scheduled-tasks.json.bak-cloudmigration-20260821-*` (next to the registry) and `Projects/.migration-staging/registry-backup-*.json`. All scripts + logs in `Projects/.migration-staging/`.

## Cloud state after cutover

**0 enabled cloud tasks.** 9 remain DISABLED as rollback holds for the migrated set — delete them after one clean proving week (~8/28). Note: a concurrent precious-metals session re-created its own cloud trigger at 14:02 UTC mid-migration (with a new device-reachability guard); it was caught and disabled too.

## Folder cleanup ("clean up folders")

51 never-registered task folders moved to `~/Documents/Claude/Scheduled/_archive-20260821/` (move-only, reversible — trash the folder to make it permanent). Includes all three salt-run folders per Joshua. KEPT 9 folders that live code still references: daily-intake-margin + daily-intake-prestage (referenced by pawn-walk), daily-loan-inventory-text, mm-merchandisers-daily-scan + new-inv-weekly-report (cross-referenced + Bravo docs), weekly-aged-inventory-report + weekly-employee-sales-rankings + weekly-loan-layaway-review (referenced by monday-bravo-combined-compile / layaway-yield-weekly), and dashboard-data-collector (the LOADED launchd agent com.valleypawn.dashboarddatacollector executes collect.sh inside it — archiving it would have broken a live agent).

## Proving checklist (next 7 days)

1. Tomorrow ~4:05 AM: bravo-preflight-relaunch ran (registry lastRunAt / Bravo up).
2. Tomorrow ~9:05 AM: precious-metals local run; certificate `_morning_pull_status_2026-08-22.txt` CLEAN; #sold-review posts.
3. Sat 10 AM: hiring-inbox-watch local runs (Preston DM only if new applicants).
4. Fri 8/28 9:30 AM: vp-ai-visibility-autofix local run — first run with restored GA4/Facebook/Sheets access.
5. Mon 8/24 8:30 AM: vp-ai-search-autofix local run.
6. 9/1: scrap-rankings 4:30 AM, eBay ratings 10 AM (monthlies' first local firing).
7. After all pass: delete the 9 disabled cloud triggers.
