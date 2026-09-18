#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/tail_any.sh" github-backup.err.log 30
bash "$BIN/tail_any.sh" github-backup.out.log 20
