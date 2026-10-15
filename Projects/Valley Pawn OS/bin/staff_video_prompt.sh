#!/bin/bash
# launchd wrapper — native vp-staff-video-prompt (Mac-first wave 2, 2026-10-14). Dormant unless fleet/state/native_live/vp-staff-video-prompt exists.
AGENT="vp-staff-video-prompt"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$BIN/staff_video_prompt.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
