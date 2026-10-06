#!/bin/bash
# storage_diag.sh — READ-ONLY storage/volume diagnostics for the host job queue (allow-listed).
#
# WHY: DISK_HEALTH.md has reported "Time Machine last success: unknown" as CRITICAL every 4 hours
# since 2026-09-04 (16 days of false alarm), and no existing allow-listed script can answer the
# three questions that actually matter when storage changes: what volumes are attached, how they
# are formatted, and where Time Machine is really pointed. host_diag.sh covers agents/registry/
# logs; this covers storage. Added 2026-09-20 when the Thunderbolt SSD arrived.
#
# READ-ONLY BY CONSTRUCTION: df / diskutil info / tmutil (query subcommands only) / du.
# It never formats, mounts, unmounts, erases, moves, or deletes anything.
#
#   storage_diag.sh [volumes|tm|tmprobe|tmcheck|space|big|all]     (default: all)
#
# bash 3.2 compatible (macOS /bin/bash).
set +e
sec() { echo; echo "--- $1 ---"; }

d_volumes() {
  sec "df -h (all mounted filesystems)"
  /bin/df -h
  sec "diskutil list"
  /usr/sbin/diskutil list
  sec "per-volume detail under /Volumes"
  for v in /Volumes/*; do
    [ -d "$v" ] || continue
    echo
    echo "### $v"
    /usr/sbin/diskutil info "$v" 2>&1 | grep -E \
      "Volume Name|Mounted|File System Personality|Type \(Bundle\)|Partition Type|Protocol|Disk Size|Volume Used Space|Container Free Space|Volume Free Space|Read-Only Volume|Device Node|Encrypted|Device Location|Solid State"
  done
}

d_tm() {
  sec "tmutil destinationinfo (where Time Machine is pointed)"
  /usr/bin/tmutil destinationinfo 2>&1
  sec "tmutil latestbackup"
  /usr/bin/tmutil latestbackup 2>&1
  sec "tmutil listbackups (last 5)"
  /usr/bin/tmutil listbackups 2>&1 | tail -5
  sec "tmutil listlocalsnapshots / (local snapshots eat internal space)"
  /usr/bin/tmutil listlocalsnapshots / 2>&1
  sec "TM preferences — LastDestination / result of last backup"
  /usr/bin/defaults read /Library/Preferences/com.apple.TimeMachine 2>&1 | grep -E \
    "LastKnownEncryptionState|BytesUsed|SnapshotDate|Result|DestinationID|LastDestinationID|kCSBackupd" | head -20
}

d_tmprobe() {
  sec "route 1 — defaults read com.apple.TimeMachine (no FDA needed)"
  /usr/bin/defaults read /Library/Preferences/com.apple.TimeMachine 2>&1 \
    | grep -E "SnapshotDates|BackupDates|[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}" \
    | tail -12
  sec "route 2 — dated .backup directories on the mounted destination"
  /usr/bin/find /Volumes/.timemachine -maxdepth 2 -name "*.backup" 2>/dev/null \
    | sed 's#.*/##' | sort | tail -3
  sec "route 3 — mounted TM destination snapshot mounts (from mount table)"
  /sbin/mount | grep -oE "com\.apple\.TimeMachine\.[0-9-]+\.(backup|local)" | sort | tail -3
}

d_tmcheck() {
  sec "what disk_health_sentinel NOW computes for 'last successful Time Machine backup'"
  /usr/bin/python3 -c '
import sys, time
sys.path.insert(0, "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin")
import disk_health_sentinel as d
for name, fn in (("route1 tmutil (needs FDA)", d._tm_from_tmutil),
                 ("route2 TM preferences   ", d._tm_from_prefs),
                 ("route3 mounted snapshot ", d._tm_from_mounts)):
    t = fn()
    print("  %s -> %s" % (name, time.strftime("%Y-%m-%d %H:%M:%S local", time.localtime(t)) if t else "None"))
age = d.tm_last_success_age_hours()
print("  RESULT: %s" % ("%.1f hours ago" % age if age is not None else "unknown"))
print("  VERDICT: %s" % ("would still be CRITICAL" if age is None or age > 72 else "healthy - no alarm"))
' 2>&1
}

d_space() {
  sec "internal volume group"
  /usr/sbin/diskutil info / 2>&1 | grep -E "Volume Name|Disk Size|Volume Used Space|Container Free Space|Volume Free Space"
  /usr/sbin/diskutil info /System/Volumes/Data 2>&1 | grep -E "Volume Name|Disk Size|Volume Used Space|Container Free Space|Volume Free Space"
  sec "purgeable / available (statvfs view)"
  /usr/bin/python3 -c 'import os,sys
for p in ("/","/System/Volumes/Data"):
    s=os.statvfs(p)
    g=lambda n: n*s.f_frsize/1024/1024/1024
    print("%-26s size %7.1fG  free %7.1fG  avail %7.1fG" % (p, g(s.f_blocks), g(s.f_bfree), g(s.f_bavail)))' 2>&1
}

d_big() {
  sec "the five folders that historically fill this disk (du, may take ~60s)"
  for d in \
    "$HOME/Library/Application Support/Claude" \
    "$HOME/Parallels" \
    "$HOME/Documents/Claude/Projects/Bravo Data Extraction/output" \
    "$HOME/Documents/Claude/Projects/Unified Search" \
    "$HOME/Library/CloudStorage" ; do
    if [ -e "$d" ]; then /usr/bin/du -sh "$d" 2>/dev/null; else echo "   (absent) $d"; fi
  done
  sec "Parallels VM bundles"
  /usr/bin/find "$HOME" -maxdepth 4 -name "*.pvm" -prune -exec /usr/bin/du -sh {} \; 2>/dev/null
}

[ $# -eq 0 ] && set -- all
while [ $# -gt 0 ]; do
  case "$1" in
    all)     d_volumes; d_space; d_tm; d_tmprobe; d_tmcheck; d_big ;;
    volumes) d_volumes ;;
    tm)      d_tm ;;
    tmprobe) d_tmprobe ;;
    tmcheck) d_tmcheck ;;
    space)   d_space ;;
    big)     d_big ;;
    *) echo "unknown section: $1  (volumes|tm|tmprobe|tmcheck|space|big|all)" ;;
  esac
  shift
done
exit 0
