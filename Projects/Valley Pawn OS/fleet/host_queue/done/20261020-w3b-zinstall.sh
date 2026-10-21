#!/bin/bash
# wave 3 second pass - install DORMANT (vp_live gate, NO native_live file) + the scrap year-file guard (live by design)
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.new-customer-report
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.gun-audit-monthly
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.entity-compliance
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.bonus-month-close
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.eom-recap
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.ceo-monthly-scorecard
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.comms-drift-monthly
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.hr-policy-sync
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.scrap-year-guard
sleep 20
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w3_probe.py" agents
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w3_probe.py" live
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/scrap_year_guard.py" --render
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/catchup.py" --render
