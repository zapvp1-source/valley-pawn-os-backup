#!/bin/bash
# Why are pawn-walk posts empty? Ask Slack what it actually stored.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== raw last 3 messages in #pawn-walks (len= is the truth) ====="
python3 "$BIN/vp_slack.py" last C0B8WR95N31 3
echo "===== and #sold-review ====="
python3 "$BIN/vp_slack.py" last C0BK802MP43 2
