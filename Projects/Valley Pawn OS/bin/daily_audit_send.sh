#!/bin/bash
# launchd wrapper — native daily-store-audit-digest (Mac-first wave 1, 2026-10-08). Dormant unless fleet/state/native_live/daily-store-audit-digest exists.
AGENT="daily-store-audit-digest"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 60
"$PY" "$BIN/daily_audit_send.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
