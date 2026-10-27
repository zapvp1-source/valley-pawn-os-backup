#!/bin/bash
# Installs the Waynesboro door counter as an always-on launchd job on the Mac Studio host.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
export VPST_DIR="$HOME/.vp_secrets/store_traffic"
VENV="$HOME/.vp-studio/store-traffic-venv"
mkdir -p "$VPST_DIR/models" "$HOME/Library/Logs/ValleyPawn"; chmod 700 "$VPST_DIR"
[ -d "$VENV" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q aiortc opencv-python-headless onnxruntime numpy
[ -f "$VPST_DIR/models/yolox_s.onnx" ] || curl -sSL -o "$VPST_DIR/models/yolox_s.onnx" \
  "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/object_detection_yolox/object_detection_yolox_2022nov.onnx"
[ -f "$VPST_DIR/sdm_oauth.json" ] || VPST_DIR="$VPST_DIR" "$VENV/bin/python" "$HERE/mint_token.py"
PL="$HOME/Library/LaunchAgents/com.valleypawn.storetraffic.waynesboro.plist"
cat > "$PL" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.valleypawn.storetraffic.waynesboro</string>
  <key>ProgramArguments</key><array>
    <string>$VENV/bin/python</string><string>$HERE/counter.py</string><string>Waynesboro</string><string>--until-close</string>
  </array>
  <key>EnvironmentVariables</key><dict><key>VPST_DIR</key><string>$VPST_DIR</string></dict>
  <key>WorkingDirectory</key><string>$HERE</string>
  <key>StartCalendarInterval</key><array>
$(for d in 1 2 3 4 5 6; do echo "    <dict><key>Weekday</key><integer>$d</integer><key>Hour</key><integer>9</integer><key>Minute</key><integer>57</integer></dict>"; done)
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>SuccessfulExit</key><false/></dict>
  <key>ThrottleInterval</key><integer>60</integer>
  <key>StandardOutPath</key><string>$HOME/Library/Logs/ValleyPawn/storetraffic-waynesboro.log</string>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/ValleyPawn/storetraffic-waynesboro.log</string>
</dict></plist>
PLIST
launchctl bootout "gui/$(id -u)" "$PL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PL"
echo "INSTALLED: $(launchctl list | grep storetraffic)"
