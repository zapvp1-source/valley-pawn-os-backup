#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/install_agent.sh" com.valleypawn.nics-monthly
bash "$BIN/install_agent.sh" com.valleypawn.gift-credit
python3 "$BIN/nics_monthly.py" 2026-09
