#!/bin/bash
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
python3 "$OS/bin/ask_vp_responder.py" --selftest
bash "$OS/bin/install_agent.sh" com.valleypawn.ask-vp --restart-only
