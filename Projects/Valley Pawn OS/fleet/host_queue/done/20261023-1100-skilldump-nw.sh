#!/bin/bash
# Joshua 10/23 cleanup: read the local Northwest + capex task instructions before retiring anything.
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" northwest-registered-agent-daily-check 5000
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" quarterly-capex-sweep 2500
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/northwest_check.py" --probe
