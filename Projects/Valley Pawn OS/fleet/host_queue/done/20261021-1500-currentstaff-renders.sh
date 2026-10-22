#!/bin/bash
# 2026-10-21 fleet-wide current-staff / no-Davis filter: Mac-only renders (render mode, nothing posted). Compare vs prior posts.
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ceo_monthly_scorecard.py" 2026-09 --render
echo "rc=$?"
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/monthly_eom_recap.py" 2026-09 --render --only C0AN6TNA4ES
echo "rc=$?"
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/missed_call_report.py" --render --week 2026-10-12
echo "rc=$?"
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_unanswered.py" morning --render --day 2026-10-20
echo "rc=$?"
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_ops.py" assign-stale --render
echo "rc=$?"
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ebay_ship_alert.py" --slot am --render
echo "rc=$?"
