#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
for a in pawn-walk sold-review discount-review; do python3 "$BIN/agent_log_tail.py" $a 6; done
python3 "$BIN/run_trace.py" vp-presence-audit-weekly 2026-09-27 12
python3 "$BIN/run_trace.py" weekly-online-store-audit 2026-09-27 12
python3 "$BIN/run_trace.py" daily-dress-code-check 2026-09-26 12
python3 "$BIN/run_trace.py" northwest-registered-agent-daily-check 2026-09-28 12
python3 "$BIN/run_trace.py" vp-staff-video-prompt 2026-09-27 6
