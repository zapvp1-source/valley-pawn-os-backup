#!/bin/bash
echo "=== chekkit-new-review-alert.log ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/agent_log_tail.py" chekkit-new-review-alert 40
echo "=== vp-website-trend-daily-refresh.log ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/agent_log_tail.py" vp-website-trend-daily-refresh 30
echo "=== host-queue.log ==="
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" host-queue.log 25
echo "=== outbox / sms relay ==="
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" outbox-flush.log 20
echo "=== agents ==="
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" agents registry
echo "=== chekkit review render ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_review_alert.py" --render --hours 48 --all
echo "=== website trend render ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/website_trend_refresh.py" --render
