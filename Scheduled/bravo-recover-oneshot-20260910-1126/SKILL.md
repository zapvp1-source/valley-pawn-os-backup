---
name: bravo-recover-oneshot-20260910-1126
description: One-shot Bravo full relaunch recovery after health-gate FAIL no-dashboard for stalled pawn-walk trigger
---

Run exactly this one command via mcp__Control_your_Mac__osascript and report the raw output, then stop: do shell script "/usr/local/bin/prlctl exec '{7dc84f03-4e68-4f43-9596-bf8a7dfb8e0a}' --current-user powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Y:\Documents\Claude\Projects\Bravo Data Extraction\_relaunch_bravo_and_watcher.ps1'". Do nothing else. This is a one-shot Bravo full relaunch recovery per BRAVO_KNOWN_ISSUES.md canonical mechanism (prlctl exec must run from a scheduled-task session, not interactive). The health gate already reported FAIL no-dashboard, so a full relaunch (not just watcher restart) is needed.