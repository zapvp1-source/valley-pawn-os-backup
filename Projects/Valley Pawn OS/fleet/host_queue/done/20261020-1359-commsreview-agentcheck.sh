#!/bin/bash
# comms review restart 2026-10-20: read-only check of the three new agents (plist -> program) and their logs
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/agent_doctor.py"
python3 "$BIN/agent_log_tail.py" weekly-phone-text-review 20
python3 "$BIN/agent_log_tail.py" ai-reply-audit 10
python3 "$BIN/agent_log_tail.py" nightly-chekkit-review-responses 10
