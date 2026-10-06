#!/bin/bash
# zoom_missed_alert.sh <alert|eod> [--render] — launchd wrapper for bin/zoom_missed_alert.py.
# alert: com.valleypawn.zoom-missed-alert (every 20 min, 09:00-19:59; the Python itself is silent
#        outside Mon-Sat store hours because there are simply no new calls to report).
# eod:   com.valleypawn.zoom-missed-eod (17:45 daily).
# Native replacement for the Cowork tasks zoom-voicemail-alert / zoom-voicemail-eod-review (2026-09-25).
MODE="${1:-alert}"; AGENT="zoom-voicemail-alert"; [ "$MODE" = "eod" ] && AGENT="zoom-voicemail-eod-review"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
[ $RENDER -eq 0 ] && vp_lock "$AGENT" 15
"$PY" "$BIN/zoom_missed_alert.py" "$@" >> "$VLOG/$AGENT.log" 2>&1; RC=$?
[ $RENDER -eq 1 ] && tail -20 "$VLOG/$AGENT.log"
exit $RC
