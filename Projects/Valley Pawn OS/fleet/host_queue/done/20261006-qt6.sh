#!/bin/bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_sim.py"
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_sim.py" --mutate
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/log_triage.py" --days 7
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/catchup.py" --render
