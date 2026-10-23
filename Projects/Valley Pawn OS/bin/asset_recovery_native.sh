#!/bin/bash
# launchd wrapper — com.valleypawn.asset-recovery (19:15 daily, native, 2026-10-22). Replaces the cloud task
# asset-recovery-daily-refresh (trig_014PS7pZqihrdybSZZ8q6ZPP). DORMANT unless
# fleet/state/native_live/asset-recovery-daily-refresh exists — create it only after the cloud trigger is off.
# File + math only: reads the Bravo EOM xlsx set already on disk, never pulls, never touches Bravo, no Slack.
AGENT="asset-recovery-daily-refresh"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$BIN/asset_recovery_native.py" run "$@" >> "$VLOG/$AGENT.log" 2>&1
