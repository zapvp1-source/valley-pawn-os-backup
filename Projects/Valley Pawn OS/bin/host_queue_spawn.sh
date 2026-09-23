#!/bin/bash
# Detached launcher for the host job queue. Called from launchd-run wrappers.
# Uses a NEW SESSION (setsid) so launchd's end-of-job process-group kill cannot
# terminate a multi-minute host job halfway through (e.g. after quitting Claude
# but before relaunching it). Returns immediately.
OS_BIN="/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin"
# Outbox (2026-09-22): posts anything a Cowork task left in fleet/outbox/ through the ops bot, so a
# scheduled run's Slack send never again dies on "no one was available to approve it." Fast, locked,
# fails closed; runs on the same ~2 min cadence as the job queue.
[ -f "$OS_BIN/outbox_flush.sh" ] && /bin/bash "$OS_BIN/outbox_flush.sh" >/dev/null 2>&1 || true
[ -f "$OS_BIN/host_queue_run.sh" ] || exit 0
/usr/bin/python3 - "$OS_BIN/host_queue_run.sh" <<'PY' >/dev/null 2>&1
import subprocess, sys
subprocess.Popen(["/bin/bash", sys.argv[1]], start_new_session=True,
                 stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
PY
exit 0
