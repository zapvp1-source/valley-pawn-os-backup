#!/bin/bash
set +e
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/weekly_analytics_summary.py" --render --cached
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/shop_weekly_report.py" --render
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/google_regrant.sh" verify
