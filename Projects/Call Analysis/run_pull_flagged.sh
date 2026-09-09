#!/bin/bash
# Runner for pull_flagged.py — kept as a file so it can be launched detached without
# AppleScript quoting fights. Safe to re-run; pull_flagged.py skips calls already converted.
cd "$HOME/Documents/Claude/Projects/Call Analysis" || exit 1
exec /usr/bin/python3 pull_flagged.py \
  --since 2026-08-31 --until 2026-09-06 \
  --map flagged_2026-08-31.json \
  --out "$HOME/Documents/Claude/Projects/Call Analysis/audio/2026-08-31_2026-09-06"
