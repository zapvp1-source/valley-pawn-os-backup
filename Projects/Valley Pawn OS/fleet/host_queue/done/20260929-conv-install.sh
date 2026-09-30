#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
bash "$BIN/health_episode.sh" --render
bash "$BIN/social_recap.sh" --render
bash "$BIN/monthly_prestage.sh" --render
python3 "$BIN/skill_tool_index.py"
bash "$BIN/install_agent.sh" com.valleypawn.health-episode
bash "$BIN/install_agent.sh" com.valleypawn.social-recap
bash "$BIN/install_agent.sh" com.valleypawn.monthly-prestage
bash "$BIN/install_agent.sh" com.valleypawn.skill-tool-index
python3 "$BIN/install_skill_block.py" connector-health-daily "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/skill_blocks/connector_health_files.md" --apply
python3 "$BIN/agent_doctor.py"
