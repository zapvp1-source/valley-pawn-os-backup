#!/bin/bash
# Ask Valley Pawn — install the nightly capture + Monday verify agents; dry-run both once (nothing posted).
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
echo "== capture dry run (Slack read only, no Zoom, no writes)"
python3 "$OS/bin/ask_vp_capture.py" --dry-run --no-zoom
echo "== verify dry run (writes Ask Valley Pawn/verify/<date>.md, posts nothing)"
python3 "$OS/bin/ask_vp_verify.py" --dry-run
echo "== install agents"
bash "$OS/bin/install_agent.sh" com.valleypawn.ask-vp-capture
bash "$OS/bin/install_agent.sh" com.valleypawn.ask-vp-verify
