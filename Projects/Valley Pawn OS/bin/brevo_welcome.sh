#!/bin/bash
# launchd wrapper — com.valleypawn.brevo-welcome (native, 2026-10-05).
AGENT="brevo-welcome-new-contacts"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/brevo_welcome.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
