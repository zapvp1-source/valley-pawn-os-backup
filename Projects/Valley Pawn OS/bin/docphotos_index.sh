#!/bin/bash
# docphotos_index.sh — native replacement for Cowork `document-photos-index-refresh` (05:00, 2026-09-30).
# Runs the SKILL's own command in the FOREGROUND (launchd keeps the job alive; no orphan-kill — see the
# 9/25 usearch AbandonProcessGroup lesson). photosindex_documents.py is untouched (its OCR fixes stay).
AGENT="document-photos-index-refresh"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
U="$HOME/Documents/Claude/Projects/Unified Search"
[ "$1" = "--render" ] && { echo "=== RENDER: would run $U/.venv_photos/bin/python3 photosindex_documents.py ==="; ls -la "$U/.venv_photos/bin/python3" "$U/photosindex_documents.py"; exit 0; }
vp_lock "$AGENT" 240
pgrep -f photosindex_documents.py >/dev/null && { vlog "already running — exit"; exit 0; }
( cd "$U" && .venv_photos/bin/python3 photosindex_documents.py ) > /tmp/docphotos_nightly.log 2>&1 < /dev/null; RC=$?
if [ $RC -eq 0 ]; then
  $PY "$BIN/vp_receipt.py" write "$AGENT" --surface file --target "$U/photosindex_documents.log" --note "$(tail -1 /tmp/docphotos_nightly.log | cut -c1-120)" >/dev/null 2>&1
else
  ledger "$AGENT" "The nightly document-photo index did not finish (exit $RC)." "no"; exit 1
fi
