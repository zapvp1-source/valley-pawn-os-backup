#!/bin/bash
# SWITCH ON missed-call-text (Joshua 2026-09-24). Retry of 1148 job, which the allow-list refused for chained lines.
set +e
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.missed-call-text
sleep 130
bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" agents
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/agent_log_tail.py" missed-call-text 40
