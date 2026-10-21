#!/bin/bash
# eBay full audit 2026-10-20 — read-only: registry state of all tasks + launchd agent health
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/task_lastrun.py" --all
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/agent_doctor.py"
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ebay_ratings_pull.sh"
