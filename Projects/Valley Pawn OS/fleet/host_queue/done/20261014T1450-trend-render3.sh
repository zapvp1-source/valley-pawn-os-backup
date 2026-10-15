#!/bin/bash
set +e
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/website_trend_refresh.py" --render
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/shop_weekly_report.py" --render
