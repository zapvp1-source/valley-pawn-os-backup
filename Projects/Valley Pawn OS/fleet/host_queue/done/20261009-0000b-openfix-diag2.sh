#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/tail_any.sh" oura-daily-import.log 60
bash "$BIN/tail_any.sh" oura-import-check.out.log 20
bash "$BIN/tail_any.sh" chrome-extension-watchdog.log 40
bash "$BIN/tail_any.sh" chrome-extension-watchdog.launchd.out 20
bash "$BIN/tail_any.sh" chrome-extension-watchdog.launchd.err 20
bash "$BIN/tail_any.sh" vp-weekly-spot-price-update.log 15
bash "$BIN/tail_any.sh" chekkit_ai_responder/heartbeat.json 3
echo "=== chekkit render ==="
bash "$BIN/chekkit_ai_responder.sh" --render --hours 2
