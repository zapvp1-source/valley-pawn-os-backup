#!/bin/bash
# Nov 1 monthly rehearsal — part B: wrapper --render runs (September period) for the Bravo-data agents. No pulls.
echo "=== RENDER monthly-analytics-report ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/monthly_analytics_report.sh" 2026-09 --render
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" monthly-analytics-report.log 45
echo "=== RENDER employee-rankings ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/monthly_employee_rankings.sh" 2026-09 --render
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" monthly-employee-sales-rankings.log 45
echo "=== RENDER scrap-rankings ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/scrap_rankings_monthly.sh" 2026-09 --render
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" monthly-scrap-rankings.log 40
echo "=== RENDER eom-gl-export ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/eom_gl_export.sh" 2026-09 --render
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" eom-bravo-gl-export.log 20
echo "=== RENDER sales-tax ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/sales_tax_monthly.sh" 2026-09 --render
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" sales-tax-monthly-update.log 12
echo "=== RENDER bonus-close-pull ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bonus_close_pull.sh" 2026-09 --render
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" bonus-month-close-pull.log 30
echo "=== RENDER mobilepawn-participation ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/mobilepawn_participation.sh" 2026-09 --render
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" monthly-mobilepawn-participation.log 25
echo "=== RENDER loan-layaway-outcomes ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/loan_layaway_outcomes_monthly.sh" --render --month 2026-09
echo "rc=$?"
echo "=== RENDER new-customer-report ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_new_customer_report.sh" 2026-09 --render
echo "rc=$?"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" vp-new-customer-report.log 20
echo "=== RENDER bravo-user-audit ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_user_audit_monthly.sh" --render --month 2026-09
echo "rc=$?"
echo "=== RENDER ebay-ratings-sweep ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ebay_ratings_sweep.sh" --render 2026-10
echo "rc=$?"
echo "=== RENDER mobilepawn-app-social ==="
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/mobilepawn_app_social.sh" --render
echo "rc=$?"
echo "=== B DONE ==="
