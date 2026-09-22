#!/bin/bash
# Prove a native agent can produce the unopened-email view with no connector. Read-only.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/mail_unread.py" --hours 24
