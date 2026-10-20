#!/bin/bash
# launchd wrapper — native monthly-scrap-rankings (Mac-first wave 3, 2026-10-19). 1st of month 04:30 ET (the SKILL's
# deliberate slot: after Bravo's ~04:00 nightly restart, before the 07:30 morning cluster).
# Dormant unless fleet/state/native_live/monthly-scrap-rankings exists (bin/vp_live.sh).
AGENT="monthly-scrap-rankings"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 170
"$PY" "$BIN/scrap_rankings_monthly.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
