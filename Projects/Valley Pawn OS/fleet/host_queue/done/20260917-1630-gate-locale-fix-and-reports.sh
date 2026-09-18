#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/bravo_unwedge.sh"
bash "$BIN/daily_report.sh" pawn 2026-09-16
bash "$BIN/daily_report.sh" sold 2026-09-16
bash "$BIN/daily_report.sh" discount 2026-09-16
