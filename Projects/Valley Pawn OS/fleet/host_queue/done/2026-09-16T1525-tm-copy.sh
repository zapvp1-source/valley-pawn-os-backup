#!/bin/bash
# HOST JOB — the NAS Time Machine backup is running (destination mounted). Find the newest backup that
# holds a non-empty scheduled-tasks.json and stage it. Keep the backup running.
set +e
REL="Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json"
DEST="$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/_backups/registry"; mkdir -p "$DEST"
echo "=== tm-copy $(date) ==="
tmutil status 2>&1 | grep -i "Running\|Percent\|Phase\|DestinationMountPoint" | head -5
echo "--- mounts ---"; mount | grep -i "timemachine\|backup\|smb" | cut -c1-200
echo "--- /Volumes ---"; ls -la /Volumes/ 2>&1; ls -la /Volumes/.timemachine/ 2>&1 | head; ls -la /Volumes/.timemachine/*/ 2>&1 | head -20
echo "--- tmutil listbackups ---"; tmutil listbackups 2>&1 | tail -8
echo "--- tmutil latestbackup -t ---"; tmutil latestbackup -t 2>&1
stage() {
  /usr/bin/python3 - "$1" "$2" "$DEST" <<'PY'
import json,sys,shutil,os,time
p,tag,dest=sys.argv[1:4]
try:
    d=json.load(open(p)); st=d.get('scheduledTasks',[]); n=len(st); en=sum(1 for t in st if t.get('enabled'))
    print('   candidate',tag,'->',n,'tasks',en,'enabled',os.path.getsize(p),'bytes',time.strftime('%F %T',time.localtime(os.path.getmtime(p))))
    if n>=100:
        out=os.path.join(dest,'scheduled-tasks.%s.json'%tag); shutil.copy2(p,out); print('   STAGED',out); sys.exit(0)
    sys.exit(3)
except Exception as e: print('   candidate',tag,'ERR',e); sys.exit(2)
PY
}
echo "--- search backups (newest first) ---"
CANDS=$( { tmutil listbackups 2>/dev/null; ls -d /Volumes/.timemachine/*/*.backup/*.backup /Volumes/.timemachine/*/*.backup "/Volumes/Backups of"*/Backups.backupdb/*/20* 2>/dev/null; } | sort -u | sort -r )
echo "$CANDS" | head -12
for B in $CANDS; do
  for f in "$B/Macintosh HD - Data/$REL" "$B/Data/$REL" "$B/$REL" "$B"/*/"$REL"; do
    if [ -f "$f" ]; then echo "## $f"; stage "$f" "tm-$(echo "$B" | grep -o '20[0-9-]*[0-9]' | tail -1)"; rc=$?; [ $rc -eq 0 ] && break 2; fi
  done
done
echo "--- fallback: find (bounded) ---"
[ -z "$(ls "$DEST" 2>/dev/null)" ] && find /Volumes/.timemachine -maxdepth 12 -path "*f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json" 2>/dev/null | head -5 | while read -r f; do echo "## $f"; stage "$f" "tm-find-$(echo "$f" | grep -o '20[0-9]\{2\}-[0-9]\{2\}-[0-9]\{2\}-[0-9]\{6\}' | head -1)"; done
echo "--- staged ---"; ls -la "$DEST"
echo "=== done $(date) ==="
