#!/bin/bash
# chrome_extension_watchdog.sh — com.valleypawn.chrome-extension-watchdog  (v2, 2026-09-09)
#
# WHY THIS EXISTS: every browser-driving automation reaches Chrome through the
# Claude-in-Chrome extension, which talks to a cloud bridge
# (wss://bridge.claudeusercontent.com) that the Claude desktop app also connects to.
# The extension only holds that connection while its service worker is running.
# After a Chrome restart (or an idle eviction) the worker can sit dormant, the bridge
# reports "No Chrome extension connected after discovery", and every browser task in
# the fleet fails until a human pokes the extension. Joshua was doing that by hand.
#
# HOW IT HEALS (no keystrokes, no Accessibility permission needed):
#   Opening ANY page of the extension (chrome-extension://<id>/options.html) starts
#   its service worker, which immediately reconnects to the bridge. Verified 2026-09-09:
#   opening an extension page -> desktop log "Selected Chrome extension" within seconds.
#   Second-tier heal: open pairing.html and click "Connect" (re-pairs with the desktop).
#
# HEALTH SIGNAL: the Claude desktop app's own log (~/Library/Logs/Claude/main.log).
#   GOOD (latest wins): "Chrome extension connected to bridge", "Selected Chrome extension",
#                       "Previously selected extension reconnected"
#   BAD  (latest wins): "Chrome extension disconnected from bridge",
#                       "No Chrome extension connected after discovery"
#   Healthy when the most recent of these lines is a GOOD one (or there are none).
#
# Runs every 2 min via launchd; silent when healthy; one log line per action to
# ~/Library/Logs/valleypawn/chrome-extension-watchdog.log
#
# Canonical copy: ~/Documents/Claude/Projects/Valley Pawn OS/bin/chrome_extension_watchdog.sh
# Runtime copy (launchd executes this one — TCC blocks launchd exec under ~/Documents):
#   ~/Library/Application Support/valleypawn/bin/chrome_extension_watchdog.sh
# Keep both in sync when editing.

LOGDIR="$HOME/Library/Logs/valleypawn"; mkdir -p "$LOGDIR"
LOG="$LOGDIR/chrome-extension-watchdog.log"
ts() { date "+%Y-%m-%d %H:%M:%S"; }
log() { echo "$(ts) $*" >> "$LOG"; }

CLAUDE_LOG="$HOME/Library/Logs/Claude/main.log"
EXT_ID="fcoeoabgfenejglbffodgkkbkcdhcgfn"
GOOD_RE='Chrome extension connected to bridge|Selected Chrome extension|Previously selected extension reconnected'
BAD_RE='Chrome extension disconnected from bridge|No Chrome extension connected after discovery'

# ---- 1. Claude desktop app (bridge endpoint) --------------------------------------
if ! ps -axo comm | grep -q '^/Applications/Claude.app/Contents/MacOS/Claude$'; then
  open -ga "Claude"; log "RELAUNCHED Claude desktop app (bridge endpoint was down)"; sleep 15
fi

# ---- 2. Chrome ----------------------------------------------------------------------
if ! pgrep -xq "Google Chrome"; then
  open -ga "Google Chrome"; log "RELAUNCHED Chrome (was not running)"; sleep 12
fi

# ---- 3. Health from the desktop app's log --------------------------------------------
state() {
  # prints GOOD, BAD, or NONE based on the most recent matching line
  local last
  last=$(tail -n 4000 "$CLAUDE_LOG" 2>/dev/null | grep -E "$GOOD_RE|$BAD_RE" | tail -1)
  [ -z "$last" ] && { echo NONE; return; }
  if echo "$last" | grep -qE "$BAD_RE"; then echo BAD; else echo GOOD; fi
}
S=$(state)
[ -n "$FORCE_HEAL" ] && S=BAD && log "FORCE_HEAL set — exercising heal path for test"
[ "$S" != "BAD" ] && exit 0

# ---- 4. Heal tier 1: start the extension's service worker by opening one of its pages --
open_ext_page() {   # $1 = page (options.html | pairing.html)   prints tab-open result
  osascript <<AS 2>/dev/null
tell application "Google Chrome"
  if (count of windows) = 0 then make new window
  tell window 1
    set keepIdx to active tab index
    set t to make new tab with properties {URL:"chrome-extension://$EXT_ID/$1"}
    delay 6
    try
      set active tab index to keepIdx
    end try
    -- close the helper tab (find it by URL so we never close the wrong one)
    repeat with i from (count of tabs) to 1 by -1
      if URL of tab i starts with "chrome-extension://$EXT_ID/$1" then close tab i
    end repeat
  end tell
end tell
AS
}

log "extension not on bridge (desktop log: BAD) — tier 1: opening options.html to start the service worker"
open_ext_page options.html
sleep 12
S=$(state)
if [ "$S" = "GOOD" ]; then log "RECOVERED — extension reconnected to bridge after tier 1"; exit 0; fi

# ---- 5. Heal tier 2: re-pair with the desktop app via pairing.html + Connect ---------
log "tier 1 did not reconnect — tier 2: pairing.html → Connect (name: Mac Studio)"
osascript <<AS 2>/dev/null
tell application "Google Chrome"
  if (count of windows) = 0 then make new window
  tell window 1
    set keepIdx to active tab index
    set t to make new tab with properties {URL:"chrome-extension://$EXT_ID/pairing.html"}
    delay 5
    try
      execute t javascript "(function(){var inp=document.querySelector('input[type=text],input:not([type])'); if(inp){var s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set; s.call(inp,'Mac Studio'); inp.dispatchEvent(new Event('input',{bubbles:true}));} var b=[...document.querySelectorAll('button')].find(x=>/connect/i.test(x.innerText)); if(b){b.click();return 'ok';} return 'nobtn';})()"
    end try
    delay 6
    try
      set active tab index to keepIdx
    end try
    repeat with i from (count of tabs) to 1 by -1
      if URL of tab i starts with "chrome-extension://$EXT_ID/pairing.html" then close tab i
    end repeat
  end tell
end tell
AS
sleep 15
S=$(state)
if [ "$S" = "GOOD" ]; then log "RECOVERED — extension reconnected after tier 2 (re-pair)"; else log "FAILED — still not on bridge after tier 1+2 (check extension sign-in at chrome-extension://$EXT_ID/options.html, or Chrome 'Allow JavaScript from Apple Events')"; fi
exit 0
