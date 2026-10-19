#!/bin/bash
echo "=== install dormant com.valleypawn.dress-code-check (gated by vp_live.sh; no native_live file) ==="
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.dress-code-check
echo "=== catchup render (syntax + job table) ==="
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/catchup.py" --render
