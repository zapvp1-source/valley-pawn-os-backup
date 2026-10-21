#!/bin/bash
# comms review: verify the audit now reads every sent AI reply (10/19 had 9 sends) — render only, nothing sent
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/ai_reply_audit.py" --date 2026-10-19 --render
python3 "$BIN/ai_reply_audit.py" --date 2026-10-14 --render
