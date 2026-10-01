# Native migration plan — before the 2026-10-06 Cowork → cloud move

Goal (Joshua 9/30): move every task that can run without Claude onto native launchd agents, so the
fleet is not exposed to Cowork product changes; identify obsolete tasks. Source: `fleet/task_triage.json`
(115 enabled Cowork tasks, SKILL-feature scan) + SKILL reads + run history.

## A. Mechanical → native (this week, in this order)
1. daily-funds-verification — `bin/funds_verification.py` BUILT; parser verified on real phrasing; waits
   on the ops bot being invited to the 5 private funds channels, then a render against 9/29's known
   $13,500 ledger, then switch (never both at once — double post).
2. The Monday chain (Oct 6 is a Monday): monday-bravo-combined-run, -cell-gapfill, -combined-compile,
   -postcheck, the 5 weekly canvas refreshes, nics-weekly-mtd-ranking, weekly-store-kpis,
   layaway-yield-weekly, weekly-markdown-verification-pull/-review, bonus-pace-monday. Data already
   native (monday_pull.sh); comms_engine.py already renders/posts loan/layaway/employee/FPD.
3. daily-items-to-price; vp-website-shop-nightly; qbo-api-token-refresh; scrap-monthly-bravo-approval-watch;
   scrap-monthly-bravo-manifest-stage; health-weekly-digest; weekly-online-store-audit; monthly-ebay-ratings-sweep.
4. Monthly (they run 10/1 on the current setup; convert after): monthly-employee-sales-rankings,
   monthly-scrap-rankings, nics-monthly-ranking, monthly-gift-card-store-credit, monthly-mobilepawn-participation,
   bonus-month-close-pull, monthly-eom-recap, monthly-publication-audit, mobilepawn-app-social-monthly.

5. daily-store-audit-digest (added 2026-09-30, registered as Cowork Mon–Sat 09:40): already mechanical —
   native form = `daily_audit_digest.py` then `vp_slack.py post U03BB52MDSA --file daily-audit/<date>.mrkdwn.txt`
   (+ U03BWMEM9GR once Preston is switched on), skip if `<date>.sent` exists, write `.sent`. Disable the Cowork
   task in the same step — never both (double post).

6. monthly-loan-layaway-outcomes (added 2026-09-30, registered as Cowork, 2nd of month 10:30): already mechanical —
   native form = `python3 bin/loan_layaway_outcomes.py --send` on the 2nd at 10:30 (the script writes the outbox
   envelope to U03BB52MDSA and the `<ym>.sent` marker itself, and refuses if `.sent` exists). Convert before the
   11/2 run (the 10/2 run is still on the current setup). Disable the Cowork task in the same step — never both.

## B. Hybrid — Mac gathers the data, Claude writes/reads
jewelry-onhand-nightly-pull & -catchup (Claude reads handwritten sheets), ebay-weekly-channel-audit,
vp-dashboard-refresh, asset-recovery-daily-refresh, ceo-weekly/monthly-scorecard, monthly-analytics-report,
marketing-ceo-briefing-weekly, yield-by-asset-class-monthly, vp-new-customer-report, precious-metals.

## C. Stays Claude (browser, vision, judgment, or a cloud-only connector)
dress code, cloudcover, clock-in (Gusto connector), Chekkit browser tasks, Bald Rock tasks, Northwest,
hiring inbox, insurance tasks, CEO mail brief, morning brief, deal-of-week tasks, Gusto signature chase,
supply prep/summary/order, AI-search/visibility, presence & website audits, HR/capex/board/drift/hygiene
reviews, connector-health, fleet-guardian, sales tax, EOM GL export, entity compliance, reviews watchdogs.

## D. Obsolete candidates (verify, then retire — never on assumption)
- monday-bravo-combined-run + monday-bravo-cell-gapfill: duplicate the native monday_pull (same 5
  reports, Sunday) and the gapfill needs the Mac connector every run. Retire when the native compile lands.
- monday-bravo-postcheck: the native compile will verify itself.
- funds-verification-watchdog: redundant once funds is native (it ledgers its own failures).
- gusto-keep-alive: 48 Claude runs/day to keep a browser login warm for clock-in's FALLBACK path only
  (clock-in's primary path is the Gusto connector). Cut to 1–2/day or retire.
- scheduled-task-model-audit-weekly: audits per-task model pins; moot once tasks run in the cloud.
- chekkit-culpeper-sms-ticket-watch: temporary support-ticket watcher (every 30 min); disables itself
  when Chekkit resolves the Culpeper texting issue.
- preston-ebay-feedback-watch: already re-disabled 9/30 (superseded 8/26).
