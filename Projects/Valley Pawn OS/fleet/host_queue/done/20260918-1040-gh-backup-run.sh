#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/github_backup.sh"
bash "$BIN/tail_any.sh" github-backup.log 10
