#!/bin/bash
# launchd wrapper — com.valleypawn.brevo-engaged-v2, Wed 06:20 (native, 2026-10-05). Logic lives in engaged_v2.py.
AGENT="brevo-engaged-v2-refresh"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 60
cd "$HOME/Documents/Claude/Projects/Email Refinement/bin" && "$PY" -u engaged_v2.py --apply --compare --max-universe 1200 >> "$VLOG/$AGENT.log" 2>&1
