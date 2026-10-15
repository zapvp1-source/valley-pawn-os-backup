#!/bin/bash
echo ===== MODEL AUDIT render
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/model_audit_weekly.py" --render
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.staff-video-prompt
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.publer-friday
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.thursday-email-watchdog
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.health-weekly-digest
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.website-health-audit
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.model-audit-weekly
echo ===== CATCHUP render
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/catchup.py" --render
