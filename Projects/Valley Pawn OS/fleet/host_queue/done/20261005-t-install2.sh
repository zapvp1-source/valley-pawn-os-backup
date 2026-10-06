#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/brevo_welcome.py" --render
bash "$BIN/install_agent.sh" com.valleypawn.brevo-welcome
bash "$BIN/install_agent.sh" com.valleypawn.brevo-engaged-v2
bash "$BIN/install_agent.sh" com.valleypawn.brevo-attr-sync
