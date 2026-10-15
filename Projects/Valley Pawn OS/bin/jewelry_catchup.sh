#!/bin/bash
# launchd wrapper — native jewelry-onhand-catchup (2026-10-14). Mon-Sat morning. Dormant unless
# fleet/state/native_live/jewelry-onhand-catchup exists (switch the cloud trigger trig_013aQGcjJYLdEHMMuarXD8HC off first).
AGENT="jewelry-onhand-catchup"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "jewelry-onhand-nightly-pull" 240
"$PY" "$BIN/jewelry_nightly.py" catchup --send "$@" >> "$VLOG/$AGENT.log" 2>&1
