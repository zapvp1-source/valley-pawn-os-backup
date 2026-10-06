#!/bin/bash
# desktop_cleanup.sh — native replacement for Cowork `nightly-desktop-cleanup` (03:00, 2026-09-30).
# The SKILL's exact rules: sort loose FILES on ~/Desktop into Documents/Photos/Spreadsheets/Videos/Other
# by extension; skip .DS_Store/.localized/Thumbs.db/desktop.ini/~$* and all folders; mv -n (never
# overwrite; a collision leaves the file where it is); never delete. Silent; receipt with the counts.
AGENT="nightly-desktop-cleanup"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
D="$HOME/Desktop"; cd "$D" || { ledger "$AGENT" "The Desktop folder could not be opened for tonight's cleanup." "no"; exit 1; }
[ $RENDER -eq 0 ] && mkdir -p Documents Photos Spreadsheets Videos Other
nd=0; np=0; ns=0; nv=0; no=0
while IFS= read -r f; do
  n=$(basename "$f")
  case "$n" in .DS_Store|.localized|Thumbs.db|desktop.ini|'~$'*) continue;; esac
  ext=$(echo "${n##*.}" | tr 'A-Z' 'a-z'); [ "$ext" = "$n" ] && ext=""
  case "$ext" in pdf|docx|doc|eml) t=Documents;; png|jpg|jpeg|heic) t=Photos;; xlsx|csv|xltx|xls) t=Spreadsheets;; mov|mp4) t=Videos;; *) t=Other;; esac
  if [ $RENDER -eq 1 ]; then echo "would move: $n -> $t"; continue; fi
  [ -e "$t/$n" ] && continue
  mv -n "$f" "$t/" && case $t in Documents) nd=$((nd+1));; Photos) np=$((np+1));; Spreadsheets) ns=$((ns+1));; Videos) nv=$((nv+1));; *) no=$((no+1));; esac
done < <(find . -maxdepth 1 -type f)
[ $RENDER -eq 1 ] && exit 0
NOTE="moved Documents=$nd Photos=$np Spreadsheets=$ns Videos=$nv Other=$no"
vlog "$NOTE"; $PY "$BIN/vp_receipt.py" write "$AGENT" --surface file --target "$D" --note "$NOTE" >/dev/null 2>&1
