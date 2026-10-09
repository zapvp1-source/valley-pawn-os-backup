#!/bin/bash
echo ===== live files present:
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" agents
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.chekkit-unanswered-alert
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.chekkit-unanswered-eod
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.chekkit-review-alert
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.daily-audit-digest
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.shop-refresh
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.deal-of-week-prompt
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.deal-of-week-reminder
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/catchup.py" --render
