#!/bin/bash
set +e
echo "=== probes (no browser)"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/northwest_check.py" --probe
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/clockin_check.py" --probe
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/dress_code_check.py" --probe
echo "=== cloudcover_check.py --render --diag on pw-vp"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/cloudcover_check.py" --render --diag
echo "rc=$?"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_browser.py" exit-type
