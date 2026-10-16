#!/bin/bash
# Read-only: copy recent STR underwriting PDFs (16 Mulvey, 251 Riberia, 6548 Putnam) from Apple Mail attachments into Unified Search/_attach/str_1015/
DEST="$HOME/Documents/Claude/Projects/Unified Search/_attach/str_1015"; mkdir -p "$DEST"
find "$HOME/Library/Mail/V10" -type f -path "*/Attachments/*" -newermt "2026-10-14 12:00" \( -iname "*.pdf" -o -iname "*.xlsx" -o -iname "*.xls" -o -iname "*.csv" -o -iname "*.docx" \) 2>/dev/null | while read -r f; do
  id=$(echo "$f" | sed -E 's#.*/Attachments/([0-9]+)/.*#\1#'); b=$(basename "$f")
  cp -n "$f" "$DEST/${id}__${b}"
done
ls -la "$DEST"
