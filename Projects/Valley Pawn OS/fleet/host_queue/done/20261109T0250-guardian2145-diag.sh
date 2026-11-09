#!/bin/bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/task_preflight.py"
echo "---REG_SHAPE---"
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/reg_shape.py"
echo "---HOST_DIAG_ALL---"
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" all
