#!/bin/bash
# launchd wrapper — native scheduled-task-model-audit-weekly (Mac-first wave 2, 2026-10-14). Dormant unless fleet/state/native_live/scheduled-task-model-audit-weekly exists.
AGENT="scheduled-task-model-audit-weekly"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$BIN/model_audit_weekly.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
