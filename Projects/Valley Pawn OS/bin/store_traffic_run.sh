#!/bin/bash
# launchd wrapper — com.valleypawn.storetraffic-<store> (Mon–Sat 09:57; KeepAlive restarts on crash).
# Runs the door counter until 5 min after that store's close. Code: Projects/Store Traffic Counter.
# Usage: store_traffic_run.sh <Store>   Dormant unless fleet/state/native_live/storetraffic-<store> exists.
STORE="${1:-Waynesboro}"; AGENT="storetraffic-$(echo "$STORE" | tr 'A-Z' 'a-z')"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"; vp_lock "$AGENT" 600
export VPST_DIR="$HOME/.vp_secrets/store_traffic"
cd "$HOME/Documents/Claude/Projects/Store Traffic Counter" || exit 1
mkdir -p logs
"$HOME/.vp-studio/store-traffic-venv/bin/python" counter.py "$STORE" --until-close 2>&1 | grep --line-buffered -v "cpuid" | tee -a "$VLOG/$AGENT.log" >> "logs/$AGENT.log"
exit ${PIPESTATUS[0]}
