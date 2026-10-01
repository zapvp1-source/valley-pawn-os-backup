#!/bin/bash
# launchd wrapper — com.valleypawn.texting-scorecard, 19:20 daily. Builds the day's phone/text friction
# scorecard and DMs Joshua a 4-line summary once per day. Added 2026-09-30 (Joshua: measure friction + response).
AGENT="texting-scorecard"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 20
"$PY" "$BIN/texting_scorecard.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
