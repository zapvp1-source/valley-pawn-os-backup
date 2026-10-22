#!/bin/bash
# verify chekkit_api limit=50 paging: re-render the 10/19 automated-text audit (render only, nothing sent) and the scorecard
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/ai_reply_audit.py" --date 2026-10-19 --render --no-judge --debug
