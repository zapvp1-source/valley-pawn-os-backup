#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/ebay_ship_alert.sh" am --render --debug
bash "$BIN/ebay_ship_alert.sh" pm --render
