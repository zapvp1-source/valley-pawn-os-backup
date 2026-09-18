#!/bin/bash
# HOST JOB — inspect the second registry (claude-code-sessions), app-migration log lines, and Time Machine sources.
set +e
AS="$HOME/Library/Application Support/Claude"
NEW="$AS/claude-code-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d"
OLD="$AS/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d"
echo "=== registry-sources $(date) ==="
echo "--- claude-code-sessions tree ---"; ls -laR "$AS/claude-code-sessions" 2>/dev/null | head -60
echo; echo "--- NEW registry ---"; stat -f '%Sm %z bytes' -t '%F %T' "$NEW/scheduled-tasks.json" 2>&1; head -c 1500 "$NEW/scheduled-tasks.json" 2>&1; echo
/usr/bin/python3 -c "
import json,sys
for p in ['$NEW/scheduled-tasks.json','$OLD/scheduled-tasks.json']:
    try:
        d=json.load(open(p)); st=d.get('scheduledTasks',[]); print(p.split('Claude/')[1], '->', len(st),'tasks', sum(1 for t in st if t.get('enabled')),'enabled; keys', list(d.keys()))
    except Exception as e: print(p, 'ERR', e)
"
echo; echo "--- OLD dir full listing ---"; ls -la "$OLD" | head -40
echo; echo "--- Claude logs dir ---"; ls -la "$HOME/Library/Logs/Claude/" | head -20
echo; echo "--- main.log: first 60 lines after launch (14:40-14:42) ---"
grep -n "2026-09-16 14:4[0-1]" "$HOME/Library/Logs/Claude/main.log" | grep -v "process-memory" | head -60 | cut -c1-260
echo; echo "--- main.log: migration / scheduled / legacy / sessions-dir lines ---"
grep -n -i "migrat\|legacy\|claude-code-sessions\|scheduled-tasks\|scheduledTask\|SchedulerService\|\[scheduler\]\|task registry\|registry" "$HOME/Library/Logs/Claude/main.log" | grep -v "wake-scheduler\|\"name\": \"scheduled-tasks\"" | head -60 | cut -c1-300
echo; echo "--- older logs mentioning the registry (main1/main2, last lines) ---"
for l in "$HOME/Library/Logs/Claude"/main[0-9].log; do [ -f "$l" ] && { echo "## $l $(head -1 "$l" | cut -c1-19) .. $(tail -1 "$l" | cut -c1-19)"; grep -n -i "scheduled-tasks\|ZodError\|migrat" "$l" | tail -8 | cut -c1-260; }; done
echo; echo "--- Time Machine ---"
tmutil destinationinfo 2>&1 | head -12
LB=$(tmutil latestbackup 2>/dev/null); echo "latestbackup: $LB"
if [ -n "$LB" ]; then
  for c in "$LB/Data/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json" "$LB/Macintosh HD - Data/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json"; do
    [ -f "$c" ] && { echo "TM COPY: $(stat -f '%Sm %z' -t '%F %T' "$c")  $c"; }
  done
fi
echo "--- local snapshot mount attempt (read-only) ---"
SNAP=$(tmutil listlocalsnapshots / 2>/dev/null | grep "2026-09-16-135819" | head -1); echo "snap=$SNAP"
mkdir -p /tmp/vpsnap
if [ -n "$SNAP" ]; then
  mount_apfs -o rdonly,nobrowse -s "$SNAP" /System/Volumes/Data /tmp/vpsnap 2>&1 && echo MOUNTED
  ls -la "/tmp/vpsnap/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/" 2>&1 | head -20
  S="/tmp/vpsnap/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json"
  if [ -f "$S" ]; then
    mkdir -p "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/_backups"
    cp "$S" "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/_backups/scheduled-tasks.json.tm-135819" && echo "COPIED snapshot registry to fleet/_backups/scheduled-tasks.json.tm-135819"
    for b in "/tmp/vpsnap/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/"scheduled-tasks.json.bak*; do [ -f "$b" ] && cp "$b" "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/_backups/" && echo "copied $(basename "$b")"; done
    /usr/bin/python3 -c "import json;d=json.load(open('$S'));st=d['scheduledTasks'];print('SNAPSHOT registry:',len(st),'tasks',sum(1 for t in st if t.get('enabled')),'enabled')"
  fi
  umount /tmp/vpsnap 2>&1; diskutil unmount /tmp/vpsnap 2>&1 | head -2
fi
echo "=== done $(date) ==="
