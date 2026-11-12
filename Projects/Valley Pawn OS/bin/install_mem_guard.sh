#!/bin/bash
# One-time installer for the memory guard (com.valleypawn.mem-guard + mem-guard-nightly).
# Safe to re-run (idempotent). Run:  bash ~/Documents/Claude/Projects/Valley\ Pawn\ OS/bin/install_mem_guard.sh
set -u
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
SCRIPT="$BIN/mem_guard.sh"
LA="$HOME/Library/LaunchAgents"
LOGS="$HOME/Library/Logs/valleypawn"
RUNNER="$HOME/bin/vp-runner"
mkdir -p "$LA" "$LOGS"
[ -f "$SCRIPT" ] || { echo "mem_guard.sh not synced yet — wait a minute and re-run."; exit 1; }
chmod +x "$SCRIPT" 2>/dev/null
if [ -x "$RUNNER" ]; then PROG="<string>$RUNNER</string><string>$SCRIPT</string>"
else PROG="<string>/bin/bash</string><string>$SCRIPT</string>"; fi

write_plist() { # label mode schedule-xml
cat > "$LA/$1.plist" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$1</string>
  <key>ProgramArguments</key><array>$PROG</array>
  <key>EnvironmentVariables</key><dict><key>MEM_GUARD_MODE</key><string>$2</string></dict>
  $3
  <key>StandardOutPath</key><string>$LOGS/$1.out.log</string>
  <key>StandardErrorPath</key><string>$LOGS/$1.err.log</string>
</dict>
</plist>
PL
plutil -lint "$LA/$1.plist" >/dev/null || { echo "bad plist $1"; exit 1; }
launchctl bootout "gui/$(id -u)/$1" 2>/dev/null
launchctl bootstrap "gui/$(id -u)" "$LA/$1.plist" && echo "loaded $1"
}

write_plist com.valleypawn.mem-guard watch \
  "<key>StartInterval</key><integer>900</integer><key>RunAtLoad</key><true/>"
write_plist com.valleypawn.mem-guard-nightly nightly \
  "<key>StartCalendarInterval</key><dict><key>Hour</key><integer>3</integer><key>Minute</key><integer>50</integer></dict>"

# keep a copy alongside the other fleet plists
FLEET="$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet"
[ -d "$FLEET" ] && cp "$LA"/com.valleypawn.mem-guard*.plist "$FLEET/" 2>/dev/null
sleep 5
launchctl list | grep mem-guard
tail -3 "$LOGS/mem_guard.log" 2>/dev/null
echo "DONE — memory guard installed."
