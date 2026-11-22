#!/bin/bash
# tm_diag.sh — READ-ONLY Time Machine + background-item notification diagnostics (2026-11-21).
# Allow-listed for the host job queue. Changes nothing.
set +e
sec() { echo; echo "--- $1 ---"; }
if [ "$1" = "brief" ]; then
  date; tmutil status 2>&1 | grep -E "Running|Percent|BackupPhase"; echo "latest: $(tmutil latestbackup 2>&1)"
  defaults read /Library/Preferences/com.apple.TimeMachine 2>/dev/null | grep -E "RESULT|sessiondata"
  ( /usr/bin/log show --last 90m --style compact --predicate 'subsystem == "com.apple.TimeMachine" AND process == "backupd"' 2>&1 | grep -E "Backup failed|Backup completed|Copy stage failed|Starting|Finished copying|BackupDispatching|Backup result" | cut -c1-220 | tail -20 ) &
  LP=$!; ( sleep 90; kill $LP 2>/dev/null ) & wait $LP
  tail -4 "$HOME/Library/Logs/valleypawn/mem_guard.log"
  exit 0
fi
sec "date"; date
sec "tmutil status"; tmutil status 2>&1
sec "tmutil destinationinfo"; tmutil destinationinfo 2>&1
sec "tmutil latestbackup"; tmutil latestbackup 2>&1
sec "local snapshots"; tmutil listlocalsnapshots / 2>&1
sec "TM prefs"; defaults read /Library/Preferences/com.apple.TimeMachine 2>&1 | grep -v -i "password" | head -80
sec "mounts"; mount | grep -i -E "smb|afp|TimeMachine|Backups" 
sec "df"; df -g / /System/Volumes/Data 2>&1
sec "backupd log (last 5h, errors + lifecycle)"
( /usr/bin/log show --last 5h --style compact --predicate 'subsystem == "com.apple.TimeMachine"' 2>&1 | grep -i -E "fail|error|cancel|could not|couldn.t|unable|Starting|Backup completed|Finished|thin|Mount|disk image|network|timed out|not available|Stopping|stopp" | tail -150 ) &
LP=$!; ( sleep 100; kill $LP 2>/dev/null ) & wait $LP
sec "background task management notifications (last 24h)"
( /usr/bin/log show --last 24h --style compact --predicate 'process == "backgroundtaskmanagementd" OR process == "BackgroundTaskManagementAgent"' 2>&1 | grep -i -E "notif|post|added|register" | cut -c1-260 | tail -60 ) &
LP=$!; ( sleep 60; kill $LP 2>/dev/null ) & wait $LP
sec "LaunchAgents newest"; ls -lt "$HOME/Library/LaunchAgents" | head -15
sec "mem-guard log tail"; tail -30 "$HOME/Library/Logs/valleypawn/mem_guard.log" 2>&1
echo; echo DONE
exit 0
