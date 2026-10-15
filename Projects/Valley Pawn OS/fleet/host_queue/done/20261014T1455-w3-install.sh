#!/bin/bash
set +e
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.website-trend-refresh
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.weekly-analytics-summary
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.shop-weekly-report
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/website_trend_refresh.sh"
echo "trend wrapper rc=$? (0 + no log line = dormant gate held)"
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/weekly_analytics_summary.sh"
echo "weekly wrapper rc=$?"
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/shop_weekly_report.sh"
echo "shop wrapper rc=$?"
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/tail_any.sh" vp-website-trend-daily-refresh.log 5
