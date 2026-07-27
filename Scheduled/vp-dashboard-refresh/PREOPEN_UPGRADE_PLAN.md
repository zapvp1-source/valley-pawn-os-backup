# Pre-open data freshness — Joshua's standard (set 2026-07-20)

REQUIREMENT: every number on the enterprise dashboard current at least daily, BEFORE stores open (9:00 AM ET).

## Done (live now)
- New Claude scheduled task `vp-dashboard-preopen-refresh` (trig_01T47FnLYqkVoGNyp3ozmoan), daily 12:30 UTC / 8:30 AM ET: re-parses Slack feeds → kpis.json → redeploys vp-dashboard.pages.dev. Complements the existing nightly refresh; idempotent.

## Remaining gap (next build session — read enterprise-map first)
The dashboard can only be as fresh as its SOURCE data. Daily feeds (funds, items-to-price, intake margin, chekkit, company loan/inventory balance) are already daily. But per-store PAST-DUE LOAN % and LAYAWAY rows come from the WEEKLY Monday Bravo loan/layaway review — so those rows can be up to 6 days old even after a refresh.

To meet the daily-pre-open standard for loans/layaway:
1. Add a DAILY early-morning pipeline pull of the loan-base/layaway past-due data (Bravo Data Extraction pipeline drop-trigger pattern — same mechanism daily_run.sh uses for company-kpis at 7:30 AM; loan handlers already exist and are registered). Target drop ~6:45 AM ET so CSVs land by ~7:30.
2. Add a small parser step (native script preferred, additive — do NOT modify the weekly review task) that converts those CSVs into the pastDue/layaway rows of site/data/kpis.json (or posts a standard-format report the refresh task already parses).
3. Keep the Monday weekly review exactly as is (Slack posts, reports) — this is additive per Rule #4.
4. Verify end-to-end: dates.loans / dates.layaway on the dashboard show TODAY by 8:45 AM ET.

Constraint reminders: additive only; pipeline work requires AHK compile-check + healthy-VM test window; schedule any new local jobs via ~/bin/vp-runner (TCC).
