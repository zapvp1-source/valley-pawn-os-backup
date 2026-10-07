#!/bin/bash
# copy_to_desktop.sh <file-or-folder...> — copy items from Valley Pawn OS/fleet/brand/ to Joshua's Desktop (nothing else).
SRC="$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/brand"
for f in "$@"; do b=$(basename "$f"); if [ -e "$SRC/$b" ]; then cp -Rp "$SRC/$b" "$HOME/Desktop/" && echo "copied $b"; fi; done
