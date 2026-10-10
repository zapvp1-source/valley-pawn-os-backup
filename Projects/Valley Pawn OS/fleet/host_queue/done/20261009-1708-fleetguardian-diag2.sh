#!/bin/bash
set +e
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" all
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/task_preflight.py"
