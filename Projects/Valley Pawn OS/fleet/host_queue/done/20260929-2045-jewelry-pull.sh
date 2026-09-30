#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
for S in CUL HAR LEX ROA WAY; do
  bash "$BIN/bravo_pull.sh" jewelry-case-counts-v2 2026-09-29 "$S" "jewelry-onhand-2026-09-29-$S"
done
