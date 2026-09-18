#!/bin/bash
# launchd wrapper for preston_watch.py (invoked via ~/bin/vp-runner for TCC access to ~/Documents).
# host job queue hook (additive 2026-09-16, detached, never blocks or fails this wrapper)
/bin/bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/host_queue_spawn.sh" >/dev/null 2>&1 || true
exec /usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/preston_watch.py" "$@"
