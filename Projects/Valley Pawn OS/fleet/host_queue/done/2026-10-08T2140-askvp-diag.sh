#!/bin/bash
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
python3 "$OS/bin/agent_log_tail.py" ask-vp 40
bash "$OS/bin/tail_any.sh" ask-vp.out.log 20
python3 "$OS/bin/ask_vp_responder.py" --status
