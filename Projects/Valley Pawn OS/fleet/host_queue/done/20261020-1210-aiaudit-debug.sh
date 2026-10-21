#!/bin/bash
# comms review: why did the 10/19 audit see 0 messages? debug counts per store, nothing sent
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/ai_reply_audit.py" --date 2026-10-19 --render --no-judge --debug
python3 "$BIN/ai_reply_audit.py" --date 2026-10-17 --render --no-judge --debug
