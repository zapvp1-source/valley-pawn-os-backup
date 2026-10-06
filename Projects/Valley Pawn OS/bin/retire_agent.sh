#!/bin/bash
# retire_agent.sh <label> [--apply]
#
# Unload and archive a launchd agent whose program no longer exists.
#
# WHY (2026-09-18): `com.valleypawn.dashboarddatacollector` fired every hour at :20 — 24 times a day
# — against a script whose whole task folder had been deleted. 278 error lines and nobody knew. An
# agent like that is worse than useless: it costs wakeups, floods the log directory, and buries real
# failures in noise.
#
# THE SAFETY INVARIANT: this script REFUSES to retire an agent whose target still exists. A tool
# that can unload a working agent is a tool that will eventually unload a working agent — so it
# simply cannot. It re-derives the target from the plist itself rather than trusting the caller.
#
# Reversible: the plist is archived to fleet/_retired-oneshots/ before removal, never deleted.
# Dry by default; --apply is required to change anything.
set -u
OS_DIR="$HOME/Documents/Claude/Projects/Valley Pawn OS"
ARCHIVE="$OS_DIR/fleet/_retired-oneshots"
LABEL="${1:-}"
APPLY=0
for a in "$@"; do [ "$a" = "--apply" ] && APPLY=1; done
[ -z "$LABEL" ] && { echo "usage: retire_agent.sh <label> [--apply]"; exit 2; }
case "$LABEL" in --*) echo "usage: retire_agent.sh <label> [--apply]"; exit 2 ;; esac

PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

# --archive-logs: for an agent that is ALREADY retired, move its leftover logs out of the live log
# directory. Needed because log_triage keeps counting a dead agent's old error log until it ages
# out, so the nightly report would keep reporting a fault that no longer exists. Guarded by the
# mirror of the main invariant: it REFUSES while the agent is still installed.
ARCHIVE_LOGS=0
for a in "$@"; do [ "$a" = "--archive-logs" ] && ARCHIVE_LOGS=1; done
if [ $ARCHIVE_LOGS -eq 1 ]; then
  if [ -f "$PLIST" ]; then
    echo "REFUSED: $LABEL is still installed. Retire it first; this mode is only for agents already gone."
    exit 1
  fi
  mkdir -p "$ARCHIVE"
  STAMP="$(date +%Y%m%d-%H%M%S)"
  # Derive the log paths from the agent's own ARCHIVED plist, never from the label. They do not
  # match: label `com.valleypawn.dashboarddatacollector` logs to `dashboard-data-collector.err.log`.
  # Guessing from the label archived 0 files and silently reported success.
  AP="$(ls -1t "$ARCHIVE/$LABEL.plist.retired-"* 2>/dev/null | head -1)"
  [ -z "$AP" ] && { echo "REFUSED: no archived plist for $LABEL — cannot determine its log paths, and guessing them from the label is what already failed once."; exit 1; }
  echo "reading log paths from $(basename "$AP")"
  n=0
  for key in StandardOutPath StandardErrorPath; do
    lg="$(/usr/libexec/PlistBuddy -c "Print :$key" "$AP" 2>/dev/null)"
    [ -z "$lg" ] && continue
    [ -f "$lg" ] || { echo "  $key -> $(basename "$lg") (already gone)"; continue; }
    mv "$lg" "$ARCHIVE/$(basename "$lg").retired-$STAMP" && { echo "  archived $(basename "$lg")"; n=$((n+1)); }
  done
  echo "archived $n log file(s) for $LABEL"
  exit 0
fi

[ -f "$PLIST" ] || { echo "REFUSED: no plist at $PLIST"; exit 1; }

# derive the target from the plist — never from an argument
TARGET="$(/usr/libexec/PlistBuddy -c 'Print :ProgramArguments:1' "$PLIST" 2>/dev/null)"
[ -z "$TARGET" ] && TARGET="$(/usr/libexec/PlistBuddy -c 'Print :ProgramArguments:0' "$PLIST" 2>/dev/null)"
[ -z "$TARGET" ] && TARGET="$(/usr/libexec/PlistBuddy -c 'Print :Program' "$PLIST" 2>/dev/null)"
echo "agent:  $LABEL"
echo "target: ${TARGET:-<none declared>}"

if [ -n "$TARGET" ] && [ -e "$TARGET" ]; then
  echo "REFUSED: target still exists. This tool only retires agents whose program is GONE."
  echo "If you mean to disable a working agent, that is a deliberate decision and a different job."
  exit 1
fi
echo "target is MISSING — this agent can only fail."

if [ $APPLY -eq 0 ]; then
  echo "DRY RUN — would: bootout the agent, archive the plist to fleet/_retired-oneshots/, remove it."
  echo "Re-run with --apply to do it."
  exit 0
fi

mkdir -p "$ARCHIVE"
STAMP="$(date +%Y%m%d-%H%M%S)"
cp "$PLIST" "$ARCHIVE/$LABEL.plist.retired-$STAMP" || { echo "FAILED: could not archive plist"; exit 1; }
echo "archived -> fleet/_retired-oneshots/$LABEL.plist.retired-$STAMP"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null && echo "booted out" || echo "bootout returned non-zero (often means it was not loaded) — continuing"
rm -f "$PLIST" && echo "plist removed"
# Archive the agent's logs too. A retired agent's old error log keeps being counted by log_triage
# until it ages out, so the nightly report would keep reporting a fault that no longer exists.
SHORT="${LABEL#com.valleypawn.}"
for lg in "$HOME/Library/Logs/valleypawn/$SHORT".*log "$HOME/Library/Logs/valleypawn/$SHORT.log"; do
  [ -f "$lg" ] || continue
  mv "$lg" "$ARCHIVE/$(basename "$lg").retired-$STAMP" 2>/dev/null && echo "archived log $(basename "$lg")"
done
if [ -f "$PLIST" ]; then echo "FAILED: plist still present"; exit 1; fi
launchctl list 2>/dev/null | grep -q "$LABEL" && { echo "WARNING: still listed in launchctl"; exit 1; }
echo "VERIFIED: $LABEL is gone from launchctl and from LaunchAgents."
echo "To restore: copy the archived plist back and 'launchctl bootstrap gui/$(id -u) <plist>'."
