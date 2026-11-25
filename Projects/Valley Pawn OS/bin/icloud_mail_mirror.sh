#!/bin/bash
# icloud_mail_mirror.sh — every 10 min, READ-ONLY mirror of iCloud Inbox + Sent (and other accounts' Sent)
# from Apple Mail's local store into Life OS/Mail Mirror/ (Drive-synced). Built 2026-11-24 because the
# cloud Apple_Mail connector's app-specific password fails auth (since 11/12). Never writes to Mail.
AGENT="icloud-mail-mirror"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"; . "$BIN/vp_live.sh"
vp_live_gate "$AGENT"
vp_lock "$AGENT" 30
"$PY" "$BIN/icloud_mail_mirror.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
exit $?
