#!/bin/bash
# launchd wrapper — native ebay-weekly-channel-audit (Mac-first, 2026-10-14). Dormant unless fleet/state/native_live/ebay-weekly-channel-audit exists.
AGENT="ebay-weekly-channel-audit"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 90
"$PY" "$BIN/ebay_channel_audit.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
