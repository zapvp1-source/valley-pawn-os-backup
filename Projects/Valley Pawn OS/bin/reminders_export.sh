#!/bin/bash
# reminders_export.sh — nightly READ-ONLY Apple Reminders export (EventKit via Life OS/bin/ekrem).
# Approved by Joshua 2026-11-21. Never writes to Reminders. Output: Life OS/Reminders/export_latest.json
AGENT="reminders-export"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vlog "start"
"$PY" "$BIN/reminders_export.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
rc=$?
vlog "end rc=$rc"
exit $rc
