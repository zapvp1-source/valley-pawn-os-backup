#!/bin/bash
# launchd wrapper — native vp-thursday-email-watchdog (Mac-first wave 2, 2026-10-14). Dormant unless fleet/state/native_live/vp-thursday-email-watchdog exists.
AGENT="vp-thursday-email-watchdog"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 60
"$PY" "$BIN/thursday_email_watchdog.py" --send "$@" >> "$VLOG/$AGENT.log" 2>&1
