#!/bin/bash
# launchd wrapper — com.valleypawn.brevo-watchdog (native, 2026-10-05).
AGENT="brevo-preflight-watchdog"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/brevo_watchdog.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
