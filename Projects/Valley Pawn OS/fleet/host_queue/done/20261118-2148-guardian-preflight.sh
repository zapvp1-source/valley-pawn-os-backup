#!/bin/bash
# read-only: fleet-guardian 21:45 pass — registry shape + preflight table for missed-run detection
echo "=== reg_shape ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/reg_shape.py"
echo "=== task_preflight (enabled only, default table) ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/task_preflight.py"
