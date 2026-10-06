#!/bin/bash
# drive_path_probe.sh — list the Google Drive for Desktop mounts and the reports folder candidates (read-only)
ls -d "$HOME/Library/CloudStorage/"* 2>&1
find "$HOME/Library/CloudStorage" -maxdepth 6 -type d -iname "*Gift Card*" 2>/dev/null | head -5
find "$HOME/Library/CloudStorage" -maxdepth 5 -type d -iname "08 Reports*" 2>/dev/null | head -5
