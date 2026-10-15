#!/bin/bash
set +e
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" vp-website-trend-daily-refresh 40000
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" weekly-analytics-summary 40000
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" vp-website-shop-weekly-report 40000
