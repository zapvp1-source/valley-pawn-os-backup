#!/bin/bash
# launchd wrapper — com.valleypawn.browser-host (2026-11-21). The always-on automation Chrome; see bin/vp_browser_host.py.
# Dormant unless fleet/state/native_live/browser-host exists. KeepAlive restarts the loop if it ever exits with an error.
AGENT="browser-host"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
exec "$PY" "$BIN/vp_browser_host.py" run >> "$VLOG/$AGENT.log" 2>&1
