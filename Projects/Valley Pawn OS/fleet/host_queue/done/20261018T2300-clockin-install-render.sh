#!/bin/bash
echo "=== probe ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/clockin_check.py" --probe
echo "=== install dormant (com.valleypawn.clockin-check, Mon-Sat 10:15; gated by vp_live.sh) ==="
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.clockin-check
echo "=== render headed (expected: login state, nothing posted) ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/clockin_check.py" --render --diag
