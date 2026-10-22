#!/bin/bash
# Nov 1 monthly rehearsal — part A: arm the publish guard (170 min, scoped to the wave-3 monthly tasks only) and run
# the agents whose LIVE path is safe for the September period (each one either hits its duplicate guard or diverts).
echo "=== ARM GUARD ==="
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_dryrun.py" on --minutes 170  --task monthly-analytics-report --task monthly-employee-sales-rankings --task monthly-scrap-rankings --task eom-bravo-gl-export --task monthly-analytics-watchdog --task sales-tax-monthly-update --task vp-hr-policy-monthly-sync --task entity-compliance-check --task monthly-mobilepawn-participation --task monthly-ebay-ratings-sweep --task monthly-eom-recap --task bonus-month-close-pull --task eom-bravo-gl-export-watchdog --task monthly-loan-layaway-outcomes --task vp-new-customer-report --task vp-comms-drift-monthly-check --task monthly-bravo-user-audit --task ceo-monthly-scorecard --task bonus-month-close --task monthly-gun-audit-report --task mobilepawn-app-social-monthly --task ebay-ratings-pull --task loan-layaway-outcomes --task bravo-user-audit --reason "Nov 1 monthly rehearsal (September period), 2026-10-21"
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_dryrun.py" status
echo "=== bravo foreground / pipeline state before ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" agents
echo "=== LIVE 1 monthly-analytics-watchdog 2026-09 ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/monthly_analytics_watchdog.sh" 2026-09
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" monthly-analytics-watchdog.log 12
echo "=== LIVE 2 eom-gl-watchdog 2026-09 ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/eom_gl_watchdog.sh" 2026-09
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" eom-bravo-gl-export-watchdog.log 8
echo "=== LIVE 3 sales-tax 2026-09 ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/sales_tax_monthly.sh" 2026-09
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" sales-tax-monthly-update.log 8
echo "=== LIVE 4 mobilepawn-participation 2026-09 ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/mobilepawn_participation.sh" 2026-09
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" monthly-mobilepawn-participation.log 6
echo "=== LIVE 5 ebay-ratings-sweep 2026-10 ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ebay_ratings_sweep.sh" 2026-10
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" monthly-ebay-ratings-sweep.log 6
echo "=== LIVE 6 new-customer-report 2026-09 ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_new_customer_report.sh" 2026-09
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" vp-new-customer-report.log 8
echo "=== LIVE 8 gun-audit 2026-09 (no sheet) ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/gun_audit_monthly.sh" --period 2026-09 --no-sheet
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" monthly-gun-audit-report.log 8
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_dryrun.py" status
echo "=== A DONE ==="
