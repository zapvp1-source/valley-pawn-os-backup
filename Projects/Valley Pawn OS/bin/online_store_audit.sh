#!/bin/bash
# launchd wrapper — com.valleypawn.online-store-audit, Sunday 08:00 (native, 2026-10-05; was Cowork weekly-online-store-audit).
AGENT="weekly-online-store-audit"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 120
"$PY" "$BIN/online_store_audit.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
