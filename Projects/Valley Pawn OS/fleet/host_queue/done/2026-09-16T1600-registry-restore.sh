#!/bin/bash
# HOST JOB — restore the pre-wipe scheduled-task registry (193 tasks, 13:34 ET copy) into the LIVE legacy store,
# via the registry guard (quiesce -> back up wiped file -> copy -> relaunch -> verify -> one plain DM).
set +e
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
SRC="$OS/fleet/_backups/registry/scheduled-tasks.json"
AUTO="$OS/fleet/_backups/registry/auto"; mkdir -p "$AUTO"
echo "=== registry-restore $(date) ==="
/usr/bin/python3 -c "
import json;d=json.load(open('$SRC'));st=d['scheduledTasks'];print('source:',len(st),'tasks',sum(1 for t in st if t.get('enabled')),'enabled; nulls:',[k for t in st for k,v in t.items() if v is None])"
cp "$SRC" "$AUTO/latest-good.json"; cp "$SRC" "$AUTO/scheduled-tasks-$(date +%Y%m%d-%H%M%S)-seed.json"; echo "seeded latest-good"
rm -f "$OS/fleet/host_queue/.registry_guard_force_relaunch"
/usr/bin/python3 "$OS/bin/registry_guard.py" --diag --restore "$SRC" 2>&1
echo "guard rc=$?"
echo "--- post ---"
ps -axo pid=,lstart=,comm= | grep -F '/Applications/Claude.app/Contents/MacOS/Claude' | grep -v grep
for p in "$HOME/Library/Application Support/Claude/local-agent-mode-sessions"/*/*/scheduled-tasks.json; do echo "$(stat -f '%Sm %z' -t '%F %T' "$p") $(/usr/bin/python3 -c "import json;print(len(json.load(open('$p'))['scheduledTasks']),'tasks')")"; done
grep -c ZodError "$HOME/Library/Logs/Claude/main.log"
grep -n "ScheduledTasks\]" "$HOME/Library/Logs/Claude/main.log" | tail -6 | cut -c1-200
echo "=== done $(date) ==="
