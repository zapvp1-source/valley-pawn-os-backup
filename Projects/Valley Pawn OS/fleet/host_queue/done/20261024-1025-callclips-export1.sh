#!/bin/bash
# 2026-10-24 November-meeting call clips: download candidate recordings (read-only Zoom) for audio verification
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/call_clip_export.py" --manifest "$HOME/Documents/Claude/Projects/Call Analysis/november_clips/manifest1.json"
