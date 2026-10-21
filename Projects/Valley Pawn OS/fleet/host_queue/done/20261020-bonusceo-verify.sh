#!/bin/bash
# 2026-10-20 bonus close (active roster) + CEO scorecard readiness — READ-ONLY Slack checks, bonus render on a copy (no post, no DM)
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_slack.py" info C0C06PWLQCR
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vp_slack.py" last C0C06PWLQCR 3
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/bonus_month_close.py" 2026-09 --render
