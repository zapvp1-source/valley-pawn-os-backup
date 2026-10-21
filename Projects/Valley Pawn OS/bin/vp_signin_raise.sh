#!/bin/bash
# vp_signin_raise.sh — bring the automation-profile Chrome window(s) on-screen and to the front (2026-10-20).
# The pw-vp profile remembers the off-screen parking position (-2400,-2400) used by the headless-style checks,
# so a sign-in window can open where nobody can see it. This moves every window of that Chrome process to the
# main screen, un-minimizes it, and makes it frontmost. Touches nothing else.
PROFILE="${VP_SIGNIN_PROFILE:-$HOME/Library/Application Support/valleypawn/pw-geo}"
PID=$(pgrep -f -- "Google Chrome --user-data-dir=$PROFILE" | head -1)
if [ -z "$PID" ]; then echo "no automation Chrome running"; exit 2; fi
osascript <<OSA
tell application "System Events"
  set p to first process whose unix id is $PID
  set visible of p to true
  set frontmost of p to true
  set i to 0
  repeat with w in windows of p
    set i to i + 1
    try
      set value of attribute "AXMinimized" of w to false
    end try
    set position of w to {80 + (i - 1) * 30, 60 + (i - 1) * 30}
    set size of w to {1400, 950}
    try
      perform action "AXRaise" of w
    end try
  end repeat
  return "raised " & i & " window(s) of pid $PID"
end tell
OSA
