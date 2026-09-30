#!/bin/bash
# health_episode.sh — native replacement for Cowork `health-episode-capture` (09:15 daily, 2026-09-29).
# The SKILL's two steps, verbatim: episode_capture.py then night_signature.py, on the host. Silent on
# success (receipt only); one ledger row on failure. Domain 3 — personal.
AGENT="health-episode-capture"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
HP="$HOME/Documents/Claude/Projects/Health Optimization"
[ $RENDER -eq 1 ] && { echo "=== RENDER ONLY ==="; ls "$HP/scripts/episode_capture.py" "$HP/scripts/night_signature.py"; exit 0; }
vp_lock "$AGENT" 20
( cd "$HP" && $PY scripts/episode_capture.py ) >> "$VLOG/$AGENT.log" 2>&1 || { ledger "$AGENT" "This morning's health episode capture did not complete." "no"; exit 1; }
( cd "$HP" && $PY scripts/night_signature.py ) >> "$VLOG/$AGENT.log" 2>&1 || ledger "$AGENT" "Health episodes were captured, but the nights ledger refresh failed." "no"
$PY "$BIN/vp_receipt.py" write "$AGENT" --surface file --target "$HP" >/dev/null 2>&1
vlog "episode capture done"
