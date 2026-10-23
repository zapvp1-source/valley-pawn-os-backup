#!/bin/bash
set -e
BASE="$HOME/Documents/Claude/Projects/Valley Pawn OS"
echo "=== host_diag.sh all ==="
bash "$BASE/bin/host_diag.sh" all 2>&1
echo "=== task_lastrun.py ==="
python3 "$BASE/bin/task_lastrun.py" 2>&1
echo "=== reg_shape.py ==="
python3 "$BASE/bin/reg_shape.py" 2>&1
