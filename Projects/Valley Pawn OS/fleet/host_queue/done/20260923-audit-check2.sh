#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/vp_audit.py"
bash "$BIN/mail_brief.sh" --render
