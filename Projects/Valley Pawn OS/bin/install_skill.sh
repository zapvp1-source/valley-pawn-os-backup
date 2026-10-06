#!/bin/bash
# install_skill.sh <task-id> <source SKILL.md>  — allow-listed, path-restricted way to update a scheduled task's
# prompt from the host: backs up ~/Documents/Claude/Scheduled/<id>/SKILL.md, verifies the source's frontmatter
# names the same task, copies it in. (Freeze rule 2: one task at a time, with a backup — this IS that.)
ID="$1"; SRC="$2"; DST="$HOME/Documents/Claude/Scheduled/$ID/SKILL.md"
case "$ID" in ""|*/*|*..*) echo "REFUSED: bad task id '$ID'"; exit 2;; esac
[ -f "$SRC" ] || { echo "REFUSED: source missing $SRC"; exit 2; }
[ -f "$DST" ] || { echo "REFUSED: $DST does not exist (this only updates existing tasks)"; exit 2; }
head -5 "$SRC" | grep -q "^name: $ID\$" || { echo "REFUSED: source frontmatter is not name: $ID"; exit 2; }
BK="$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/_backups/skills"; mkdir -p "$BK"
cp "$DST" "$BK/$ID.SKILL.md.bak-$(date +%Y%m%d-%H%M%S)" && cp "$SRC" "$DST" && echo "installed $ID ($(wc -l < "$DST" | tr -d ' ') lines; backup in fleet/_backups/skills)"
