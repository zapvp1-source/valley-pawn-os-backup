#!/bin/bash
# Ask Valley Pawn v2 — conversational (threads, follow-ups, DMs). Selftest first, then restart.
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
echo "== selftest (25 incl. follow-ups)"
python3 "$OS/bin/ask_vp_responder.py" --selftest
echo "== restart"
bash "$OS/bin/install_agent.sh" com.valleypawn.ask-vp --restart-only
