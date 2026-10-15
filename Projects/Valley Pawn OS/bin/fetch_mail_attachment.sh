#!/bin/bash
# Copy Apple Mail attachments (by Mail attachment-folder id) into Projects/Unified Search/_attach/<id>/
# so cloud sessions can read images/PDFs the text index cannot (2026-10-14). Read-only on ~/Library/Mail.
ID="$1"
case "$ID" in ''|*[!0-9]*) echo "REFUSED: attachment id must be numeric"; exit 2;; esac
DEST="$HOME/Documents/Claude/Projects/Unified Search/_attach/$ID"; mkdir -p "$DEST"
find "$HOME/Library/Mail/V10" -type d -path "*/Attachments/$ID" 2>/dev/null | head -1 | while read -r d; do
  find "$d" -type f -exec cp -n {} "$DEST/" \;
done
ls -la "$DEST"
