#!/bin/bash
# launchd wrapper — com.valleypawn.store-kpis-weekly (Mon 10:30, native, 2026-10-05). Replaces Cowork `weekly-store-kpis`.
AGENT="weekly-store-kpis"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 150
"$PY" "$BIN/store_kpis_weekly.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
