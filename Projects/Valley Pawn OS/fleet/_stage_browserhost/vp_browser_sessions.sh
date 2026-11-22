#!/bin/bash
# launchd wrapper — com.valleypawn.browser-sessions (nightly 02:40; 2026-11-21). Read-only check that each site in the
# always-on automation browser is still signed in; a site that signed out goes on the Login Day list before a task fails.
AGENT="browser-sessions"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"; vp_lock "$AGENT" 20
"$PY" "$BIN/vp_browser_host.py" sessions >> "$VLOG/$AGENT.log" 2>&1
