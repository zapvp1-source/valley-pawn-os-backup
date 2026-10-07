#!/bin/bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_sim.py"
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/log_triage.py" --days 7
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/catchup.py" --render
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" missed_call_text/run.log 200
