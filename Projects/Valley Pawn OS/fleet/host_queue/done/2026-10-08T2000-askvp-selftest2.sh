#!/bin/bash
# Ask Valley Pawn — rebuild corpus after the sub-section + cite fixes, rerun the selftest, restart the agent.
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
echo "== corpus build"
python3 "$OS/bin/ask_vp_corpus.py" --force
echo "== selftest"
python3 "$OS/bin/ask_vp_responder.py" --selftest
echo "== restart agent"
bash "$OS/bin/install_agent.sh" com.valleypawn.ask-vp --restart-only
