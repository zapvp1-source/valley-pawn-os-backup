#!/bin/bash
# vp_live.sh — the "native_live" switch for Mac-first conversions (2026-10-08). Source AFTER vp_lib.sh:
#   . "$BIN/vp_live.sh"; vp_live_gate "<cowork-task-id>"
# The agent exits 0 SILENTLY unless  fleet/state/native_live/<task-id>  exists. That lets a native agent be
# installed and scheduled while the task's claude.ai cloud copy is still running (no double posts). Going
# live = create that one empty file (only after the cloud copy is switched off). Going back = delete it.
# --render / manual runs call the .py directly and are never gated.
vp_live_gate() {
  [ -f "$OS_DIR/fleet/state/native_live/$1" ] && return 0
  exit 0
}
