#!/bin/bash
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_dryrun.py" status
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/task_lastrun.py"
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/task_preflight.py" --json
