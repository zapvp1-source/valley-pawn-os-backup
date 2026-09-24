#!/bin/bash
# Render-test all three (no publishing), then install.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== backup_health --render ====="
bash "$BIN/backup_health.sh" --render
echo "===== oura_import --render ====="
bash "$BIN/oura_import.sh" --render
echo "===== health_intake --render ====="
bash "$BIN/health_intake.sh" --render
echo "===== install ====="
bash "$BIN/install_agent.sh" com.valleypawn.backup-health
bash "$BIN/install_agent.sh" com.valleypawn.oura-import-check
bash "$BIN/install_agent.sh" com.valleypawn.health-intake
python3 "$BIN/agent_doctor.py"
