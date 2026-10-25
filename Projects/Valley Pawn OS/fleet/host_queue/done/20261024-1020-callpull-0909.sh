#!/bin/bash
# 2026-10-24 November-meeting call clips: transcribe Sep 9-20 recordings (pull + local whisper only, detached, no grading)
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/call_week_review.py" --since 2026-09-09 --until 2026-09-20 --detach
