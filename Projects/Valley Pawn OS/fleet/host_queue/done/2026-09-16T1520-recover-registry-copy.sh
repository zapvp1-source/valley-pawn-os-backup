#!/bin/bash
# HOST JOB — obtain a pre-wipe copy of scheduled-tasks.json (Time Machine local snapshot or NAS backup) and
# stage it under fleet/_backups/registry/. NO restore in this job.
set +e
AS="$HOME/Library/Application Support/Claude"
REL="Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d"
DEST="$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/_backups/registry"; mkdir -p "$DEST"
echo "=== recover-registry-copy $(date) ==="
echo "--- why did the app reset? (quit-cleanup + startup store reads) ---"
sed -n 11,23p "$HOME/Library/Logs/Claude/main.log" | cut -c1-240
grep -n -i "account\|sign\|logout\|login\|auth" "$HOME/Library/Logs/Claude/main.log" | sed -n 1,25p | cut -c1-220
grep -n -B2 -A6 "\[ScheduledTasks\] Reset" "$HOME/Library/Logs/Claude/main.log" | cut -c1-240 | head -40

stage() { # $1=file $2=tag
  /usr/bin/python3 - "$1" "$2" "$DEST" <<'PY'
import json,sys,shutil,os,time
p,tag,dest=sys.argv[1:4]
try:
    d=json.load(open(p)); st=d.get('scheduledTasks',[])
    n=len(st); en=sum(1 for t in st if t.get('enabled'))
    print('   candidate',tag,'->',n,'tasks',en,'enabled',os.path.getsize(p),'bytes', time.strftime('%F %T',time.localtime(os.path.getmtime(p))))
    if n>=100:
        out=os.path.join(dest,'scheduled-tasks.%s.json'%tag); shutil.copy2(p,out); print('   STAGED',out)
except Exception as e: print('   candidate',tag,'ERR',e)
PY
}

echo; echo "--- 1) local APFS snapshots via device mount ---"
DEV=$(df "/System/Volumes/Data" | tail -1 | awk '{print $1}'); echo "data device: $DEV"
mkdir -p /tmp/vpsnap
for SNAP in $(tmutil listlocalsnapshots / 2>/dev/null | grep 2026-09-16 | sort -r); do
  echo "## $SNAP"
  mount_apfs -o rdonly,nobrowse -s "$SNAP" "$DEV" /tmp/vpsnap 2>&1
  if mount | grep -q /tmp/vpsnap; then
    ls -la "/tmp/vpsnap/$REL/" 2>&1 | grep -i sched
    for f in "/tmp/vpsnap/$REL"/scheduled-tasks.json*; do [ -f "$f" ] && stage "$f" "snap-${SNAP##*.TimeMachine.}-$(basename "$f" | sed 's/scheduled-tasks.json//;s/^\.//')"; done
    umount /tmp/vpsnap 2>/dev/null || diskutil unmount force /tmp/vpsnap >/dev/null 2>&1
    ls "$DEST" | grep -q snap && { echo "got a snapshot copy; stopping snapshot loop"; break; }
  fi
done

if ! ls "$DEST" 2>/dev/null | grep -q "snap-"; then
  echo; echo "--- 2) NAS Time Machine: start a backup so the destination gets mounted with stored credentials ---"
  tmutil startbackup 2>&1
  for i in $(seq 1 18); do sleep 10; LB=$(tmutil latestbackup 2>/dev/null); [ -n "$LB" ] && break; done
  echo "latestbackup: $LB"; tmutil status 2>&1 | grep -i "Running\|Percent\|Phase" | head -4
  if [ -n "$LB" ]; then
    BASE=$(dirname "$LB")
    for B in $(ls -1d "$BASE"/*.backup "$BASE"/20* 2>/dev/null | sort -r | head -6); do
      for f in "$B"/*/"$REL"/scheduled-tasks.json "$B/Data/$REL/scheduled-tasks.json"; do
        [ -f "$f" ] && { echo "## $f"; stage "$f" "tm-$(basename "$B" | tr -dc '0-9-' | cut -c1-15)"; }
      done
      ls "$DEST" | grep -q "tm-" && break
    done
  else
    echo "TM destination did not mount (no credentials in this context?)"
  fi
fi
echo; echo "--- staged copies ---"; ls -la "$DEST"
echo "=== done $(date) ==="
