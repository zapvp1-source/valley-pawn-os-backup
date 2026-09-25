#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/install_outbox_step.py" jewelry-onhand-nightly-pull C0BM9NHGTT4 --apply
python3 "$BIN/grep_skill.py" jewelry-onhand-nightly-pull "OUTBOX SEND"
bash "$BIN/retire_agent.sh" com.valleypawn.chekkitperms-oneshot --apply
bash "$BIN/install_agent.sh" com.valleypawn.taskperms-oneshot
python3 "$BIN/agent_doctor.py"
