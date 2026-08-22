#!/bin/bash
# Relaunch Claude app if not running, so Cowork scheduled tasks can fire.
# launchd: 8:20 PM (before nightly jewelry pull) and 7:35 AM (before catch-up).
LOG="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/claude_keepalive.log"
if ps -axo comm | grep -q '^/Applications/Claude.app/Contents/MacOS/Claude$'; then
  echo "$(date '+%F %T') already running" >> "$LOG"
else
  open -ga 'Claude'
  echo "$(date '+%F %T') RELAUNCHED Claude" >> "$LOG"
fi
