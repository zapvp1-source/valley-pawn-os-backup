#!/bin/bash
# wave 3 second pass - RENDERS against the last real (Oct) outputs. Nothing posted, no pulls, no production writes.
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_new_customer_report.py" 2026-09 --render
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/gun_audit_monthly.py" --period 2026-09 --render
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bonus_month_close.py" 2026-09 --render
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ceo_monthly_scorecard.py" 2026-09 --render
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/entity_compliance_monthly.py" --render --asof 2026-10-01
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/hr_policy_sync_monthly.py" --render --since 2026-08-01 --until 2026-10-01
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/comms_drift_monthly.py" --render --asof 2026-10-03
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/monthly_eom_recap.py" 2026-09 --render
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/scrap_year_guard.py" --render
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/gun_audit_monthly.sh"
