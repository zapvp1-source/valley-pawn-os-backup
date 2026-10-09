#!/bin/bash
echo ===== parity morning 10/5
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/parity_check.py" C0B1PEW0C30 ":bar_chart: _Daily Response Summary — October 5, 2026_" "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/test_output/parity/morning-1005.txt"
echo ===== EOD 2026-09-29 replay
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_unanswered.py" eod --render --day 2026-09-29
echo ===== EOD today so far
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_unanswered.py" eod --render
echo ===== MORNING tomorrow-preview of today
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_unanswered.py" morning --render --day 2026-10-08
echo ===== REVIEW now
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_review_alert.py" --render
