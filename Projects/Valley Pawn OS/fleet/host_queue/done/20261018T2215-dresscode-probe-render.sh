#!/bin/bash
echo "=== probe ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/dress_code_check.py" --probe
echo "=== render headed off-screen, Monday store set (Sunday: stores closed, mechanics test) ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/dress_code_check.py" --render --diag --date 2026-10-19
