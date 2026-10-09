#!/bin/bash
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
echo "== capture dry run (join attempt on the three missing channels)"
python3 "$OS/bin/ask_vp_capture.py" --dry-run --no-zoom
echo "== selftest 4"
python3 "$OS/bin/ask_vp_responder.py" --selftest
echo "== agent status"
bash "$OS/bin/install_agent.sh" com.valleypawn.ask-vp --restart-only
