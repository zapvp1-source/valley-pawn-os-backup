#!/bin/bash
# dailygl_handler_refresh.sh — 2026-11-08. Stop an in-flight bravo-daily-gl run (state is saved per store-day, nothing
# posted is lost), restart the Bravo AHK watcher so the fixed PostToAccountingPostV2.ahk is loaded, then (re)install the
# bravo-daily-gl plist (adds the 07:50 / 13:10 daytime runs) which starts a fresh run with the new handler.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
LOG="$HOME/Library/Logs/valleypawn/dailygl_handler_refresh.log"; mkdir -p "$(dirname "$LOG")"
log(){ echo "$(date '+%F %T') $*" | tee -a "$LOG"; }
log "stopping in-flight daily GL run"
pkill -f "bin/bravo_daily_gl.sh" 2>/dev/null; pkill -f "bin/bravo_daily_gl.py" 2>/dev/null; pkill -f "bravo_pull.sh post-to-accounting" 2>/dev/null
sleep 5; rmdir "$HOME/Library/Logs/valleypawn/.lock.bravo-daily-gl" 2>/dev/null
log "waiting for the Bravo pipeline to go idle, then restarting the watcher"
sleep 240
bash "$BIN/bravo_watcher_restart.sh"; rc=$?; log "watcher restart rc=$rc"
[ $rc -ne 0 ] && { sleep 300; bash "$BIN/bravo_watcher_restart.sh"; rc=$?; log "watcher restart retry rc=$rc"; }
log "installing com.valleypawn.bravo-daily-gl plist (daytime runs) and starting a fresh run"
bash "$BIN/install_agent.sh" com.valleypawn.bravo-daily-gl; log "install_agent rc=$?"
launchctl list | grep -F com.valleypawn.bravo-daily-gl | tee -a "$LOG"
