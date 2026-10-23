#!/bin/bash
echo ===== gate check: wrapper must exit silently while dormant
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ebay_inbox_alert.sh" am
echo ===== install dormant agent
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.ebay-inbox-alert
