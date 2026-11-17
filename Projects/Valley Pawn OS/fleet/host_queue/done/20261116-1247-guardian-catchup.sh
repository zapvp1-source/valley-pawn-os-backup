#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/cloudcover_check.sh"
bash "$BIN/dress_code_check.sh"
bash "$BIN/monday_compile.sh"
