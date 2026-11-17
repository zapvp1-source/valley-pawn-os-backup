#!/bin/bash
# launchd wrapper — com.valleypawn.preston-phone-week, Mondays 06:00/08:00/10:00/12:00/14:00 (first slot after the
# 02:30 Phone & Text Review finishes does the work; later slots exit at once once the week is delivered).
# Preston Phone Brief (Joshua 2026-11-16). Reads the review's files only; DM to Joshua via fleet/outbox.
AGENT="preston-phone-week"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 120
"$PY" "$BIN/preston_phone_week.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
