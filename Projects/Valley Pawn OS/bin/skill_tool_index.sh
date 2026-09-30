#!/bin/bash
AGENT="skill-tool-index"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
"$PY" "$BIN/skill_tool_index.py" >> "$VLOG/$AGENT.log" 2>&1
