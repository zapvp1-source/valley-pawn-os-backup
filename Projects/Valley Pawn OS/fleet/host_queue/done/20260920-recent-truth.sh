#!/bin/bash
# What has ACTUALLY posted in the last 2 weeks? Recent reality, not lifetime history.
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/recent_truth.py" --days 14
