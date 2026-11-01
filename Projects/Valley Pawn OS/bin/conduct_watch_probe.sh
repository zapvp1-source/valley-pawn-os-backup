#!/bin/bash
# conduct_watch_probe.sh — read-only probe for Store Conduct Watch: `list` cameras (names only) or `grab <Store> "<Camera>" [secs]`. No Slack.
export VPST_DIR="$HOME/.vp_secrets/store_traffic"
cd "$HOME/Documents/Claude/Projects/Store Conduct Watch" || exit 1
PYV="$HOME/.vp-studio/conduct-watch-venv/bin/python"; [ -x "$PYV" ] || PYV="$HOME/.vp-studio/store-traffic-venv/bin/python"
"$PYV" probe.py "$@" 2>&1 | grep -v cpuid
