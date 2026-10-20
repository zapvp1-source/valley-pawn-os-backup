#!/bin/bash
# launchd wrapper — native eom-bravo-gl-export-watchdog (Mac-first wave 3, 2026-10-19). Dormant unless fleet/state/native_live/eom-bravo-gl-export-watchdog exists (bin/vp_live.sh).
AGENT="eom-bravo-gl-export-watchdog"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$BIN/eom_gl_watchdog.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
