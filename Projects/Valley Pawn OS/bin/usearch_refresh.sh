#!/bin/bash
# Native replacement for unified-search-index-refresh — 2026-09-17. Launch-and-exit; refresh_hardened.sh owns its lock/retries.
AGENT=usearch-refresh; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
U="$HOME/Documents/Claude/Projects/Unified Search"
pgrep -f refresh_hardened.sh >/dev/null && { vlog "already running — exit"; exit 0; }
( bash "$U/refresh_hardened.sh" ) > /tmp/usearch_task_run.log 2>&1 < /dev/null &
vlog "launched refresh_hardened.sh (pid $!)"
