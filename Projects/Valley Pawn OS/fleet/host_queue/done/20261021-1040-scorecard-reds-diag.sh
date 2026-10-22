#!/bin/bash
# 2026-10-21 scorecard reds: read-only diagnostics (logs, agent load state, scorecard detail). Nothing posted.
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/host_diag.sh" agents
bash "$BIN/tail_any.sh" weekly-website-health-audit.log 60
bash "$BIN/tail_any.sh" ebay-weekly-channel-audit.log 60
bash "$BIN/tail_any.sh" vp-website-trend-daily-refresh.log 30
bash "$BIN/tail_any.sh" fleet-scorecard.log 30
bash "$BIN/tail_any.sh" daily-clockin-check.log 40
bash "$BIN/tail_any.sh" daily-dress-code-check.log 40
bash "$BIN/tail_any.sh" daily-cloudcover-check.log 40
python3 "$BIN/agent_log_tail.py" weekly-website-health-audit 40
python3 "$BIN/agent_log_tail.py" vp-ebay-channel-audit 40
python3 "$BIN/agent_log_tail.py" vp-website-trend-daily-refresh 20
python3 "$BIN/fleet_scorecard.py" --render 2026-10-20 --detail
python3 "$BIN/fleet_scorecard.py" --today --detail
python3 "$BIN/agent_log_tail.py" weekly-website-health-audit.out 40
python3 "$BIN/agent_log_tail.py" vp-ebay-channel-audit.out 40
bash "$BIN/tail_any.sh" host-queue.log 15
