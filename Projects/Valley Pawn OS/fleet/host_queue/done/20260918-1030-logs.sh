#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/host_diag.sh" logs github-backup 25
bash "$BIN/host_diag.sh" logs morning-pull 12
