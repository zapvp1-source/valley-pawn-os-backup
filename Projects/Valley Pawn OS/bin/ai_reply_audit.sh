#!/bin/bash
# launchd wrapper — com.valleypawn.ai-reply-audit, 21:45 daily. Reads back every automated customer text sent
# yesterday/today from the Chekkit API and grades it against the current hours + facts (comms review 2026-10-20).
# DMs Joshua only when a reply was wrong or a fact is stale. No cloud copy exists, so no vp_live gate.
AGENT="ai-reply-audit"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 40
"$PY" "$BIN/ai_reply_audit.py" --date "$(date +%Y-%m-%d)" "$@" >> "$VLOG/$AGENT.log" 2>&1
