#!/bin/bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_scorecard.py" --render 2026-10-13 --detail
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/fleet_scorecard.py" --today --detail
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/log_triage.py" --days 7
