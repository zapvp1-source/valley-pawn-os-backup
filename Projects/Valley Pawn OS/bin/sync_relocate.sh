#!/bin/bash
# sync_relocate.sh — move high-churn machine data OUT of ~/Documents (which Google Drive backs up as
# "My Mac" and iCloud syncs) into ~/.vp-studio/offsync, leaving a symlink at the old path so every
# script keeps working unchanged. Built 2026-11-07 after Drive sat at ~200% CPU for days re-uploading
# the 8.2 GB Unified Search index.db and the door counters' per-second detection logs.
# Idempotent: an entry that is already a symlink is skipped. A file still open by any process is
# deferred (re-run later; cpu_guard.sh retries it hourly). Same APFS volume -> mv is an instant rename.
# Usage: sync_relocate.sh [--dry-run]       bash 3.2 compatible.
set +e
P="$HOME/Documents/Claude/Projects"; OFF="$HOME/.vp-studio/offsync"; DRY="$1"
STATE="$P/Valley Pawn OS/fleet/state/sync_relocate.txt"
ENTRIES="unified-search|$P/Unified Search/index.db
store-traffic|$P/Store Traffic Counter/dets
store-traffic|$P/Store Traffic Counter/tracks
store-traffic|$P/Store Traffic Counter/audit
store-traffic|$P/Store Traffic Counter/evidence"
pending=0
echo "$ENTRIES" | while IFS='|' read -r grp src; do
  name=$(basename "$src"); dst="$OFF/$grp/$name"
  if [ -L "$src" ]; then echo "OK already relocated: $src -> $(readlink "$src")"; continue; fi
  if [ ! -e "$src" ]; then echo "SKIP missing: $src"; continue; fi
  if [ -f "$src" ]; then
    # a single file (sqlite db): only move when NO process has it or its journal/WAL open
    if /usr/sbin/lsof "$src" "$src-wal" "$src-shm" "$src-journal" >/dev/null 2>&1; then
      echo "DEFER (open by a process): $src"; echo "$(date '+%F %T') DEFER $src" >> "$STATE"; continue
    fi
  fi
  [ -e "$dst" ] && { echo "REFUSED: destination exists $dst"; continue; }
  if [ "$DRY" = "--dry-run" ]; then echo "WOULD move $src -> $dst"; continue; fi
  mkdir -p "$OFF/$grp"
  if ! mv "$src" "$dst" 2>/dev/null; then
    if [ -d "$src" ]; then
      # a whole-directory rename out of the iCloud/FileProvider-managed Documents tree can fail with
      # EDEADLK ("Resource deadlock avoided"); plain files rename fine -> move file by file, then link.
      for pass in 1 2 3; do
        ( cd "$src" && find . -type d ) | while read -r d; do mkdir -p "$dst/$d"; done
        ( cd "$src" && find . -type f ) | while read -r f; do mv "$src/$f" "$dst/$f" || echo "FAIL file $f"; done
        find "$src" -depth -type d -empty -exec rmdir {} \; 2>/dev/null
        [ -e "$src" ] || break
      done
      [ -e "$src" ] && { echo "FAIL could not empty $src (still has files)"; continue; }
    else
      echo "FAIL mv $src"; continue
    fi
  fi
  for ext in -wal -shm -journal; do [ -e "$src$ext" ] && mv "$src$ext" "$dst$ext"; done
  ln -s "$dst" "$src" && echo "MOVED $src -> $dst" && echo "$(date '+%F %T') MOVED $src -> $dst" >> "$STATE"
done
ls -la "$OFF"/* 2>/dev/null
exit 0
