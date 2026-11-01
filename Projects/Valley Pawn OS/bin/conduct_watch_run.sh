#!/bin/bash
# launchd wrapper — com.valleypawn.conductwatch-<store> (Mon–Sat 09:55; KeepAlive restarts on crash). Built 2026-10-31.
# Records the store's counter cameras until 5 min after close (stills + 720p video/audio). Code: Projects/Store Conduct Watch.
# Dormant unless fleet/state/native_live/conductwatch-<store> exists.
STORE="${1:?store}"; AGENT="conductwatch-$(echo "$STORE" | tr 'A-Z' 'a-z')"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"; vp_lock "$AGENT" 600
export VPST_DIR="$HOME/.vp_secrets/store_traffic"
cd "$HOME/Documents/Claude/Projects/Store Conduct Watch" || exit 1
mkdir -p logs
"$HOME/.vp-studio/conduct-watch-venv/bin/python" watch.py "$STORE" --until-close 2>&1 | grep --line-buffered -v "cpuid" | tee -a "$VLOG/$AGENT.log" >> "logs/$AGENT.log"
exit ${PIPESTATUS[0]}
