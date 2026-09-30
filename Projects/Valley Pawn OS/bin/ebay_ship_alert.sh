#!/bin/bash
# launchd wrapper — com.valleypawn.ebay-ship-alert (Mon–Sat 09:30 = am, 14:00 = pm). Built 2026-09-29.
# Usage: ebay_ship_alert.sh am|pm [--render] [--debug]   (--render = print, send nothing)
AGENT="ebay-ship-alert"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
SLOT="$1"; shift
if [ -z "$SLOT" ]; then H=$(date +%H); [ "$H" -lt 12 ] && SLOT=am || SLOT=pm; fi
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
[ $RENDER -eq 0 ] && vp_lock "$AGENT" 20
"$PY" "$BIN/ebay_ship_alert.py" --slot "$SLOT" "$@" 2>&1 | tee -a "$VLOG/$AGENT.log"
exit ${PIPESTATUS[0]}
