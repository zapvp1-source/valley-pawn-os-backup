#!/bin/bash
set +e
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/reg_shape.py"
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/inspect_path.py" "$HOME/Documents/Claude/Scheduled" --lines 2
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" 2>/dev/null
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" registry
