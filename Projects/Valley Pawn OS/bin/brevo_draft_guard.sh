#!/bin/bash
# launchd wrapper — com.valleypawn.brevo-draft-guard (native, 2026-10-05).
AGENT="brevo-weekly-draft-guard"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
"$PY" "$BIN/brevo_draft_guard.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
