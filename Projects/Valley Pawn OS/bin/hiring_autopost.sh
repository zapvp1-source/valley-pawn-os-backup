#!/bin/bash
# launchd wrapper — hiring auto-post (2026-10-21, Joshua: "whenever Preston opens hiring at a store, auto post").
# Every 30 min: reads HIRING_SWITCH.md; any store ON with no hiring post yet (or 14 days since the last) gets one
# on its Facebook page + Google Business Profile through the vp_social engine. No Slack; failures = one ledger row.
AGENT="hiring-autopost"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 30
"$PY" "$BIN/hiring_autopost.py" --live "$@" >> "$VLOG/$AGENT.log" 2>&1
