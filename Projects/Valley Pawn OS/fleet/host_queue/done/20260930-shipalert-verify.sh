#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/tail_any.sh" ebay-ship-alert.log 40
bash "$BIN/tail_any.sh" ebay-ship-alert.err.log 20
bash "$BIN/tail_any.sh" ebay-ship-alert.out.log 10
bash "$BIN/tail_any.sh" ebay-ship-alert.state.json 30
