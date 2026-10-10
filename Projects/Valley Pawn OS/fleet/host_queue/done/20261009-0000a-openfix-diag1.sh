#!/bin/bash
set +e
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "=== field_scorecard dry-run ==="
python3 "$BIN/field_scorecard.py" --dry-run
echo "=== chekkit run.log ==="
bash "$BIN/tail_any.sh" chekkit_ai_responder/run.log 120
echo "=== chekkit run.err ==="
bash "$BIN/tail_any.sh" chekkit_ai_responder/run.err 120
bash "$BIN/tail_any.sh" chekkit_ai_responder/run.err.log 120
python3 "$BIN/agent_log_tail.py" chekkit-ai-responder 60
echo "=== log_triage ==="
python3 "$BIN/log_triage.py" --days 7
echo "=== quiet_triage ==="
python3 "$BIN/quiet_triage.py"
echo "=== fleet-doctor ==="
python3 "$BIN/agent_log_tail.py" fleet-doctor 60
