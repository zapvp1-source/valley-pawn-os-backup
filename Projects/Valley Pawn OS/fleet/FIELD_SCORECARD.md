# Field Scorecard — Tier-1 publications

Native, launchd, zero-Claude-usage (`bin/field_scorecard.py`). Verifies real Slack/file output against each publication's cadence + grace period — never just a scheduled task's `lastRunAt` (Rule 12). This is the single source of truth for FLEET_FREEZE_2026-09-16.md Rule 6 ("working" = every row here OK for 7 consecutive days).

Generated: 2026-09-18 10:24:34 ET

| Task | Status | Expected | Note |
|---|---|---|---|
| daily-cloudcover-check | MISSED | Thu 09/17 10:25 |  |
| daily-dress-code-check | MISSED | Thu 09/17 10:30 |  |
| daily-unopened-email-eval | MISSED | Thu 09/17 18:00 |  |
| layaway-yield-weekly | MISSED | Mon 09/14 11:15 |  |
| monday-bravo-cell-gapfill | MISSED | Sun 09/13 20:30 | file missing: ~/Documents/Claude/Projects/Valley Pawn OS/monday-gapfill/2026-09-13.md |
| monday-bravo-combined-compile | MISSED | Mon 09/14 08:00 |  |
| monday-bravo-postcheck | MISSED | Mon 09/14 08:00 |  |
| monthly-publication-audit | MISSED | Wed 09/02 10:00 | file missing: ~/Documents/Claude/Projects/Valley Pawn OS/fleet/publication_audits/2026-09-02.json |
| monthly-publication-audit | MISSED | Fri 09/04 10:00 | file missing: ~/Documents/Claude/Projects/Valley Pawn OS/fleet/publication_audits/2026-09-04.json |
| nics-weekly-mtd-ranking | MISSED | Mon 09/14 09:30 |  |
| review-obtained-last-week | MISSED | Mon 09/14 09:00 |  |
| weekly-returns-summary | MISSED | Mon 09/14 09:00 |  |
| weekly-store-kpis | MISSED | Mon 09/14 10:30 |  |
| bald-rock-15-day-contract | DM-SURFACE | Fri 09/18 04:08 | DMs Joshua via the Cowork bot; not readable by vp_ops_engine — re-point in Phase 1 |
| bonus-month-close | DM-SURFACE | Thu 09/10 09:00 | DMs Joshua via the Cowork bot; not readable by vp_ops_engine — re-point in Phase 1 |
| bonus-month-close-pull | DM-SURFACE | Tue 09/01 11:30 | DMs Joshua via the Cowork bot; not readable by vp_ops_engine — re-point in Phase 1 |
| bonus-pace-monday | DM-SURFACE | Mon 09/14 09:35 | DMs Joshua via the Cowork bot; not readable by vp_ops_engine — re-point in Phase 1 |
| bonus-paid-verify | DM-SURFACE | Mon 09/14 10:00 | DMs Joshua via the Cowork bot; not readable by vp_ops_engine — re-point in Phase 1 |
| bravo-health-watchdog | INFRA | — | infrastructure task — no field publication to score (registry-guard/fleet-health cover its health) |
| bravo-morning-pull | INFRA | — | infrastructure task — no field publication to score (registry-guard/fleet-health cover its health) |
| bravo-preflight-relaunch | INFRA | — | infrastructure task — no field publication to score (registry-guard/fleet-health cover its health) |
| bravo-prestaging-7am | INFRA | — | infrastructure task — no field publication to score (registry-guard/fleet-health cover its health) |
| business-os-daily-refresh | INFRA | — | infrastructure task — no field publication to score (registry-guard/fleet-health cover its health) |
| ceo-mail-brief | INFRA | — | infrastructure task — no field publication to score (registry-guard/fleet-health cover its health) |
| ceo-monthly-scorecard | NO COVERAGE | — | Tier-1 publication with no expected_outputs.json entry yet — add one verified against a real post (additive-only) |
| ceo-weekly-scorecard | NO COVERAGE | — | Tier-1 publication with no expected_outputs.json entry yet — add one verified against a real post (additive-only) |
| chekkit-unanswered-alert | PENDING | Fri 09/18 08:00 | due 11:00, grace not yet elapsed |
| chekkit-unanswered-eod-followup | OK | Thu 09/17 19:00 |  |
| daily-clockin-check | PENDING | Fri 09/18 10:15 | due 13:15, grace not yet elapsed |
| daily-funds-verification | OK | Thu 09/17 18:00 |  |
| daily-items-to-price | PENDING | Fri 09/18 08:00 | due 12:00, grace not yet elapsed |
| discount-review | PENDING | Fri 09/18 08:25 | due 12:25, grace not yet elapsed |
| eom-bravo-gl-export | NO COVERAGE | — | Tier-1 publication with no expected_outputs.json entry yet — add one verified against a real post (additive-only) |
| eom-bravo-gl-export-watchdog | NO COVERAGE | — | Tier-1 publication with no expected_outputs.json entry yet — add one verified against a real post (additive-only) |
| fleet-guardian | OK | Thu 09/17 12:45 |  |
| fleet-guardian | OK | Thu 09/17 21:45 |  |
| funds-verification-watchdog | NO COVERAGE | — | Tier-1 publication with no expected_outputs.json entry yet — add one verified against a real post (additive-only) |
| google-reviews-post-watchdog | NO COVERAGE | — | Tier-1 publication with no expected_outputs.json entry yet — add one verified against a real post (additive-only) |
| jewelry-onhand-catchup | NO COVERAGE | — | Tier-1 publication with no expected_outputs.json entry yet — add one verified against a real post (additive-only) |
| jewelry-onhand-nightly-pull | UNVERIFIED | Thu 09/17 20:30 | slack error: channel_not_found (bot needs a one-time /invite to this channel, or channel_id is stale) |
| jewelry-pull-watchdog | NO COVERAGE | — | Tier-1 publication with no expected_outputs.json entry yet — add one verified against a real post (additive-only) |
| monday-bravo-combined-run | DM-SURFACE | Sun 09/13 18:00 | DMs Joshua via the Cowork bot; not readable by vp_ops_engine — re-point in Phase 1 |
| monthly-analytics-prestage | NO COVERAGE | — | Tier-1 publication with no expected_outputs.json entry yet — add one verified against a real post (additive-only) |
| monthly-analytics-report | OK | Tue 09/01 01:45 |  |
| monthly-analytics-watchdog | NO COVERAGE | — | Tier-1 publication with no expected_outputs.json entry yet — add one verified against a real post (additive-only) |
| monthly-employee-sales-rankings | OK | Tue 09/01 02:00 |  |
| monthly-eom-recap | OK | Tue 09/01 10:30 |  |
| monthly-gun-audit-report | UNVERIFIED | Wed 09/16 02:30 | slack error: not_in_channel (bot needs a one-time /invite to this channel, or channel_id is stale) |
| monthly-scrap-rankings | OK | Tue 09/01 04:30 |  |
| nics-monthly-ranking | OK | Tue 09/01 09:30 |  |
| pawn-walk | PENDING | Fri 09/18 07:15 | due 11:15, grace not yet elapsed |
| precious-metals-settlement-handler | PENDING | Fri 09/18 09:00 | due 13:00, grace not yet elapsed |
| sales-tax-monthly-update | NO COVERAGE | — | Tier-1 publication with no expected_outputs.json entry yet — add one verified against a real post (additive-only) |
| sold-review | PENDING | Fri 09/18 07:45 | due 11:45, grace not yet elapsed |
| sunday-checklist-summary | NO COVERAGE | — | Tier-1 publication with no expected_outputs.json entry yet — add one verified against a real post (additive-only) |
| unified-search-index-refresh | INFRA | — | infrastructure task — no field publication to score (registry-guard/fleet-health cover its health) |
| unified-search-verify | INFRA | — | infrastructure task — no field publication to score (registry-guard/fleet-health cover its health) |
| vp-new-customer-report | OK | Thu 09/03 07:00 |  |
| vp-os-github-nightly-backup | INFRA | — | infrastructure task — no field publication to score (registry-guard/fleet-health cover its health) |
| weekly-aged-inventory-canvas-refresh | CANVAS | Mon 09/14 09:26 | canvas F0BHDL6AULU — freshness = its 'as of slack_date:' heading; not scored natively yet (Phase 1) |
| weekly-employee-perf-canvas-refresh | CANVAS | Mon 09/14 09:24 | canvas F0BH9UK284S — freshness = its 'as of slack_date:' heading; not scored natively yet (Phase 1) |
| weekly-layaway-review-canvas-refresh | CANVAS | Mon 09/14 09:22 | canvas F0BJ48BMZGQ — freshness = its 'as of slack_date:' heading; not scored natively yet (Phase 1) |
| weekly-loan-layaway-manager-dms | DM-SURFACE | Mon 09/14 09:00 | DMs Joshua via the Cowork bot; not readable by vp_ops_engine — re-point in Phase 1 |
| weekly-loan-review-canvas-refresh | CANVAS | Mon 09/14 09:20 | canvas F0BH6BJ0PK7 — freshness = its 'as of slack_date:' heading; not scored natively yet (Phase 1) |
| weekly-markdown-verification-pull | DM-SURFACE | Sun 09/13 19:00 | DMs Joshua via the Cowork bot; not readable by vp_ops_engine — re-point in Phase 1 |
| weekly-markdown-verification-review | OK | Mon 09/14 09:35 |  |
| weekly-store-perf-canvas-refresh | CANVAS | Mon 09/14 09:28 | canvas F0BH6S9U5FX — freshness = its 'as of slack_date:' heading; not scored natively yet (Phase 1) |
| weekly-timekeeping-analysis | OK | Mon 09/14 09:00 |  |
