#!/bin/bash
# Install weekly read-only FFL drift agent (Sun 02:40) + first live run writing Compliance/FFL_DRIFT.md (FFL audit 2026-10-21)
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.ffl-drift
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ffl_drift_check.py"
