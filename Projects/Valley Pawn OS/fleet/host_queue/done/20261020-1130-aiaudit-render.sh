#!/bin/bash
# comms review 2026-10-20: render the automated-text audit for 10/14 (the known-bad Waynesboro day) and 10/19 — sends nothing
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/ai_reply_audit.py" --date 2026-10-14 --render
python3 "$BIN/ai_reply_audit.py" --date 2026-10-19 --render
