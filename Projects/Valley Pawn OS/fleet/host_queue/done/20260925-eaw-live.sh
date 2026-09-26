#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/install_agent.sh" com.valleypawn.email-analytics-weekly
bash "$BIN/email_analytics_weekly.sh"
python3 "$BIN/agent_log_tail.py" zoom-voicemail-alert 4
