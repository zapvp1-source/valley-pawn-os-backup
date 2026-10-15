#!/bin/bash
echo ===== HEALTH 2026-10-04
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/health_weekly_digest.py" --render --day 2026-10-04
echo ===== HEALTH today
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/health_weekly_digest.py" --render
echo ===== WEB 10/12 again
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/website_health_audit.py" --render --scan "/Users/joshuadavis/Documents/Claude/Projects/Website/AUDIT_2026-08-22/weekly_scan_2026-10-12.json"
