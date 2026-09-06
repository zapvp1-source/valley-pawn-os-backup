#!/bin/bash
# Installs the two native launchd agents for Airthings monitoring (no Claude in the loop).
#   com.personal.airthings-poll    every 15 min  -> airthings_poll.py
#   com.personal.airthings-digest  07:30 daily   -> airthings_poll.py --digest
# Safe to re-run: bootout first, then bootstrap.
set -u
HERE="/Users/joshuadavis/Documents/Claude/Projects/Air Quality Monitoring"
PY="$(command -v python3 || echo /usr/bin/python3)"
LA="$HOME/Library/LaunchAgents"
mkdir -p "$LA"

write_plist() { # label, extra-args-xml, schedule-xml
cat > "$LA/$1.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$1</string>
  <key>ProgramArguments</key><array>
    <string>$PY</string>
    <string>$HERE/airthings_poll.py</string>$2
  </array>
  $3
  <key>StandardOutPath</key><string>$HERE/launchd.out.log</string>
  <key>StandardErrorPath</key><string>$HERE/launchd.err.log</string>
</dict></plist>
EOF
}

write_plist com.personal.airthings-poll "" "<key>StartInterval</key><integer>900</integer>
  <key>RunAtLoad</key><true/>"
write_plist com.personal.airthings-digest "
    <string>--digest</string>" "<key>StartCalendarInterval</key><dict><key>Hour</key><integer>7</integer><key>Minute</key><integer>30</integer></dict>"

plutil -lint "$LA/com.personal.airthings-poll.plist" "$LA/com.personal.airthings-digest.plist" || exit 1
for L in com.personal.airthings-poll com.personal.airthings-digest; do
  launchctl bootout "gui/$(id -u)/$L" 2>/dev/null
  launchctl bootstrap "gui/$(id -u)" "$LA/$L.plist" && echo "loaded $L"
done
sleep 3
launchctl list | grep airthings
tail -3 "$HERE/poll.log"
