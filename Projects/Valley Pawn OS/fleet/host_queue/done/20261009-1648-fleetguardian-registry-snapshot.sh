#!/bin/bash
set +e
OUT="$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/host_queue/done/fleetguardian-registry-snapshot-20261009-1648"
mkdir -p "$OUT"
SRC="$HOME/Library/Application Support/Claude/local-agent-mode-sessions"
find "$SRC" -maxdepth 3 -name 'scheduled-tasks.json' -not -name '*.bak*' > "$OUT/registry-paths.txt" 2>&1
i=0
while IFS= read -r f; do
  i=$((i+1))
  cp "$f" "$OUT/registry-$i.json" 2>>"$OUT/errors.txt"
done < "$OUT/registry-paths.txt"
ls -la "$HOME/Documents/Claude/Scheduled" > "$OUT/scheduled-dir-listing.txt" 2>&1
date -u > "$OUT/host-time-utc.txt"
date > "$OUT/host-time-local.txt"
echo done > "$OUT/STATUS"
