#!/bin/bash
# HOST JOB — locate the real scheduled-task registry (193 tasks) and any backups; explain the 14:40 reset.
set +e
AS="$HOME/Library/Application Support/Claude"
rm -f "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/host_queue/.registry_guard_force_relaunch"
echo "=== find-registry $(date) ==="
echo "--- App Support/Claude top level ---"; ls -la "$AS" | head -60
echo; echo "--- local-agent-mode-sessions tree (dirs, depth 2, with mtimes) ---"
ls -la "$AS/local-agent-mode-sessions/"; for d in "$AS/local-agent-mode-sessions"/*/; do echo "## $d"; ls -la "$d" | head -20; done
echo; echo "--- every scheduled-tasks.json* anywhere under ~/Library (any depth) ---"
find "$HOME/Library" -name 'scheduled-tasks.json*' -print0 2>/dev/null | xargs -0 -I{} sh -c 'echo "$(stat -f "%Sm %z" -t "%F %T" "{}")  {}"'
echo; echo "--- any file under App Support/Claude > 10KB containing \"scheduledTasks\" ---"
find "$AS" -type f -size +10k \( -name '*.json' -o -name '*.bak*' -o -name '*.log' \) 2>/dev/null | while read -r f; do grep -l '"scheduledTasks"' "$f" 2>/dev/null; done | while read -r f; do echo "$(stat -f "%Sm %z" -t "%F %T" "$f")  $f"; done
echo; echo "--- Spotlight ---"; mdfind -name scheduled-tasks.json 2>/dev/null | head
echo; echo "--- Trash ---"; ls -la "$HOME/.Trash" 2>/dev/null | grep -i "sched\|claude" | head
echo; echo "--- other backup spots ---"
ls -la "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/_backups" 2>/dev/null
ls -la "$HOME/Documents/Claude/Projects/.migration-staging" 2>/dev/null | head -30
find "$HOME/Documents/Claude" -maxdepth 3 -name '*scheduled-tasks*' 2>/dev/null
find "$HOME/Library/Application Support/valleypawn" -name '*.json*' 2>/dev/null | head
echo; echo "--- Time Machine latest snapshot for the registry dir? ---"
tmutil listlocalsnapshots / 2>/dev/null | tail -5
echo; echo "--- what happened 14:35-14:45 (previous app instance log = main1.log) ---"
for l in "$HOME/Library/Logs/Claude/main1.log" "$HOME/Library/Logs/Claude/main.log"; do
  [ -f "$l" ] || continue; echo "## $l"
  grep -n "2026-09-16 14:3[5-9]\|2026-09-16 14:4[0-2]" "$l" | grep -i -v "process-memory\|workspaceMcpServer\|Remote tool\|MCP tool call" | cut -c1-260 | tail -80
done
echo; echo "--- registry-related lines in main1.log (scheduler/registry/migrat/reset/wipe/write) ---"
grep -n -i "scheduled-tasks\|scheduler\|registry\|migrat\|wipe\|reset\|corrupt\|zod" "$HOME/Library/Logs/Claude/main1.log" 2>/dev/null | cut -c1-260 | tail -60
echo; echo "--- current empty registry content ---"; cat "$AS/local-agent-mode-sessions"/*/*/scheduled-tasks.json; echo
echo; echo "--- Scheduled task folders on disk ---"; ls "$HOME/Documents/Claude/Scheduled" | wc -l; ls -t "$HOME/Documents/Claude/Scheduled" | head -5
echo "=== done $(date) ==="
