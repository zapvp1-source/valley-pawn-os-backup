#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/brevo_draft_guard.py" --render --thursday 2026-10-15
python3 "$BIN/brevo_draft_guard.py" --render --thursday 2026-10-22
bash "$BIN/install_agent.sh" com.valleypawn.brevo-watchdog
bash "$BIN/install_agent.sh" com.valleypawn.brevo-draft-guard
