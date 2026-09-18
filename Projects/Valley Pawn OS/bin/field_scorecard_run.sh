#!/bin/bash
# launchd wrapper for the Field Scorecard (invoked via ~/bin/vp-runner for TCC access to
# ~/Documents). Logs to ~/Library/Logs/valleypawn/ so launchd itself never opens a file
# inside ~/Documents. Also drains the host job queue first (detached, non-blocking), same
# pattern as registry_guard_run.sh.
OS_BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
/bin/bash "$OS_BIN/host_queue_spawn.sh" >/dev/null 2>&1 || true
# Phase 0.8: keep CHANGELOG_RECENT.md fresh (derived slice of CHANGELOG.md; detached, best-effort)
/usr/bin/python3 "$OS_BIN/changelog_recent.py" >/dev/null 2>&1 &
exec /usr/bin/python3 "$OS_BIN/field_scorecard.py" "$@"
