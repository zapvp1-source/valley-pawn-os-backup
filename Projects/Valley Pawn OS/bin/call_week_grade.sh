#!/bin/bash
# launchd wrapper — com.valleypawn.call-week-review, Mondays 02:30. The weekly Phone & Text Review, native
# (comms review 2026-10-20): pull + transcribe last Mon–Sun, grade every call via the Claude API, PDF, one DM to Joshua.
# No cloud copy exists, so no vp_live gate. Lock is long (the transcription of a full week can take an hour).
AGENT="weekly-phone-text-review"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 300
"$PY" "$BIN/call_week_grade.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
