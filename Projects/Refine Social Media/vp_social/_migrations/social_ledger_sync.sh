#!/bin/bash
# Nightly Publer -> ledger sync for the vp_social engine.
#
# TWO macOS gotchas, both found 2026-09-06 while installing this agent:
#  1. launchd cannot EXECUTE a script that lives under ~/Documents ("Operation not
#     permitted", TCC). The runner therefore lives at ~/vp_social_ledger_sync.sh; this
#     file is the source of record — copy it over after editing.
#  2. A launchd-spawned python cannot IMPORT a package from ~/Documents either (the
#     directory read is denied even though appending to a log file there succeeds), so
#     `cd`+`-m vp_social` fails with "No module named vp_social". The fix is a stub
#     package directory in $HOME whose __init__ execs the real code by absolute path —
#     see vp_social_boot.py, written by install_ledger_sync_agent.sh.
RSM="/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media"
LOG="$RSM/state/logs/ledger_sync.log"
export PYTHONWARNINGS=ignore
cd "$HOME" || exit 1
if /usr/bin/python3 "$HOME/vp_social_boot.py" sync --back 21 --forward 30 >> "$LOG" 2>&1; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') sync ok" >> "$LOG"
else
  echo "$(date '+%Y-%m-%d %H:%M:%S') sync FAILED (see lines above)" >> "$LOG"
fi
