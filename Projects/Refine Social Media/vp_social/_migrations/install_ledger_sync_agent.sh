#!/bin/bash
# Installs com.valleypawn.social-ledger-sync — nightly Publer -> ledger sync (11:10 PM),
# plus a light 7:10 AM refresh so the Monday planner always sees a current queue.
# Additive: touches no existing agent. Re-runnable.
set -euo pipefail

RSM="/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media"
PLIST="$HOME/Library/LaunchAgents/com.valleypawn.social-ledger-sync.plist"
LOGDIR="$RSM/state/logs"
mkdir -p "$LOGDIR"

# NOTE: the runner lives in $HOME, not under Documents/. launchd's bash cannot execute a
# script inside ~/Documents (TCC: "Operation not permitted") — same reason every other
# com.valleypawn.* agent keeps its shell script at the top of the home folder.
RUNNER="$HOME/vp_social_ledger_sync.sh"

cat > "$RUNNER" <<'EOS'
#!/bin/bash
RSM="/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media"
cd "$RSM" || exit 1
export PYTHONWARNINGS=ignore
/usr/bin/env python3 -m vp_social sync --back 21 --forward 30 \
  >> "$RSM/state/logs/ledger_sync.log" 2>&1
echo "$(date '+%Y-%m-%d %H:%M:%S') exit=$?" >> "$RSM/state/logs/ledger_sync.log"
EOS
chmod +x "$RUNNER"

cat > "$PLIST" <<EOP
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.valleypawn.social-ledger-sync</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$RUNNER</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Hour</key><integer>23</integer><key>Minute</key><integer>10</integer></dict>
    <dict><key>Hour</key><integer>7</integer><key>Minute</key><integer>10</integer></dict>
  </array>
  <key>StandardOutPath</key><string>$LOGDIR/ledger_sync.out</string>
  <key>StandardErrorPath</key><string>$LOGDIR/ledger_sync.err</string>
  <key>RunAtLoad</key><false/>
</dict>
</plist>
EOP

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
launchctl list | grep social-ledger-sync || echo "NOT LOADED"
echo "installed: $PLIST"
