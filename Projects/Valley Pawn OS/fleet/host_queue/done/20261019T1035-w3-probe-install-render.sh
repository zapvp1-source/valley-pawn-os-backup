#!/bin/bash
set +e
echo "=== probe: agents / drive / google / live ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w3_probe.py" drive
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w3_probe.py" google
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w3_probe.py" live
echo "=== install DORMANT (vp_live gate, no native_live file) ==="
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.monthly-employee-rankings
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.mobilepawn-participation
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.loan-layaway-outcomes
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.bravo-user-audit
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.mobilepawn-app-social
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.ebay-ratings-sweep
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.scrap-rankings-monthly
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.monthly-analytics-report
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.monthly-analytics-watchdog
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.eom-gl-export
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.eom-gl-watchdog
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.sales-tax-monthly
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.bonus-close-pull
echo "=== renders (September data on disk - nothing posted, no pulls) ==="
echo "--- employee rankings"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/monthly_employee_rankings.py" 2026-09 --render
echo "--- mobilepawn participation"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/mobilepawn_participation.py" 2026-09 --render
echo "--- loan layaway outcomes - script --test mode"
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/loan_layaway_outcomes_monthly.sh" --render
echo "--- bravo user audit - no --send"
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_user_audit_monthly.sh" --render
echo "--- mobilepawn app social - dry-run, next month"
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/mobilepawn_app_social.sh" --render
echo "--- ebay ratings post - October file"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ebay_ratings_post.py" 2026-10 --render
echo "--- scrap rankings"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/scrap_rankings_monthly.py" 2026-09 --render
echo "--- monthly analytics report - plus TEST sheet via Sheets API"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/monthly_analytics_report.py" 2026-09 --render --sheet-too
echo "--- monthly analytics watchdog"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/monthly_analytics_watchdog.py" 2026-09 --render
echo "--- eom gl export - August is the last complete GL set"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/eom_gl_export.py" 2026-08 --render
echo "--- eom gl watchdog - September"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/eom_gl_watchdog.py" 2026-09 --render
echo "--- sales tax - August"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/sales_tax_monthly.py" 2026-08 --render
echo "--- bonus close pull"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bonus_close_pull.py" 2026-09 --render
echo "=== agents after install ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w3_probe.py" agents
echo "=== dormant wrappers exit silently - gate ==="
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/monthly_employee_rankings.sh"
echo "wrapper rc=$?"
