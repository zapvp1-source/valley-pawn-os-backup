#!/bin/bash
# HOST JOB — install the native morning pull (replaces the silently-dying Cowork task) and run it once now.
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/morning_pull.sh" --dry-run
bash "$BIN/install_agent.sh" com.valleypawn.morning-pull
bash "$BIN/morning_pull.sh"
