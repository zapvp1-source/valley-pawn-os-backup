#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/agent_log_tail.py" pawn-walk 6
python3 "$BIN/agent_log_tail.py" sold-review 6
python3 "$BIN/agent_log_tail.py" discount-review 4
python3 "$BIN/run_trace.py" vp-presence-audit-weekly 2026-09-27 12
python3 "$BIN/run_trace.py" weekly-online-store-audit 2026-09-27 12
python3 "$BIN/run_trace.py" daily-dress-code-check 2026-09-26 12
python3 "$BIN/run_trace.py" northwest-registered-agent-daily-check 2026-09-28 12
python3 "$BIN/run_trace.py" northwest-registered-agent-daily-check 2026-09-26 12
