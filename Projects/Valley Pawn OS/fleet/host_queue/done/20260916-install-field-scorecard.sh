#!/bin/bash
# HOST JOB (runs once via bin/host_queue_run.sh on the host, outside Claude).
# FLEET_FREEZE_2026-09-16.md Phase 0.4 — install the native Field Scorecard agent.
set +e
U=$(id -u)
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
BIN="$OS/bin"; FLEET="$OS/fleet"; LA="$HOME/Library/LaunchAgents"
mkdir -p "$HOME/Library/Logs/valleypawn"
echo "=== field-scorecard install start $(date) ==="

echo; echo "--- exec bits ---"
chmod +x "$BIN/field_scorecard.py" "$BIN/field_scorecard_run.sh"
ls -la "$BIN/field_scorecard.py" "$BIN/field_scorecard_run.sh"

echo; echo "--- dry run (no DM, no history write) ---"
/usr/bin/python3 "$BIN/field_scorecard.py" --dry-run 2>&1
echo "dry-run rc=$?"

echo; echo "--- real run (writes fleet/FIELD_SCORECARD.md + history) ---"
/usr/bin/python3 "$BIN/field_scorecard.py" 2>&1
echo "run rc=$?"

echo; echo "--- INSTALL field-scorecard agent (every 30 min) ---"
cp "$FLEET/com.valleypawn.field-scorecard.plist" "$LA/com.valleypawn.field-scorecard.plist"
launchctl bootout gui/$U/com.valleypawn.field-scorecard 2>/dev/null
launchctl bootstrap gui/$U "$LA/com.valleypawn.field-scorecard.plist" 2>&1 && echo "field-scorecard bootstrapped"
sleep 3
launchctl list | grep -E "field-scorecard|registry-guard"

echo; echo "--- post-state ---"
tail -5 "$HOME/Library/Logs/valleypawn/field-scorecard.log" 2>&1
echo "=== field-scorecard install done $(date) ==="
