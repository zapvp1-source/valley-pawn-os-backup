#!/bin/bash
# Ask Valley Pawn — first build: corpus, selftest (no Slack), then install the agent in SHADOW mode.
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
echo "== corpus build"
python3 "$OS/bin/ask_vp_corpus.py" --force
echo "== selftest (writes Projects/Ask Valley Pawn/selftest/<stamp>.md)"
python3 "$OS/bin/ask_vp_responder.py" --selftest
echo "== install agent com.valleypawn.ask-vp (SHADOW mode per config.json)"
bash "$OS/bin/install_agent.sh" com.valleypawn.ask-vp
echo "== status"
python3 "$OS/bin/ask_vp_responder.py" --status
