#!/bin/bash
# launchd wrapper — native jewelry-onhand-nightly-pull (2026-10-14). Mon-Sat 20:30. Dormant unless
# fleet/state/native_live/jewelry-onhand-nightly-pull exists (switch the cloud trigger trig_01VvvttPGf7VTqK6thQhf36m off first).
AGENT="jewelry-onhand-nightly-pull"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 240
"$PY" "$BIN/jewelry_nightly.py" nightly --send "$@" >> "$VLOG/$AGENT.log" 2>&1
