#!/bin/bash
# comms review: find the last day automated texts actually appear in Chekkit conversations (10/15-10/18), nothing sent
BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/ai_reply_audit.py" --date 2026-10-15 --render --no-judge
python3 "$BIN/ai_reply_audit.py" --date 2026-10-16 --render --no-judge
python3 "$BIN/ai_reply_audit.py" --date 2026-10-17 --render --no-judge
python3 "$BIN/ai_reply_audit.py" --date 2026-10-18 --render --no-judge
python3 "$BIN/agent_log_tail.py" missed_call_text/run 60
python3 "$BIN/agent_log_tail.py" chekkit-ai-responder 80
