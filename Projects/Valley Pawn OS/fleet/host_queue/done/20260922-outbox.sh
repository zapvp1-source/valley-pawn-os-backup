#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
echo "===== flush (the spawn hook will also run it; this makes it deterministic) ====="
bash "$BIN/outbox_flush.sh"
python3 "$BIN/inspect_path.py" "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/outbox/outbox.log" --lines 5
echo "===== install outbox step on the EOD task ====="
python3 "$BIN/install_outbox_step.py" chekkit-unanswered-eod-followup C0B1PEW0C30 --apply
