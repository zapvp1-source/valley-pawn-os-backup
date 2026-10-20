#!/bin/bash
# launchd wrapper — native bonus-month-close-pull (Mac-first wave 3, 2026-10-19). 1st of month 11:30 ET. DM to Joshua only.
# Dormant unless fleet/state/native_live/bonus-month-close-pull exists (bin/vp_live.sh).
AGENT="bonus-month-close-pull"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 170
"$PY" "$BIN/bonus_close_pull.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
