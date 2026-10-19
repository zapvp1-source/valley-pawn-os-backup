#!/bin/bash
echo "=== render 5: cookie-domain diag (names only) + headless comparison ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/dress_code_check.py" --render --diag --date 2026-10-19
echo "=== headless ==="
set -a
DC_HEADLESS=1
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/dress_code_check.py" --render --date 2026-10-19
