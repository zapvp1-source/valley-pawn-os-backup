#!/bin/bash
# One-time installer for disk guard (com.valleypawn.disk-guard + disk-guard-report). Idempotent.
set -u
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"; SCRIPT="$BIN/disk_guard.sh"
LA="$HOME/Library/LaunchAgents"; LOGS="$HOME/Library/Logs/valleypawn"; RUNNER="$HOME/bin/vp-runner"
mkdir -p "$LA" "$LOGS"
[ -f "$SCRIPT" ] || { echo "disk_guard.sh not synced yet — wait a minute and re-run."; exit 1; }
chmod +x "$SCRIPT" 2>/dev/null
if [ -x "$RUNNER" ]; then PROG="<string>$RUNNER</string><string>$SCRIPT</string>"; else PROG="<string>/bin/bash</string><string>$SCRIPT</string>"; fi
write_plist() {
cat > "$LA/$1.plist" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$1</string>
  <key>ProgramArguments</key><array>$PROG</array>
  <key>EnvironmentVariables</key><dict><key>DISK_GUARD_MODE</key><string>$2</string></dict>
  $3
  <key>LowPriorityIO</key><true/>
  <key>Nice</key><integer>15</integer>
  <key>StandardOutPath</key><string>$LOGS/$1.out.log</string>
  <key>StandardErrorPath</key><string>$LOGS/$1.err.log</string>
</dict>
</plist>
PL
plutil -lint "$LA/$1.plist" >/dev/null || { echo "bad plist $1"; exit 1; }
launchctl bootout "gui/$(id -u)/$1" 2>/dev/null
launchctl bootstrap "gui/$(id -u)" "$LA/$1.plist" && echo "loaded $1"
}
write_plist com.valleypawn.disk-guard clean "<key>StartCalendarInterval</key><dict><key>Hour</key><integer>4</integer><key>Minute</key><integer>10</integer></dict>"
write_plist com.valleypawn.disk-guard-report report "<key>StartCalendarInterval</key><dict><key>Weekday</key><integer>0</integer><key>Hour</key><integer>4</integer><key>Minute</key><integer>20</integer></dict><key>RunAtLoad</key><true/>"
FLEET="$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet"; [ -d "$FLEET" ] && cp "$LA"/com.valleypawn.disk-guard*.plist "$FLEET/" 2>/dev/null
launchctl list | grep disk-guard
echo "DONE — disk guard installed. First space report is running in the background (a few minutes)."
