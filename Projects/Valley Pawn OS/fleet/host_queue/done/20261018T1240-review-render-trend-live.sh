#!/bin/bash
echo "=== chekkit review render (new gate) ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_review_alert.py" --render --hours 48 --all
echo "=== website trend LIVE ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/website_trend_refresh.py" --live
echo "=== mail brief probe ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/mail_unread.py" --hours 6
