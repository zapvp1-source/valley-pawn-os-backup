#!/bin/bash
exec > /tmp/dusweep.log 2>&1
echo "=== sweep $(date) ==="
du -xsk "$HOME"/* 2>/dev/null | sort -rn | head -15
echo '--- Library ---'
du -xsk "$HOME"/Library/* 2>/dev/null | sort -rn | head -12
echo '--- App Support ---'
du -xsk "$HOME/Library/Application Support"/* 2>/dev/null | sort -rn | head -10
echo '--- Caches ---'
du -xsk "$HOME/Library/Caches"/* 2>/dev/null | sort -rn | head -8
echo '--- Parallels ---'
du -xsk "$HOME/Parallels"/* 2>/dev/null | sort -rn | head -5
ls -lh "$HOME/Parallels" 2>/dev/null
echo '--- Unified Search dir ---'
du -xsk "$HOME/Documents/Claude/Projects/Unified Search"/* 2>/dev/null | sort -rn | head -8
echo '--- Trash / logs ---'
du -xsk "$HOME/.Trash" "$HOME/Library/Logs" 2>/dev/null
echo '--- local snapshots ---'
tmutil listlocalsnapshots / 2>/dev/null
echo "=== done $(date) ==="
