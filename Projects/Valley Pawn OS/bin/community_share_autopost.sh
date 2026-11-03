#!/bin/bash
# launchd wrapper — community share auto-post (2026-11-02, Joshua: "split version").
# Every 30 min: schedules queued community SHARES (from the daily prep run's QUEUE.json) on the store pages through
# the vp_social engine / Publer, within the RAMP weekly caps. No Slack; failures = one ledger row.
AGENT="community-share-autopost"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 30
"$PY" "$BIN/community_share_autopost.py" --live "$@" >> "$VLOG/$AGENT.log" 2>&1
