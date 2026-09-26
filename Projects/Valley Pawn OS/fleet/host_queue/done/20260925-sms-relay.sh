#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/sms_code_relay.sh" --render
bash "$BIN/install_agent.sh" com.valleypawn.sms-code-relay
python3 "$BIN/install_skill_block.py" northwest-registered-agent-daily-check "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/skill_blocks/northwest_sms_relay.md" --apply
