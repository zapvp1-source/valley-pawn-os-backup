#!/bin/bash
# 2026-11-02 November meeting deep dive: contact sheets + transcripts from the conduct watch, last 4 days, all 5 stores
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/conduct_watch_export.py" sheets --out "$HOME/Documents/Claude/Projects/Store Conduct Watch/export_nov2" --days 4
