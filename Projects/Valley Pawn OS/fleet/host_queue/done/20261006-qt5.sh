#!/bin/bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/quiet_triage.py" --grep-agents run_daily_v5
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/quiet_triage.py" --grep-agents HealthOS
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/quiet_triage.py" --grep-file "~/Library/Application Support/HealthOS/bin/run_daily_v5.sh" "mv "
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/quiet_triage.py" --grep-file "~/Library/Application Support/HealthOS/bin/run_daily_v5.sh" "oura_latest"
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/quiet_triage.py" --grep-file "~/Library/Application Support/HealthOS/bin/run_daily_v5.sh" "[Ll][Oo][Cc][Kk]"
