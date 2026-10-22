#!/bin/bash
# dailygl_restart.sh — stop an in-flight bravo-daily-gl run (state.json is saved after every store-day, so nothing
# posted is lost), clear its lock, and start a fresh run with the current code. 2026-10-21.
pkill -f "bin/bravo_daily_gl.sh" 2>/dev/null
pkill -f "bin/bravo_daily_gl.py" 2>/dev/null
pkill -f "bravo_pull.sh post-to-accounting-gl" 2>/dev/null
sleep 3
rmdir "$HOME/Library/Logs/valleypawn/.lock.bravo-daily-gl" 2>/dev/null
[ -n "$1" ] && /usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/bravo_daily_gl.py" --mark-posted-through "$1"
launchctl kickstart -k "gui/$(id -u)/com.valleypawn.bravo-daily-gl" && echo "bravo-daily-gl restarted"
sleep 2; launchctl list | grep -F com.valleypawn.bravo-daily-gl
