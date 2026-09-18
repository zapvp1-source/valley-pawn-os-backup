#!/bin/bash
# HOST JOB — try reading the registry from the mounted local snapshots (13:58 / 11:31 today) and NAS backups by direct path.
set +e
REL="Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/scheduled-tasks.json"
DEST="$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/_backups/registry"; mkdir -p "$DEST"
echo "=== localsnap-copy $(date) ==="; tmutil status 2>&1 | grep -i "Running\|Percent" | head -2
stage() { /usr/bin/python3 - "$1" "$2" "$DEST" <<'PY'
import json,sys,shutil,os,time
p,tag,dest=sys.argv[1:4]
try:
    d=json.load(open(p)); st=d.get('scheduledTasks',[]); n=len(st); en=sum(1 for t in st if t.get('enabled'))
    print('   candidate',tag,'->',n,'tasks',en,'enabled',os.path.getsize(p),'bytes',time.strftime('%F %T',time.localtime(os.path.getmtime(p))))
    if n>=100: out=os.path.join(dest,'scheduled-tasks.%s.json'%tag); shutil.copy2(p,out); print('   STAGED',out)
except Exception as e: print('   candidate',tag,'ERR',e)
PY
}
for S in 2026-09-16-135819 2026-09-16-133206 2026-09-16-113117 2026-09-16-083019; do
  P="/Volumes/com.apple.TimeMachine.localsnapshots/Backups.backupdb/Mac Studio (2)/$S/Data/$REL"
  echo "## local snapshot $S"; ls -la "$P" 2>&1 | cut -c1-200; [ -f "$P" ] && stage "$P" "localsnap-$S"
  ls "$DEST" | grep -q localsnap && break
done
if ! ls "$DEST" | grep -q localsnap; then
  for B in 2026-09-16-123732 2026-09-16-102742 2026-09-16-072006 2026-09-16-043423 2026-09-15-223711; do
    for P in "/Volumes/.timemachine/CD580F56-1342-4622-93A2-04D09690683E/$B.backup/$B.backup/Macintosh HD - Data/$REL" "/Volumes/.timemachine/CD580F56-1342-4622-93A2-04D09690683E/$B.backup/Macintosh HD - Data/$REL" "/Volumes/Backups of Mac Studio (2)/$B.backup/Macintosh HD - Data/$REL"; do
      echo "## $P"; ls -la "$P" 2>&1 | cut -c1-200; [ -f "$P" ] && stage "$P" "tm-$B"
    done
    ls "$DEST" | grep -q "tm-" && break
  done
fi
echo "--- Full Disk Access check: can vp-runner read ~/Library/Mail? ---"; ls "$HOME/Library/Mail" 2>&1 | head -2
echo "--- staged ---"; ls -la "$DEST"; echo "=== done $(date) ==="
