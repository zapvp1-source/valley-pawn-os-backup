#!/bin/bash
# SWITCH ON missed-call-text (Joshua 2026-09-24: "ok lets switch it on"). Installs the launchd agent,
# then waits for two cycles and shows it is loaded and what it did.
set +e
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
bash "$OS/bin/install_agent.sh" com.valleypawn.missed-call-text
echo "--- launchctl"; launchctl list | grep missed-call-text
sleep 130
echo "--- launchctl after 130s"; launchctl list | grep missed-call-text
echo "--- agent logs"; ls -la "$HOME/Library/Logs/valleypawn/missed_call_text/" 2>&1
for f in "$HOME/Library/Logs/valleypawn/missed_call_text/"*.log "$HOME/Library/Logs/valleypawn/missed-call-text"*.log; do [ -f "$f" ] && { echo "== $f"; tail -40 "$f"; }; done
echo "--- receipts"; tail -5 "$OS/fleet/receipts/missed-call-text.jsonl" 2>&1
