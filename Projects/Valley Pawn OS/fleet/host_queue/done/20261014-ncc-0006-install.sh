#!/bin/bash
echo ===== gate check: wrappers must exit silently while dormant
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/cloudcover_check.sh"
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ebay_channel_audit.sh"
echo ===== install dormant agents
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.cloudcover-check
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.ebay-channel-audit
echo ===== CATCHUP render
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/catchup.py" --render
