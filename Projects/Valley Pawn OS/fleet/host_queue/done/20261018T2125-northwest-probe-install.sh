#!/bin/bash
echo "=== probe ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/northwest_check.py" --probe
echo "=== install dormant ==="
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.northwest-check
echo "=== render (expected: stops at the sign-in state, nothing posted) ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/northwest_check.py" --render --diag
