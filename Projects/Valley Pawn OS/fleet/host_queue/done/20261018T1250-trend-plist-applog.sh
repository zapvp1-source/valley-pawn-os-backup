#!/bin/bash
echo "=== install website-trend plist (02:40 + 12:40) ==="
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.website-trend-refresh
echo "=== claude app log tail ==="
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" applog
echo "=== chekkit review log tail ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/agent_log_tail.py" chekkit-new-review-alert 6
