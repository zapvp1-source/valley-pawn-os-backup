#!/bin/bash
echo "=== host_diag.sh all ==="
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" all
echo "=== task_lastrun.py ==="
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/task_lastrun.py"
echo "=== reg_shape.py ==="
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/reg_shape.py"
