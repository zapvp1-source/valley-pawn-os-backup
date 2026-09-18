#!/bin/bash
# chrome_tab_hygiene.sh — com.valleypawn.chrome-tab-hygiene
# Daily Chrome tab cleanup so automation residue + duplicate tabs never
# accumulate into memory bloat / frozen renderers.
#
# SAFETY RULES (do not weaken):
#   - Never closes the ACTIVE tab of any window (re-checked live before every close).
#   - Duplicate rule keeps the FIRST (leftmost) copy — pinned tabs are leftmost, so
#     pinned tabs survive even though Chrome's AppleScript API can't see "pinned".
#   - Only closes: (a) known automation-residue URLs, (b) exact-duplicate URLs.
#     It NEVER closes a unique tab Joshua may be using, no matter the tab count.
#   - Runs 5:10 AM — before the 6:30–8:15 Bravo corridor, when no Chrome-driving
#     task is scheduled (collision-safe by schedule, per bravo-context timing rules).
#
# Canonical copy: ~/Documents/Claude/Projects/Valley Pawn OS/bin/chrome_tab_hygiene.sh
# Runtime copy (what launchd executes — TCC blocks launchd exec under ~/Documents):
#   ~/Library/Application Support/valleypawn/bin/chrome_tab_hygiene.sh
# Keep both in sync when editing.

LOGDIR="$HOME/Library/Logs/valleypawn"
mkdir -p "$LOGDIR"
LOG="$LOGDIR/chrome-tab-hygiene.log"
ts() { date "+%Y-%m-%d %H:%M:%S"; }

if ! pgrep -xq "Google Chrome"; then
  echo "$(ts) Chrome not running — nothing to do" >> "$LOG"
  exit 0
fi

RESULT=$(osascript <<'APPLESCRIPT'
on isResidue(u)
  set residueList to {"about:blank", "chrome://newtab", "chrome://new-tab-page", "slack.com/app_redirect", "accounts.google.com/o/oauth2", "accounts.google.com/signin", "chrome-error://"}
  repeat with r in residueList
    if u contains (r as text) then return true
  end repeat
  return false
end isResidue

on indexOfURL(theList, u)
  repeat with i from 1 to count of theList
    if item i of theList is u then return i
  end repeat
  return 0
end indexOfURL

tell application "Google Chrome"
  set totalBefore to 0
  set closedResidue to 0
  set closedDupes to 0
  set urlList to {}
  set urlCounts to {}
  -- pass 1: census
  repeat with w in windows
    repeat with t in tabs of w
      set totalBefore to totalBefore + 1
      set u to URL of t
      set idx to my indexOfURL(urlList, u)
      if idx is 0 then
        set end of urlList to u
        set end of urlCounts to 1
      else
        set item idx of urlCounts to (item idx of urlCounts) + 1
      end if
    end repeat
  end repeat
  -- pass 2: close, right-to-left so kept-first == leftmost (pinned-safe)
  repeat with wi from (count of windows) to 1 by -1
    set w to window wi
    set n to count of tabs of w
    repeat with i from n to 1 by -1
      set activeIdx to active tab index of w
      if i is not activeIdx then
        set t to tab i of w
        set u to URL of t
        set idx to my indexOfURL(urlList, u)
        if my isResidue(u) then
          close t
          set closedResidue to closedResidue + 1
          if idx > 0 then set item idx of urlCounts to (item idx of urlCounts) - 1
        else if idx > 0 and (item idx of urlCounts) > 1 then
          close t
          set closedDupes to closedDupes + 1
          set item idx of urlCounts to (item idx of urlCounts) - 1
        end if
      end if
    end repeat
  end repeat
  set totalAfter to 0
  repeat with w in windows
    set totalAfter to totalAfter + (count of tabs of w)
  end repeat
  return (totalBefore as text) & "|" & closedResidue & "|" & closedDupes & "|" & totalAfter
end tell
APPLESCRIPT
)
RC=$?

if [ $RC -ne 0 ] || [ -z "$RESULT" ]; then
  echo "$(ts) ERROR rc=$RC result='$RESULT' (likely Automation/TCC consent — see plist notes)" >> "$LOG"
  exit 1
fi

BEFORE=$(echo "$RESULT" | cut -d'|' -f1)
RES=$(echo "$RESULT"  | cut -d'|' -f2)
DUP=$(echo "$RESULT"  | cut -d'|' -f3)
AFTER=$(echo "$RESULT" | cut -d'|' -f4)
echo "$(ts) tabs_before=$BEFORE closed_residue=$RES closed_dupes=$DUP tabs_after=$AFTER" >> "$LOG"

if [ "$AFTER" -gt 80 ] 2>/dev/null; then
  echo "$(ts) WARN tab count still >80 after cleanup — all unique, real tabs; not auto-closing. Review manually." >> "$LOG"
fi
exit 0
